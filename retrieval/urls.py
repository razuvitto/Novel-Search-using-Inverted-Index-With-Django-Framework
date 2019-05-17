from django.urls import path
from retrieval import views
from . import views

app_name = 'retrieval'
urlpatterns = [
    path('', views.import_csv),
    path('novel/<int:id>', views.novel_page, name='novel'),
    path('result/', views.result),
    # path('novel/<int:pk>', views.book_detail_view.as_view(), name='book-detail'),
]