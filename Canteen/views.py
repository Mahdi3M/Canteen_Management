from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from .models import *
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
        image_file = request.FILES.get('image')         
        
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
                if image_file:
                    myuser.image = image_file
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
    context = {}
    
    category_names = Category.objects.values_list('name', flat=True)
    subcategory_names = Subcategory.objects.values_list('name', flat=True)
    context["keywords"] = list(category_names) + list(subcategory_names)
    
    if request.method == "POST":
        query = request.POST.get('query')
        if query in category_names:
            context["products"] = Product.objects.filter(category__name = query).order_by('category__name', 'subcategory__name', 'name')
        elif query in subcategory_names:
            context["products"] = Product.objects.filter(subcategory__name = query).order_by('category__name', 'subcategory__name', 'name')
        else:
            context["products"] = Product.objects.all().order_by('category__name', 'subcategory__name', 'name')
    else:        
        context["products"] = Product.objects.all().order_by('category__name', 'subcategory__name', 'name')
    
    return render(request, "Canteen/catalog.html", context)



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
    if request.method == "POST":
        image_file = request.FILES.get('image')
        name = request.POST.get('productName')
        category = request.POST.get('category')
        new_category = request.POST.get('new-category')
        subcategory = request.POST.get('subCategory')
        new_subcategory = request.POST.get('new-sub-category')
        buying_price = request.POST.get('buyingPrice')
        selling_price = request.POST.get('sellingPrice')
        amount = request.POST.get('amount')           
        
        new_Product = Product()        
        new_Product.name = name
        new_Product.image = image_file
        new_Product.buying_price = buying_price
        new_Product.selling_price = selling_price
        new_Product.stock_quantity = amount
        
        if category:
            new_Category = Category.objects.get(name = category)
            new_Product.category = new_Category
        else:            
            new_Category = Category(name = new_category)
            new_Category.save()
            new_Product.category = new_Category
        
        if subcategory:
            new_Product.subcategory = Subcategory.objects.get(name = subcategory)
        else:
            new_Subcategory = Subcategory(name = new_subcategory, category = new_Category)
            new_Subcategory.save()
            new_Product.subcategory = new_Subcategory
        new_Product.save()    
        
    context = {}
    
    context["categories"] = Category.objects.all()
    context["subcategories"] = Subcategory.objects.all()
    
    return render(request, "Canteen/nco_inventory.html", context)



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
    
    if request.method == "POST":
        if request.POST.get("user_id_add"):
            id = request.POST.get("user_id_add")
            role = request.POST.get("userRole")
            new_user = User.objects.get(id = id)
            new_user.is_active = True
            new_user.role = role
            new_user.save()
            
        if request.POST.get("user_id_remove"):
            id = request.POST.get("user_id_remove")
            delete_user = User.objects.get(id = id)
            delete_user.delete()
    
    context = {}
    
    context["pending_users"] = User.objects.filter(is_active = False)
    context["all_users"] = User.objects.filter(is_active = True)
    
    return render(request, "Canteen/admin_users.html", context)