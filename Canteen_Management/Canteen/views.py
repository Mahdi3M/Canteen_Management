from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.db import transaction
from django.db.models import Sum, Count
from .models import *
from functools import wraps
from datetime import timedelta
import json

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

def get_sales_data(timespan):
    today = timezone.localtime(timezone.now())
    if timespan == "one_month_ago":
        start_time = today - timedelta(days = 30)
        diff = timedelta(days = 1)
        spans = [start_time + timedelta(days=i) for i in range(30)]
    elif timespan == "one_week_ago":
        start_time = today - timedelta(weeks = 1)
        diff = timedelta(days = 1)
        spans = [start_time + timedelta(days=i) for i in range(7)]
    elif timespan == "one_day_ago":
        start_time = today - timedelta(days = 1)
        diff = timedelta(hours = 1)
        spans = [start_time + timedelta(hours=i) for i in range(24)]
        
    sales_list = []
    revenue_list = []
    customer_list = []
    time_list = []        
    top_sales = OrderItem.objects.filter(order__timestamp__gte=start_time, order__timestamp__lte=today).values('product_id').annotate(total_sold=Sum('quantity')).order_by('-total_sold')[:5]
    top_products = [{
        'sold': item['total_sold'], 
        'product': Product.objects.get(id = item['product_id']),
        'revenue': Product.objects.get(id = item['product_id']).selling_price * item['total_sold']
        } for item in top_sales]
    
    for ti in spans:
        next_ti = ti + diff
        sales = OrderItem.objects.filter(order__timestamp__gte=ti, order__timestamp__lte=next_ti).aggregate(
            sold=Sum('quantity'), 
            revenue=Sum('total')
        )        
        sales['customer'] = Order.objects.filter(timestamp__gte=ti,timestamp__lte=next_ti).count()
        
        sales_list.append(sales['sold'] or 0)
        revenue_list.append(float(str(sales['revenue'] or 0))/100)
        customer_list.append(sales['customer'] or 0)
        time_list.append(next_ti.isoformat())
        print(next_ti)
    
    return {
        'sales':sales_list, 
        'revenue':revenue_list, 
        'customer': customer_list, 
        'time':time_list, 
        'total_sales': sum(sales_list), 
        'total_revenue': round(sum(revenue_list)*100), 
        'total_customer':sum(customer_list),
        'top_products': top_products,
        }


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
    if request.user.role == "Bar NCO":        
        context['notification'] = Product.objects.filter(stock_quantity__lte = 5)
    
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
@role_required(allowed_roles=['Admin', 'Customer'])
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
    context = {}
    
    if request.method == "POST":        
        start_date = request.POST.get('start_date')
        s_date = parse_date(start_date)
        finish_date = request.POST.get('finish_date')
        f_date = parse_date(finish_date)
        
        if start_date and finish_date:
            orders = Order.objects.filter(ba = request.user.ba, timestamp__gte = s_date, timestamp__lte=f_date)
        elif start_date:
            orders = Order.objects.filter(ba = request.user.ba, timestamp__gte = s_date)
        elif finish_date:
            orders = Order.objects.filter(ba = request.user.ba, timestamp__lte=f_date)
        else:
            orders = Order.objects.filter(ba = request.user.ba)
    else:
        orders = Order.objects.filter(ba = request.user.ba)
        
    context['order_list'] = OrderItem.objects.filter(order__in = orders, order__status = 'Complete').order_by('order__id')
    
    return render(request, "Canteen/customer_history.html", context)



#<-- ======= Bar NCO ======= -->

@login_required(redirect_field_name='next', login_url="Canteen:signin")
@role_required(allowed_roles=['Bar NCO'])
def nco_order(request):
    context = {}
    context['orders_pending'] = OrderItem.objects.filter(order__status = 'Pending').order_by('order__id')
    context['orders_complete'] = OrderItem.objects.filter(order__status = 'Complete').order_by('-order__timestamp')
    context['notification'] = Product.objects.filter(stock_quantity__lte = 5)
    
    if request.method == "POST":
        if request.POST.get('complete-order') or request.POST.get('paid-order'):
            id = request.POST.get('complete-order')
            order = Order.objects.get(id = id)
            if request.POST.get('paid-order'):
                order.paid = True            
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
def nco_bills(request):
    context = {}

    if request.method == "POST":
        if "date_btn" in request.POST:
            start_date = request.POST.get('start_date')
            s_date = parse_date(start_date)
            finish_date = request.POST.get('finish_date')
            f_date = parse_date(finish_date)
            
            print(s_date, f_date)
            
            if start_date and finish_date:
                orders = Order.objects.filter(timestamp__gte = s_date, timestamp__lte=f_date)
            elif start_date:
                orders = Order.objects.filter(timestamp__gte = s_date)
            elif finish_date:
                orders = Order.objects.filter(timestamp__lte=f_date)
            else:
                orders = Order.objects.all()
                
        elif "bill_btn" in request.POST:
            print("Bill Generated")
            orders = Order.objects.all()
    else:
        orders = Order.objects.all()
        
    context['order_list'] = OrderItem.objects.filter(order__in = orders, order__status = 'Complete').order_by('-order__timestamp')
    context['notification'] = Product.objects.filter(stock_quantity__lte = 5)
    
    return render(request, "Canteen/nco_bills.html", context)



@login_required(redirect_field_name='next', login_url="Canteen:signin")
@role_required(allowed_roles=['Bar NCO'])
def nco_inventory(request):
    if request.method == "POST":
        if request.POST.get('form_name') == "add_new_product":            
            new_Product = Product()        
            new_Product.name = request.POST.get('productName')
            new_Product.image = request.FILES.get('image')
            new_Product.buying_price = request.POST.get('buyingPrice')
            new_Product.selling_price = request.POST.get('sellingPrice')
            new_Product.stock_quantity = request.POST.get('amount')
            
            category = request.POST.get('category')
            new_category = request.POST.get('new-category')
            subcategory = request.POST.get('subCategory')
            new_subcategory = request.POST.get('new-sub-category') 
            
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
        
        elif request.POST.get('form_name') == "edit_product":
            product_name = request.POST.get('productName')
            product = Product.objects.get(name = product_name)
            
            if request.POST.get('editProductName'):
                product.name = request.POST.get('editProductName')               
            if request.POST.get('add_amount'):
                product.stock_quantity += request.POST.get('add_amount')                
            if request.POST.get('remove_amount'):
                product.stock_quantity -= request.POST.get('remove_amount')               
            if request.POST.get('buyingPrice'):
                product.buying_price = request.POST.get('buyingPrice')               
            if request.POST.get('sellingPrice'):
                product.selling_price = request.POST.get('sellingPrice')
                
            product.save()
        
        elif request.POST.get('form_name') == "edit_category":
            category_name = request.POST.get('category')
            category = Category.objects.get(name = category_name)
            
            if request.POST.get('editCategoryName'):
                category.name = request.POST.get('editCategoryName')
                
            category.save()
        
        elif request.POST.get('form_name') == "edit_subcategory":
            subcategory_name = request.POST.get('subCategory')
            subcategory = Subcategory.objects.get(name = subcategory_name)
            
            if request.POST.get('editSubCategoryName'):
                subcategory.name = request.POST.get('editSubCategoryName')
                
            subcategory.save()
            
            
    context = {}
    
    categories = Category.objects.all()

    category_dict = {}

    for category in categories:
        subcategories = Subcategory.objects.filter(category=category)
        subcategory_dict = {}
        
        for subcategory in subcategories:
            products = Product.objects.filter(subcategory=subcategory)
            product_names = [product.name for product in products]
            subcategory_dict[subcategory.name] = product_names
        
        category_dict[category.name] = subcategory_dict

    context['category_dict'] = category_dict
    context['all_products'] = Product.objects.all()
    context['notification'] = Product.objects.filter(stock_quantity__lte = 5)
    
    return render(request, "Canteen/nco_inventory.html", context)



#<-- ======= Admin ======= -->

@login_required(redirect_field_name='next', login_url="Canteen:signin")
@role_required(allowed_roles=['Admin'])
def home(request):
    
    context = {}

    context['monthly'] = get_sales_data("one_month_ago")
    context['weekly'] = get_sales_data("one_week_ago")
    context['daily'] = get_sales_data("one_day_ago")
    
    return render(request, "Canteen/index.html", context)



@login_required(redirect_field_name='next', login_url="Canteen:signin")
@role_required(allowed_roles=['Admin'])
def admin_summary(request):

    return render(request, "Canteen/admin_summary.html")



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