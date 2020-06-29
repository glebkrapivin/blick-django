from django.contrib import admin

# Register your models here.

from .models import Movie, Question, Category

admin.site.register(Movie)
admin.site.register(Question)
admin.site.register(Category)