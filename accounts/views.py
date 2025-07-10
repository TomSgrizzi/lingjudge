from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm  # Import your form
from django.contrib.auth import update_session_auth_hash
from .forms import CustomUserChangeForm
from django.contrib.auth import logout

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        return redirect('signup')  # or redirect to a goodbye page
    return render(request, 'accounts/delete_account.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)  # Prevent logout after saving
            return redirect('edit_profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            form.save_m2m()  # Important to save many-to-many native_languages
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

