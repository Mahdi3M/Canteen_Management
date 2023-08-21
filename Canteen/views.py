from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
from .models import User
from functools import wraps
import time
import datetime

# Create your views here.

#<-- ======= Functions ======= -->from functools import wraps

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('Canteen:signin')
        return _wrapped_view
    return decorator



#<-- ======= Pages ======= -->

def signin(request):
    logout(request)
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
            else:
                pass
            if request.user.role == "Admin":
                return redirect("Canteen:home")
            elif request.user.role == "Bar NCO":
                return redirect("Canteen:nco_order")
            elif request.user.role == "Customer":
                return redirect("Canteen:customer_catalog")
        else:
            messages.error(request, "Username or Password is wrong.")
    return render(request, "Canteen/signin.html")

        

def sign_out(request):
    logout(request)
    return redirect('Canteen:signin')



def register(request):
    if request.method == "POST":
        name = request.POST.get('name')
        ba = request.POST.get('ba')
        rank = request.POST.get('rank')
        unit = request.POST.get('unit')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmpassword')
        
        if User.objects.all().filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, "Canteen/register.html")
        elif User.objects.all().filter(email=email).exists():
            messages.error(request, "Email is already taken.")
            return render(request, "Canteen/register.html")        
        elif password != confirm_password:
            print(password, confirm_password)         
            messages.error(request, "Password is not correct.")
            return render(request, "Canteen/register.html")
        else:        
            try:
                myuser = User.objects.create_user(
                    username=username, 
                    email=email, 
                    password=password)
                myuser.is_active = False
                myuser.first_name = rank
                myuser.last_name = name
                myuser.ba = ba
                myuser.unit = unit
                myuser.save() 
                messages.success(request, "You are succesfully registered.")
                return redirect('Canteen:signin')
            except Exception:
                messages.error(request, "Error....")
                return render(request, "Canteen/register.html")
    return render(request, "Canteen/register.html")



@login_required(redirect_field_name='next', login_url="Canteen:signin")
def profile(request):
    return render(request, "Canteen/profile.html")



@login_required(redirect_field_name='next', login_url="Canteen:signin")
def contact(request):
    return render(request, "Canteen/contact.html")



#<-- ======= Customer ======= -->

@login_required(redirect_field_name='next', login_url="Canteen:signin")
def customer_catalog(request):
    return render(request, "Canteen/catalog.html")



@login_required(redirect_field_name='next', login_url="Canteen:signin")
def customer_cart(request):
    return render(request, "Canteen/customer_cart.html")



@login_required(redirect_field_name='next', login_url="Canteen:signin")
def customer_history(request):
    return render(request, "Canteen/customer_history.html")



#<-- ======= Bar NCO ======= -->

@login_required(redirect_field_name='next', login_url="Canteen:signin")
@role_required(allowed_roles=['Bar NCO'])
def nco_order(request):
    return render(request, "Canteen/nco_order.html")



@login_required(redirect_field_name='next', login_url="Canteen:signin")
@role_required(allowed_roles=['Bar NCO'])
def nco_inventory(request):
    return render(request, "Canteen/nco_inventory.html")



#<-- ======= Admin ======= -->

@login_required(redirect_field_name='next', login_url="Canteen:signin")
@role_required(allowed_roles=['Admin'])
def home(request):
    return render(request, "Canteen/index.html")



@login_required(redirect_field_name='next', login_url="Canteen:signin")
@role_required(allowed_roles=['Admin'])
def admin_stats(request):
    return render(request, "Canteen/admin_stats.html")



@login_required(redirect_field_name='next', login_url="Canteen:signin")
@role_required(allowed_roles=['Admin'])
def admin_users(request):
    return render(request, "Canteen/admin_users.html")