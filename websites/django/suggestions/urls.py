from django.urls import path
from . import views

urlpatterns = [
    path('', views.suggestions_home, name='suggestions_home'),
    path('create', views.create, name='create'),
    path('<int:pk>', views.SuggestionsDetailView.as_view(), name='suggestions_detail'),
]