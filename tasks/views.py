from django.shortcuts import render, redirect, get_object_or_404
from .forms import TaskForm
from .models import Task
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from .models import LikertItem, ForcedChoiceItem
from .forms import LikertItemForm, ForcedChoiceItemForm
from django.contrib import messages
import csv
import random
import io
from .forms import CSVUploadForm
from django.db.models import Q
from accounts.models import CustomUser  # if not already imported
from django.utils.timezone import now
from .models import LikertResponse
from .models import ForcedChoiceResponse
from datetime import timedelta
from tasks.models import LANGUAGE_CHOICES


@login_required
def start_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, status='published')

    # Store start time in session
    request.session['task_start_time'] = now().isoformat()

    # Store randomized item IDs in session
    if task.task_type == 'Likert':
        item_ids = list(task.likert_items.values_list('id', flat=True))
    else:
        item_ids = list(task.forced_items.values_list('id', flat=True))

    if task.randomized:
        random.shuffle(item_ids)

    request.session[f'task_{task.id}_item_order'] = item_ids

    return render(request, 'tasks/task_instructions.html', {
        'task': task
    })


@login_required
def task_basic_info(request, task_id=None):
    if task_id:
        task = get_object_or_404(Task, id=task_id, user=request.user, status='draft')
    else:
        task = None

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.user = request.user
            # Set the status before save
            new_task.status = new_task.status or 'draft'
            new_task.num_items = form.cleaned_data.get('num_items')  # ← explicitly assign
            print("DEBUG: form.cleaned_data['num_items'] =", form.cleaned_data.get('num_items'))
            print("DEBUG: new_task.num_items before save =", new_task.num_items)
            new_task.save()

            print("DEBUG: new_task.num_items after save =", new_task.num_items)

            if new_task.task_type == 'Likert':
                return redirect('tasks:add_likert_items', task_id=new_task.id)
            else:
                return redirect('tasks:add_fc_items', task_id=new_task.id)
        else:
            print("DEBUG: form errors:", form.errors)
    else:
        form = TaskForm(instance=task)

    return render(request, 'tasks/task_basic_info.html', {'form': form, 'task': task})



@login_required
def task_feed(request):
    user = request.user

    # Get user's native language codes (e.g., ['en', 'it'])
    user_languages = set(user.native_languages.values_list('name', flat=True))
    name_to_code = {name: code for code, name in LANGUAGE_CHOICES}
    user_language_codes = [name_to_code[name] for name in user_languages if name in name_to_code]

    sort_by = request.GET.get('sort', 'created_at')

    # STEP 1: Find task IDs where the user has submitted any response
    likert_done_task_ids = LikertResponse.objects.filter(user=user).values_list('task_id', flat=True)
    fc_done_task_ids = ForcedChoiceResponse.objects.filter(user=user).values_list('task_id', flat=True)
    excluded_task_ids = set(likert_done_task_ids).union(fc_done_task_ids)

    # STEP 2: Build the query
    tasks = Task.objects.filter(
        status='published',
        task_language__in=user_language_codes
    ).exclude(user=user).exclude(id__in=excluded_task_ids)

    # Sorting
    if sort_by == 'num_items':
        tasks = tasks.order_by('num_items')
    else:
        tasks = tasks.order_by('created_at')

    return render(request, 'tasks/task_feed.html', {
        'tasks': tasks,
        'sort_by': sort_by,
    })


@login_required
def add_likert_items(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user, task_type='Likert')
    LikertFormSet = modelformset_factory(LikertItem, form=LikertItemForm, extra=task.num_items)
    csv_form = CSVUploadForm()
    print(f"DEBUG: Loaded Task {task.id} with num_items = {task.num_items}")


    if request.method == 'POST':
        if 'upload_csv' in request.POST:
            csv_form = CSVUploadForm(request.POST, request.FILES)
            if csv_form.is_valid():
                csv_file = csv_form.cleaned_data['csv_file']
                decoded_file = csv_file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))

                required_fields = {'id', 'sentence', 'context'}
                if not required_fields.issubset(reader.fieldnames):
                    messages.error(request, 'CSV file must contain "id", "sentence" and "context" columns.')
                    return redirect('tasks:add_likert_items', task_id=task.id)

                row_count = 0
                for row in reader:
                    LikertItem.objects.create(
                        item_id=row.get('id').strip(),
                        task=task,
                        sentence=row.get('sentence', '').strip(),
                        context=row.get('context', '').strip()
                    )


                task.num_items = row_count
                task.status = 'published'
                task.save()

                messages.success(request, 'CSV uploaded successfully!')
                messages.success(request, f'Task successfully posted as {task.status}.')
                return redirect('tasks:task_preview', task_id=task.id)


        else:
            formset = LikertFormSet(request.POST, queryset=LikertItem.objects.none())
            if formset.is_valid():
                valid_forms = [form for form in formset if form.cleaned_data]

                all_filled = all(form.cleaned_data.get('sentence') for form in valid_forms)

                if not all_filled or len(valid_forms) != task.num_items:
                    messages.error(request, f'Please fill all {task.num_items} sentence fields before submitting.')
                    return render(request, 'tasks/add_likert_items.html', {
                        'formset': formset,
                        'csv_form': csv_form,
                        'task': task
                    })

                for form in valid_forms:
                    item = form.save(commit=False)
                    item.task = task
                    item.save()

                #task.num_items = task.likert_items.count()
                task.status = 'published'
                task.save()
                messages.success(request, f'Task successfully posted as {task.status}.')
                return redirect('tasks:task_preview', task_id=task.id)


    else:
        formset = LikertFormSet(queryset=LikertItem.objects.none())

    return render(request, 'tasks/add_likert_items.html', {
        'formset': formset,
        'csv_form': csv_form,
        'task': task
    })

@login_required
def add_fc_items(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user, task_type='ForcedChoice')
    FCFormSet = modelformset_factory(ForcedChoiceItem, form=ForcedChoiceItemForm, extra=task.num_items)
    csv_form = CSVUploadForm()
    print(f"DEBUG: Loaded Task {task.id} with num_items = {task.num_items}")


    if request.method == 'POST':
        if request.POST.get('upload_csv') == '1':
            csv_form = CSVUploadForm(request.POST, request.FILES)
            if csv_form.is_valid():
                csv_file = csv_form.cleaned_data['csv_file']
                decoded_file = csv_file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))
                required_fields = {'id', 'sentence_a', 'sentence_b', 'context'}
                if not required_fields.issubset(reader.fieldnames):
                    messages.error(request, 'CSV must contain "id", "sentence_a", "sentence_b", and "context" columns.')
                    return redirect('tasks:add_fc_items', task_id=task.id)
                row_count = 0
                for row in reader:
                    ForcedChoiceItem.objects.create(
                        item_id=row.get('id').strip(),
                        task=task,
                        sentence_a=row.get('sentence_a', '').strip(),
                        sentence_b=row.get('sentence_b', '').strip(),
                        context=row.get('context', '').strip()
                    )

                    row_count += 1

                task.num_items = row_count
                task.status = 'published'
                task.save()

                messages.success(request, 'CSV uploaded successfully!')
                messages.success(request, f'Task successfully posted as {task.status}.')
                return redirect('tasks:task_preview', task_id=task.id)


        else:
            formset = FCFormSet(request.POST, queryset=ForcedChoiceItem.objects.none())
            if formset.is_valid():
                valid_forms = [form for form in formset if form.cleaned_data]

                all_filled = all(
                    form.cleaned_data.get('sentence_a') and form.cleaned_data.get('sentence_b')
                    for form in valid_forms
                )

                if not all_filled or len(valid_forms) != task.num_items:
                    messages.error(request, f'Please fill all {task.num_items} sentence pairs before submitting.')
                    return render(request, 'tasks/add_fc_items.html', {
                        'formset': formset,
                        'csv_form': csv_form,
                        'task': task
                    })

                for form in valid_forms:
                    item = form.save(commit=False)
                    item.task = task
                    item.save()

                #task.num_items = task.likert_items.count()
                task.status = 'published'
                task.save()
                messages.success(request, f'Task successfully posted as {task.status}.')
                return redirect('tasks:task_preview', task_id=task.id)


    else:
        formset = FCFormSet(queryset=ForcedChoiceItem.objects.none())

    return render(request, 'tasks/add_fc_items.html', {
        'formset': formset,
        'csv_form': csv_form,
        'task': task
    })


@login_required
def task_preview(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if task.task_type == 'Likert':
        items = LikertItem.objects.filter(task=task)
    else:
        items = ForcedChoiceItem.objects.filter(task=task)

    return render(request, 'tasks/task_preview.html', {
        'task': task,
        'items': items,
    })



@login_required
def do_likert_task(request, task_id, item_index):
    task = get_object_or_404(Task, id=task_id, task_type='Likert', status='published')
    item_ids = request.session.get(f'task_{task.id}_item_order')
    if item_ids is None:
        return redirect('tasks:start_task', task_id=task.id)

    if item_index >= len(item_ids):
        return redirect('tasks:end_task', task_id=task.id)

    item_id = item_ids[item_index]
    item = get_object_or_404(LikertItem, id=item_id)

    # Navigation
    if request.method == 'POST':
        response = request.POST.get('response')
        if response:
            LikertResponse.objects.update_or_create(
                user=request.user,
                task=task,
                item=item,
                defaults={
                    'response': int(response),
                    'start_time': request.session.get('task_start_time'),
                    'end_time': now()
                }
            )
            # Next or previous
            if 'next' in request.POST:
                return redirect('tasks:do_likert_task', task_id=task.id, item_index=item_index + 1)
            elif 'previous' in request.POST and item_index > 0:
                return redirect('tasks:do_likert_task', task_id=task.id, item_index=item_index - 1)

    # Progress bar calculation
    progress = int((item_index + 1) / len(item_ids) * 100)


    return render(request, 'tasks/likert_task_item.html', {
        'task': task,
        'item': item,
        'item_index': item_index,
        'total_items': len(item_ids),
        'progress': progress,
        'range': range(1, task.num_scale_points + 1),
    })


@login_required
def end_task(request, task_id):
    request.session.pop(f'task_{task_id}_item_order', None)
    return render(request, 'tasks/end_task.html')



@login_required
def do_fc_task(request, task_id, item_index):
    task = get_object_or_404(Task, id=task_id, task_type='ForcedChoice', status='published')
    item_ids = request.session.get(f'task_{task.id}_item_order')
    if item_ids is None:
        return redirect('tasks:start_task', task_id=task.id)

    if item_index >= len(item_ids):
        return redirect('tasks:end_task', task_id=task.id)

    item_id = item_ids[item_index]
    item = get_object_or_404(ForcedChoiceItem, id=item_id)


    if request.method == 'POST':
        selection = request.POST.get('selection')
        if selection in ['A', 'B']:
            ForcedChoiceResponse.objects.update_or_create(
                user=request.user,
                task=task,
                item=item,
                defaults={
                    'selection': selection,
                    'start_time': request.session.get('task_start_time'),
                    'end_time': now()
                }
            )
            if 'next' in request.POST:
                return redirect('tasks:do_fc_task', task_id=task.id, item_index=item_index + 1)
            elif 'previous' in request.POST and item_index > 0:
                return redirect('tasks:do_fc_task', task_id=task.id, item_index=item_index - 1)

    progress = int((item_index + 1) / len(item_ids) * 100)

    return render(request, 'tasks/fc_task_item.html', {
        'task': task,
        'item': item,
        'item_index': item_index,
        'total_items': len(item_ids),
        'progress': progress
    })