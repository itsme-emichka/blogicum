from django.urls import path

from pages import views
from pages.apps import PagesConfig

app_name = PagesConfig.name

urlpatterns = [
    path('about/', views.About.as_view(), name='about'),
    path('rules/', views.Rules.as_view(), name='rules'),
]
