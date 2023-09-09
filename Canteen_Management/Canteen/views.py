from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from .models import *
from functools import wraps
import json
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
    product_names = Product.objects.values_list('name', flat=True)
    context["keywords"] = list(category_names) + list(subcategory_names) + list(product_names)
    
    if request.method == "POST":
        query = request.POST.get('query')
        if query in category_names:
            context["products"] = Product.objects.filter(category__name = query).exclude(stock_quantity = 0).order_by('category__name', 'subcategory__name', 'name')
        elif query in subcategory_names:
            context["products"] = Product.objects.filter(subcategory__name = query).exclude(stock_quantity = 0).order_by('category__name', 'subcategory__name', 'name')
        elif query in product_names:
            context["products"] = Product.objects.filter(name = query).exclude(stock_quantity = 0).order_by('category__name', 'subcategory__name', 'name')
        else:
            context["products"] = Product.objects.exclude(stock_quantity = 0).order_by('category__name', 'subcategory__name', 'name')
    else:        
        context["products"] = Product.objects.exclude(stock_quantity = 0).order_by('category__name', 'subcategory__name', 'name')
    
    return render(request, "Canteen/catalog.html", context)



@login_required(redirect_field_name='next', login_url="Canteen:signin")
def customer_checkout(request):
    context = {}
    context['thank'] = False
    if request.method == "POST":
        cartJSON = request.POST.get("cartJSON")
        cart = json.loads(cartJSON)
        total = request.POST.get("cartTotal")
        
        with transaction.atomic():
            new_Order = Order()
            new_Order.name = request.user.name
            new_Order.ba = request.user.ba
            new_Order.total = total
            new_Order.save()
            
            for item in cart:
                new_Order_List = OrderItem()
                new_Order_List.order = new_Order
                new_Order_List.product_id = cart[item]["id"]
                new_Order_List.name = cart[item]["name"]
                new_Order_List.price = cart[item]["price"]
                new_Order_List.quantity = cart[item]["quantity"]
                new_Order_List.total = cart[item]["quantity"] * cart[item]["price"]
                new_Order_List.save()
                
                product = Product.objects.get(id = cart[item]["id"])
                product.stock_quantity -= cart[item]["quantity"]
                product.save()
            
        context['thank'] = True
    return render(request, "Canteen/customer_checkout.html", context)



@login_required(redirect_field_name='next', login_url="Canteen:signin")
@role_required(allowed_roles=['Admin', 'Customer'])
def customer_history(request):
    return render(request, "Canteen/customer_history.html")



#<-- ======= Bar NCO ======= -->

@login_required(redirect_field_name='next', login_url="Canteen:signin")
@role_required(allowed_roles=['Bar NCO'])
def nco_order(request):
    context = {}
    context['orders_pending'] = OrderItem.objects.filter(order__status = 'Pending').order_by('order__id')
    context['orders_complete'] = OrderItem.objects.filter(order__status = 'Complete').order_by('-order__timestamp')
    
    if request.method == "POST":
        
        if request.POST.get('complete-order'):
            id = request.POST.get('complete-order')
            order = Order.objects.get(id = id)
            order.status = 'Complete'
            order.save()
            
        if request.POST.get('remove-order'):
            id = request.POST.get('remove-order')
            order = Order.objects.get(id = id)
            products = OrderItem.objects.filter(order = order)
            with transaction.atomic():
                for p in products:
                    product = Product.objects.get(id = p.product_id)
                    product.stock_quantity += p.quantity
                    product.save()
                order.delete()
            print("Order Removed")
    
    return render(request, "Canteen/nco_order.html", context)



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
    
    categories = Category.objects.all().prefetch_related('subcategory_set')
    category_dict = {}

    for category in categories:
        subcategory_names = [subcategory.name for subcategory in category.subcategory_set.all()]
        category_dict[category.name] = subcategory_names

    context['category_dict'] = category_dict
    context['all_products'] = Product.objects.all()
    
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