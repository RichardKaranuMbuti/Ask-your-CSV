from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    path('company/create/', views.create_company), # working
    #path('upload-file/', views.upload_file, name='upload-file'),
    path('upload-csv-file/', views.upload_csv_file, name='upload-csv-file'), #working
    path('get-csv-files/<int:company_id>/', views.get_csv_files, name='get-csv-files'), # working
    path('get-csv-files-list/<int:company_id>/', views.get_csv_files_list, name='get-csv-files-list'), #working
    path('chat-with-csv/<int:company_id>/', views.chat_with_csv, name='chat-with-csv'), # Working
    path('update-api-key/', views.update_api_key, name='update-api-key'),# Working
    path('delete-api-key/', views.delete_api_key, name='delete-api-key'),
    path('delete-company/<int:company_id>/', views.delete_company, name='delete-company'),
    path('delete-csv-file/<int:company_id>/', views.delete_csv_file, name='delete-csv-file'),
]
    
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
