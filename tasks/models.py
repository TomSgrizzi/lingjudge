from django.db import models
from accounts.models import CustomUser

LANGUAGE_CHOICES = [
    ('en', 'English'),
    ('zh', 'Mandarin Chinese'),
    ('es', 'Spanish'),
    ('hi', 'Hindi'),
    ('ar', 'Arabic'),
    ('bn', 'Bengali'),
    ('pt', 'Portuguese'),
    ('ru', 'Russian'),
    ('ja', 'Japanese'),
    ('pa', 'Punjabi'),
    ('de', 'German'),
    ('jv', 'Javanese'),
    ('wuu', 'Wu Chinese'),
    ('ms', 'Malay/Indonesian'),
    ('te', 'Telugu'),
    ('vi', 'Vietnamese'),
    ('ko', 'Korean'),
    ('fr', 'French'),
    ('mr', 'Marathi'),
    ('ta', 'Tamil'),
    ('ur', 'Urdu'),
    ('tr', 'Turkish'),
    ('it', 'Italian'),
    ('yue', 'Yue Chinese (Cantonese)'),
    ('th', 'Thai'),
    ('gu', 'Gujarati'),
    ('jcn', 'Jin Chinese'),
    ('fa', 'Persian'),
    ('pl', 'Polish'),
    ('ps', 'Pashto'),
    ('kn', 'Kannada'),
    ('hsn', 'Xiang Chinese'),
    ('ml', 'Malayalam'),
    ('su', 'Sundanese'),
    ('ha', 'Hausa'),
    ('or', 'Odia (Oriya)'),
    ('my', 'Burmese'),
    ('hak', 'Hakka'),
    ('uk', 'Ukrainian'),
    ('bho', 'Bhojpuri'),
    ('tl', 'Tagalog (Filipino)'),
    ('yo', 'Yoruba'),
    ('sd', 'Sindhi'),
    ('arz', 'Arabic (Egyptian Spoken)'),
    ('nl', 'Dutch'),
    ('apc', 'Sa’idi Arabic'),
    ('ku', 'Northern Kurdish'),
    ('ro', 'Romanian'),
    ('nl', 'Dutch'),  # repeated in your list
    ('el', 'Greek'),
    ('cs', 'Czech'),
    ('sv', 'Swedish'),
    ('hu', 'Hungarian'),
    ('be', 'Belarusian'),
    ('sr', 'Serbian'),
    ('az', 'Azerbaijani'),
    ('fi', 'Finnish'),
    ('sk', 'Slovak'),
    ('bg', 'Bulgarian'),
    ('no', 'Norwegian'),
    ('da', 'Danish'),
    ('he', 'Hebrew'),
    ('lt', 'Lithuanian'),
    ('lv', 'Latvian'),
    ('hr', 'Croatian'),
    ('mn', 'Mongolian'),
    ('sl', 'Slovenian'),
    ('et', 'Estonian'),
    ('sq', 'Albanian'),
    ('mk', 'Macedonian'),
    ('lb', 'Luxembourgish'),
    ('ga', 'Irish'),
    ('cy', 'Welsh'),
    ('ca', 'Catalan'),
    ('eu', 'Basque'),
    ('gl', 'Galician'),
    ('af', 'Afrikaans'),
]


class Task(models.Model):
    TASK_TYPES = (
        ('Likert', 'Likert'),
        ('ForcedChoice', 'Forced Choice'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    title = models.CharField(max_length=255)
    instructions = models.TextField()
    num_scale_points = models.IntegerField(null=True, blank=True)
    left_label = models.CharField(max_length=100, blank=True)
    right_label = models.CharField(max_length=100, blank=True)
    randomized = models.BooleanField(default=False)
    task_language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    status = models.CharField(max_length=20, choices=[('draft', 'Draft')])
    created_at = models.DateTimeField(auto_now_add=True)
    num_items = models.IntegerField(default=1)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.left_label:
            self.left_label = 'ungrammatical'
        if not self.right_label:
            self.right_label = 'grammatical'

        # Save once to ensure the object has an ID
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Don't delete on initial save (when there are no items yet)
        if is_new:
            return

        if self.status == 'published':
            actual_num_items = 0
            if self.task_type == 'Likert':
                actual_num_items = self.likert_items.count()
            elif self.task_type == 'ForcedChoice':
                actual_num_items = self.forced_items.count()

            if actual_num_items == 0:
                print(f"Deleting task '{self.title}' (id={self.id}) because it has no items.")
                self.delete()






class LikertItem(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='likert_items')
    item_id = models.CharField(max_length=50, blank=True)  # ← NEW: user-defined ID like '1', 'itemA', etc.
    sentence = models.TextField()
    context = models.TextField(blank=True)

class ForcedChoiceItem(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='forced_items')
    item_id = models.CharField(max_length=50, blank=True)  # ← NEW
    sentence_a = models.TextField()
    sentence_b = models.TextField()
    context = models.TextField(blank=True)

class LikertResponse(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    item = models.ForeignKey(LikertItem, on_delete=models.CASCADE)
    response = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

class ForcedChoiceResponse(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    item = models.ForeignKey(ForcedChoiceItem, on_delete=models.CASCADE)
    selection = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B')])
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
