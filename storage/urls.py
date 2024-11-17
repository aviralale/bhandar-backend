from django.urls import path
from . import views

urlpatterns = [
    path('share//', views.PublicShareView.as_view(), name='public-share'),
    path('share//download/', views.PublicDownloadView.as_view(), name='public-download'),
]