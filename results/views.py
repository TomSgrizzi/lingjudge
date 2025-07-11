from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from tasks.models import Task, LikertItem, ForcedChoiceItem
from django.contrib import messages
import csv
from django.http import HttpResponse
from django.utils import timezone
from collections import defaultdict
from tasks.models import LikertResponse, ForcedChoiceResponse
from accounts.models import CustomUser

@login_required
def my_results_view(request):
    user = request.user
    my_tasks = Task.objects.filter(user=user)  # Only tasks created by this user

    return render(request, 'results/my_results.html', {  # note my_results.html here
        'drafts': my_tasks.filter(status='draft'),
        'published': my_tasks.filter(status='published'),
    })

@login_required
def my_results(request):
    user = request.user
    my_tasks = Task.objects.filter(user=user)
    return render(request, 'results/my_results.html', {
        'drafts': my_tasks.filter(status='draft'),
        'published': my_tasks.filter(status='published'),
    })


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)

    if task.task_type == 'Likert':
        items = LikertItem.objects.filter(task=task)
        user_ids = LikertResponse.objects.filter(task=task).values_list('user_id', flat=True).distinct()
    else:
        items = ForcedChoiceItem.objects.filter(task=task)
        user_ids = ForcedChoiceResponse.objects.filter(task=task).values_list('user_id', flat=True).distinct()

    unique_user_count = len(user_ids)

    return render(request, 'results/task_detail.html', {
        'task': task,
        'items': items,
        'unique_user_count': unique_user_count,
    })


@login_required
def task_edit(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user, status='draft')

    if request.method == 'POST':
        if 'publish' in request.POST:
            task.status = 'published'
            task.save()
            messages.success(request, 'Task created successfully (not published yet).')
            return redirect('my_results')
        elif 'delete' in request.POST:
            task.delete()
            messages.success(request, 'Successfully deleted task.')
            return redirect('my_results')

    return render(request, 'results/task_edit.html', {'task': task})

@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted.')
        return redirect('my_results')
    return render(request, 'results/task_delete_confirm.html', {'task': task})


@login_required
def download_task_results(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=task_{task_id}_results.csv'

    writer = csv.writer(response)
    writer.writerow([
        'task id', 'task type', 'scale points', 'left label', 'right label', 'randomized', 'item id',
        'item 1', 'item 2', 'context', 'user id', 'native languages',
        'date of birth', 'task total duration (s)', 'selection', 'completion date'
    ])

    if task.task_type == 'Likert':
        responses = LikertResponse.objects.filter(task=task).select_related('item', 'user')

        # Group responses by user
        user_responses = defaultdict(list)
        for r in responses:
            user_responses[r.user_id].append(r)

        for user_id, user_group in user_responses.items():
            total_duration = round(
                (max(r.end_time for r in user_group) - min(r.start_time for r in user_group)).total_seconds(),
                2
            )
            completion_date = max(r.end_time for r in user_group).date()


            for r in user_group:
                user = r.user
                native_langs = ', '.join(user.native_languages.values_list('name', flat=True))
                writer.writerow([
                    task.id, 'Likert', task.num_scale_points, task.left_label, task.right_label,
                    task.randomized,
                    r.item.item_id or r.item.id, r.item.sentence, '', r.item.context or '', user.id,
                    native_langs, user.date_of_birth,
                    total_duration, r.response, completion_date
                ])


    else:  # ForcedChoice
        responses = ForcedChoiceResponse.objects.filter(task=task).select_related('item', 'user')

        user_responses = defaultdict(list)
        for r in responses:
            user_responses[r.user_id].append(r)

        for user_id, user_group in user_responses.items():
            total_duration = round(
                (max(r.end_time for r in user_group) - min(r.start_time for r in user_group)).total_seconds(),
                2
            )

            completion_date = max(r.end_time for r in user_group).date()

            for r in user_group:
                user = r.user
                native_langs = ', '.join(user.native_languages.values_list('name', flat=True))
                writer.writerow([
                    task.id, 'ForcedChoice', '', '', '',
                    task.randomized,
                    r.item.item_id or r.item.id, r.item.sentence_a, r.item.sentence_b, r.item.context or '', user.id,
                    native_langs, user.date_of_birth,
                    total_duration, r.selection, completion_date
                ])


    return response