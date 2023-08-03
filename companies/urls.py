from django.urls import path,re_path
from . import views
from django.conf import settings

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    #path('save/user/', views.save_user_id, name='save-user-id'),
    path('login/', views.login_view, name='login'),
    path('company/create/', views.create_company), # working
    path('user/companies/', views.get_user_companies, name='get_user_companies'),
    #path('upload-file/', views.upload_file, name='upload-file'),
    path('upload-csv-file/', views.upload_csv_file, name='upload-csv-file'), #working
    path('get-csv-files/', views.get_csv_files, name='get-csv-files'), # working-paths for AI agent
    path('get-csv-names/', views.get_csv_names , name='get-csv-names'), #working
    path('chat/', views.chat_with_csv , name='chat-csv'), #working
    path('delete-files/', views.delete_csv_files , name='delete-csv'),
    path('update-api-key/', views.update_api_key, name='update-api-key'),# Working
    path('delete-api-key/', views.delete_api_key, name='delete-api-key'),
    path('inspect-csv-files/', views.inspect_user_csv, name='inspect-csv-files'),
    path('create-room/', views.create_room, name='create-room'),
    path('room_list/', views.room_list, name='room_list'),
    path('room_messages/', views.room_messages, name='room_messages'),
]
    
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
