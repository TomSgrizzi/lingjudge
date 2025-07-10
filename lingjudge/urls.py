from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # 👈 Public homepage at '/'
    path('dashboard/', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),  # 👈 for signup
    path('accounts/', include('django.contrib.auth.urls')),  # for login/logout
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('tasks/', include('tasks.urls')),  # ← this line
    path('results/', include('results.urls')),  # <- include this line
    

]
