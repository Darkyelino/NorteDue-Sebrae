from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('fornecedores/', views.suppliers_list, name='suppliers_list'),
    path('monitorar/', views.toggle_monitor, name='toggle_monitor'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]