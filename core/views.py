from django.shortcuts import render, redirect

def public_home(request):
    if request.user.is_authenticated:
        return redirect('dashboard_home')  # or the URL path name for your dashboard
    return render(request, 'core/home.html')