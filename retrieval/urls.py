# Coded with <3 Razuvitto
# location : retrieval/urls.py
# April 2018

from django.urls import path
from retrieval import views
from . import views

app_name = 'retrieval'
urlpatterns = [
    path('', views.import_csv),
    path('novel/<int:id>', views.novel_page, name='novel'),
    path('result/', views.result),
]