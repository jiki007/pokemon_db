from django.urls import path
from . import views

app_name = 'cards'

urlpatterns = [
    path('account/signup/', views.signup, name='signup'),
    path('account/', views.account, name='account'),
    path('', views.home, name='home'),
    path('cards/', views.card_list, name='card_list'),
    path('cards/new/',views.card_create, name='card_create'),
    path('cards/<str:card_id>/edit/', views.card_edit, name='card_edit'),
    path('cards/<str:card_id>/delete/', views.card_delete, name='card_delete'),
    path('cards/<str:card_id>/', views.card_detail, name='card_detail'),
    path('sets/', views.set_list, name='set_list'),
    path('sets/compare/', views.set_compare, name='set_compare'),
    path('sets/<str:set_id>/', views.set_detail, name='set_detail'),
    path('search/', views.search, name='search'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('sql-showcase/', views.sql_showcase, name='sql_showcase'),
    path('insights/', views.insights, name='insights'),
    
]
