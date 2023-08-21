from django.urls import path
from Canteen import views

app_name = "Canteen"

urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.login, name="login"),
    path('register/', views.register, name="register"),
    path('profile/', views.profile, name="profile"),
    path('contact/', views.contact, name="contact"),

    path('customer_catalog/', views.customer_catalog, name="customer_catalog"),
    path('customer_cart/', views.customer_cart, name="customer_cart"),
    path('customer_history/', views.customer_history, name="customer_history"),
    
    path('nco_order/', views.nco_order, name="nco_order"),
    path('nco_inventory/', views.nco_inventory, name="nco_inventory"),
    
    path('admin_stats/', views.admin_stats, name="admin_stats"),
    path('admin_users/', views.admin_users, name="admin_users"),
]