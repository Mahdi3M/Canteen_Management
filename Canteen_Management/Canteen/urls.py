from django.urls import path
from Canteen import views

app_name = "Canteen"

urlpatterns = [
    path('', views.signin, name="signin"),
    path('signout', views.sign_out, name="signout"),
    path('register/', views.register, name="register"),
    path('profile/', views.profile, name="profile"),

    path('customer_catalog/', views.customer_catalog, name="customer_catalog"),
    path('customer_checkout/', views.customer_checkout, name="customer_checkout"),
    path('customer_history/', views.customer_history, name="customer_history"),
    
    path('nco_order/', views.nco_order, name="nco_order"),
    path('nco_inventory/', views.nco_inventory, name="nco_inventory"),
    path('nco_bills/', views.nco_bills, name="nco_bills"),
    
    path('home/', views.home, name="home"),
    path('admin_users/', views.admin_users, name="admin_users"),
    path('admin_stock/', views.admin_stock, name="admin_stock"),
    
    path('send_otp_email/', views.send_otp_email, name="send_otp_email"),
    path('get_barcode_data/', views.get_barcode_data, name="get_barcode_data"),
]