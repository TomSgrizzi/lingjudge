from django import forms
from .models import Task
from django.forms import ModelForm, modelformset_factory
from .models import LikertItem, ForcedChoiceItem

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'task_type',
            'title',
            'instructions',
            'num_scale_points',
            'left_label',
            'right_label',
            'randomized',
            'task_language',
            'status',
            'num_items',
        ]
        widgets = {
            'task_type': forms.Select(choices=Task.TASK_TYPES),
            'status': forms.Select(choices=[('draft', 'Draft')]),
            'instructions': forms.Textarea(attrs={'rows': 4}),
        }

# Keep these for backward compatibility if needed, but they should use the same fields
class LikertItemForm(ModelForm):
    class Meta:
        model = LikertItem
        fields = ['sentence', 'context']
        widgets = {
            'sentence': forms.TextInput(attrs={'class': 'block w-full rounded border border-gray-300 px-3 py-1 text-sm'}),
            'context': forms.TextInput(attrs={'class': 'block w-full rounded border border-gray-300 px-3 py-1 text-sm'}),
        }


class ForcedChoiceItemForm(ModelForm):
    class Meta:
        model = ForcedChoiceItem
        fields = ['sentence_a', 'sentence_b', 'context']
        widgets = {
            'sentence_a': forms.TextInput(attrs={'class': 'block w-full rounded border border-gray-300 px-3 py-1 text-sm'}),
            'sentence_b': forms.TextInput(attrs={'class': 'block w-full rounded border border-gray-300 px-3 py-1 text-sm'}),
            'context': forms.TextInput(attrs={'class': 'block w-full rounded border border-gray-300 px-3 py-1 text-sm'}),
        }

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='Upload a CSV file')
