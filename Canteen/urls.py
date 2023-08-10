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
    path('customer_order/', views.customer_order, name="customer_order"),
    path('customer_history/', views.customer_history, name="customer_history"),
]