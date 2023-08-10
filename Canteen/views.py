from django.shortcuts import render

# Create your views here.

#<-- ======= Pages ======= -->

def home(request):
    return render(request, "Canteen/index.html")

def login(request):
    return render(request, "Canteen/login.html")

def register(request):
    return render(request, "Canteen/register.html")

def profile(request):
    return render(request, "Canteen/profile.html")

def contact(request):
    return render(request, "Canteen/contact.html")

#<-- ======= Customer ======= -->

def customer_catalog(request):
    return render(request, "Canteen/catalog.html")

def customer_order(request):
    return render(request, "Canteen/customer_order.html")

def customer_history(request):
    return render(request, "Canteen/customer_history.html")

#<-- ======= Bar NCO ======= -->



#<-- ======= Admin ======= -->