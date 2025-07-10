# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from tasks.models import Task
from results.models import Submission

@login_required
def dashboard_home(request):
    user = request.user
    created_tasks = Task.objects.filter(user=user)
    submissions = Submission.objects.filter(user=user)

    return render(request, "dashboard/dashboard.html", {
        "user": user,
        "created_tasks": created_tasks,
        "submissions": submissions
    })
