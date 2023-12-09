from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    # path('create_consumer/', views.create_consumer, name='create_consumer'),
    path('create_authorize_connection/', views.create_authorize_connection, name='create_authorize_connection'),
    # path('get_all_invoices/', views.get_all_invoices, name='get_all_invoices'),
    # path('invoices_store_in_session/', views.invoices_store_in_session, name='invoices_store_in_session'),
    path('invoices_store_in_database/', views.invoices_store_in_database, name='invoices_store_in_database'),
    # path('chat/', views.chat_with_json , name='chat-csv'), #working
    path('chat_about_invoices/', views.chat_about_invoices , name='chat_about_invoices'),
    path('get_room_messages/', views.get_room_messages, name='get_room_messages'),

]
