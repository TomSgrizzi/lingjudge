from django.db import models
from accounts.models import CustomUser
from tasks.models import Task, LikertItem, ForcedChoiceItem

class Submission(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

