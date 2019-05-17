from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from retrieval import views

urlpatterns = [
    # path('', views.index),
    path('admin/', admin.site.urls),
    path('',include('retrieval.urls')),
]
