from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload-file'),
    path('files/', views.file_list, name='file-list'),
    path('download/<int:file_id>/', views.download_file, name='download-file'),
    path('delete/<int:file_id>/', views.delete_file, name='delete-file'),
    path('logs/', views.access_logs, name='access-logs'),
] 