from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path("", csrf_exempt(views.Bot.as_view())),
    path("movies", views.MovieImages.as_view()),
]
