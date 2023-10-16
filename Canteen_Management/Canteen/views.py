from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.dateparse import parse_date
from django.http import JsonResponse
from django.db.models import Sum
from django.db import transaction
from .models import *
from .utils import *
import json
import random

# Create your views here.

#<-- ======= Ajax Requests and Others ======= -->

def send_otp_email(request):
    if request.method == 'POST':
        otp = ''.join(random.choices('0123456789', k=6))

        # Send the OTP via email
        subject = 'OTP Verification'
        message = f'Your OTP: {otp}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [request.POST.get('email')]

        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            return JsonResponse({'success': True, 'otp': otp})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        

def get_barcode_data(request):
    if request.method == "POST":
        barcode = request.POST.get('barcode')
        
        product_id = int(barcode[6:11])
        product = Product.objects.get(id = product_id)
        name = product.name
        price = product.selling_price
        qnt = product.stock_quantity
        image = product.image.url

        try:
            return JsonResponse({'success': True, 'id':product_id, 'name': name, 'price': str(price), 'available': qnt, 'image': image})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        


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
                return redirect("Canteen:nco_inventory")
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
        image_file = request.FILES.get('image')
        prefix = request.POST.get('prefixType')
        number = request.POST.get('number')
        personal_no = prefix+number
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
                myuser.personal_no = personal_no
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
    if request.method == "POST":
        
        user = request.user
        if "saveChanges" in request.POST:
            image = request.FILES.get('image')
            name = request.POST.get('fullName')
            rank = request.POST.get('rank')
            unit = request.POST.get('unit')
            address = request.POST.get('address')
            phone = request.POST.get('phone')
            
            if image:
                user.image = image
            if name:
                user.last_name = name
            if rank:
                user.first_name = rank
            if unit:
                user.unit = unit
            if address:
                user.address = address
            if phone:
                user.phone = phone                
            user.save()
        
        elif "changePassword" in request.POST:
            current = request.POST.get('password')
            new = request.POST.get('newpassword')
            renew = request.POST.get('renewpassword')
            
            if check_password(current, user.password):
                if new == renew:
                    user.set_password(new)
                    user.save()
                else:
                    messages.error(request, "New Password and Re-enter Password did not match")
            else:
                messages.error(request, "Current Password Wrong")
            
    context = {}
    if request.user.role == "Bar NCO":
        context['notification'] = Product.objects.filter(stock_quantity__lte = 5)
    return render(request, "Canteen/profile.html", context)



#<-- ======= Customer ======= -->

@login_required(redirect_field_name='next', login_url="Canteen:signin")
def customer_catalog(request):
    context = {}
    
    category_names = Category.objects.values_list('name', flat=True)
    subcategory_names = Subcategory.objects.values_list('name', flat=True)
    product_names = Product.objects.values_list('name', flat=True)
    context["keywords"] = list(category_names) + list(subcategory_names) + list(product_names)
    if request.user.role == "Admin":
        context['p_users'] = User.objects.filter(is_active = False).count()
        context['s_requests'] = StockEdit.objects.filter(approved = False).count()
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
    if request.user.role == "Admin":
        context['p_users'] = User.objects.filter(is_active = False).count()
        context['s_requests'] = StockEdit.objects.filter(approved = False).count()
    if request.method == "POST":
        cartJSON = request.POST.get("cartJSON")
        cart = json.loads(cartJSON)
        total = request.POST.get("cartTotal")
        
        with transaction.atomic():
            new_Order = Order()
            new_Order.name = request.user.name
            new_Order.personal_no = request.user.personal_no
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
            orders = Order.objects.filter(personal_no = request.user.personal_no, timestamp__gte = s_date, timestamp__lte=f_date)
        elif start_date:
            orders = Order.objects.filter(personal_no = request.user.personal_no, timestamp__gte = s_date)
        elif finish_date:
            orders = Order.objects.filter(personal_no = request.user.personal_no, timestamp__lte=f_date)
        else:
            orders = Order.objects.filter(personal_no = request.user.personal_no)
    else:
        orders = Order.objects.filter(personal_no = request.user.personal_no)
        
    context['order_list'] = OrderItem.objects.filter(order__in = orders, order__status = 'Complete').order_by('-order__timestamp')    
    if request.user.role == "Admin":
        context['p_users'] = User.objects.filter(is_active = False).count()
        context['s_requests'] = StockEdit.objects.filter(approved = False).count()
        
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
        if "complete-order" in request.POST:
            id = request.POST.get('order-id')
            order = Order.objects.get(id = id)
            order.status = 'Complete'
            order.save()
            
        elif "remove-order" in request.POST:
            id = request.POST.get('order-id')
            order = Order.objects.get(id = id)
            products = OrderItem.objects.filter(order = order)
            with transaction.atomic():
                for p in products:
                    product = Product.objects.get(id = p.product_id)
                    product.stock_quantity += p.quantity
                    product.save()
                order.delete()
            print("Order Removed")
            
        elif "checkout-order" in request.POST:
            cartJSON = request.POST.get("cartJSON")
            cart = json.loads(cartJSON)
            total = request.POST.get("cartTotal")
            prefix = request.POST.get("prefixType")
            num = request.POST.get("personal_no")
            personal_no = prefix+num
            customer = User.objects.get(personal_no=personal_no)
            
            with transaction.atomic():
                new_Order = Order()
                new_Order.name = customer.name
                new_Order.personal_no = personal_no
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
    return render(request, "Canteen/nco_order.html", context)

@login_required(redirect_field_name='next', login_url="Canteen:signin")
@role_required(allowed_roles=['Bar NCO'])
def nco_bills(request):
    context = {}

    if request.method == "POST":
        start_date = request.POST.get('start_date')
        s_date = parse_date(start_date)
        finish_date = request.POST.get('finish_date')
        f_date = parse_date(finish_date)
        prefix = request.POST.get('prefixType')
        number = request.POST.get('personal_no')
        personal_no = prefix + number
        
        context['start'] = start_date
        context['finish'] = finish_date
        context['prefix'] = prefix
        context['number'] = number
        
        
        orders = Order.objects.filter(timestamp__gte = s_date, timestamp__lte=f_date, personal_no= personal_no)
        due_orders = Order.objects.filter(timestamp__gte = s_date, timestamp__lte=f_date, personal_no= personal_no, paid=False)
                
        if "bill_btn" in request.POST:
            return generate_bill_pdf(personal_no, due_orders)
                
        elif "payment_btn" in request.POST:
            with transaction.atomic():
                for order in orders:
                    order.paid = True
                    order.save()
            print("Payment Complete")
            
    else:
        orders = Order.objects.all()
        due_orders = Order.objects.filter(paid = False)
        
    context['order_list'] = OrderItem.objects.filter(order__in = orders, order__status = 'Complete').order_by('-order__timestamp')
    context['total_due'] = due_orders.aggregate(Sum('total'))['total__sum']
    context['notification'] = Product.objects.filter(stock_quantity__lte = 5)
    
    return render(request, "Canteen/nco_bills.html", context)



@login_required(redirect_field_name='next', login_url="Canteen:signin")
@role_required(allowed_roles=['Bar NCO'])
def nco_inventory(request):
    if request.method == "POST":
        if "barcode_btn" in request.POST:
            product_id = request.POST.get('barcode')
            product_obj = Product.objects.get(id = product_id)
            if product_obj:
                return generate_barcode_pdf(product_obj.barcode.url, product_obj.name)
                
                
        elif "add_new_product" in request.POST:
            new_Product = Product()        
            new_Product.name = request.POST.get('productName')
            new_Product.image = request.FILES.get('image')
            new_Product.buying_price = request.POST.get('buyingPrice')
            new_Product.selling_price = request.POST.get('sellingPrice')
            new_Product.stock_quantity = request.POST.get('amount')
            
            category = request.POST.get('category')
            if not category:
                category = request.POST.get('new-category')
            subcategory = request.POST.get('subCategory')
            if not subcategory:
                subcategory = request.POST.get('new-sub-category') 
            
            if Category.objects.filter(name = category).exists():
                new_Product.category = Category.objects.get(name = category)
            else:            
                new_Category = Category(name = category)
                new_Category.save()
                new_Product.category = new_Category
            
            if Subcategory.objects.filter(name = subcategory, category=new_Product.category).exists():
                new_Product.subcategory = Subcategory.objects.get(name = subcategory)
            else:
                new_Subcategory = Subcategory(name = subcategory, category = new_Product.category)
                new_Subcategory.save()
                new_Product.subcategory = new_Subcategory
            new_Product.save()            
            get_barcode(new_Product)
        
        elif "edit_product" in request.POST:
            product_name = request.POST.get('productName')
            product = Product.objects.get(name = product_name)
            
            if request.POST.get('editProductName'):
                product.name = request.POST.get('editProductName')           
            if request.POST.get('buyingPrice'):
                product.buying_price = request.POST.get('buyingPrice')               
            if request.POST.get('sellingPrice'):
                product.selling_price = request.POST.get('sellingPrice')
                
            product.save()
        
        elif "edit_stock" in request.POST:
            product_name = request.POST.get('productName')
            product = Product.objects.get(name = product_name)
            stock = StockEdit(name = product_name, product_id  = product.id)
            
            if request.POST.get('add_amount'):
                stock.change = int(request.POST.get('add_amount'))
            if request.POST.get('remove_amount'):
                stock.change = int(request.POST.get('remove_amount')) * (-1)                
            if request.POST.get('comment'):
                stock.comment = request.POST.get('comment')
                
            stock.save()
        
        elif "edit_category" in request.POST:
            category_name = request.POST.get('category')
            category = Category.objects.get(name = category_name)
            
            if request.POST.get('editCategoryName'):
                category.name = request.POST.get('editCategoryName')
                
            category.save()
        
        elif "edit_subcategory" in request.POST:
            category_name = request.POST.get('category')
            subcategory_name = request.POST.get('subCategory')
            category = Category.objects.get(name = category_name)
            subcategory = Subcategory.objects.get(name = subcategory_name, category = category)
            
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
    context['all_products'] = Product.objects.all().order_by('name')
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
    context['p_users'] = User.objects.filter(is_active = False).count()
    context['s_requests'] = StockEdit.objects.filter(approved = False).count()
        
    return render(request, "Canteen/index.html", context)



@login_required(redirect_field_name='next', login_url="Canteen:signin")
@role_required(allowed_roles=['Admin'])
def admin_users(request):
    
    if request.method == "POST":
        if request.POST.get("user_id_add"):
            with transaction.atomic():
                id = request.POST.get("user_id_add")
                role = request.POST.get("userRole")
                new_user = User.objects.get(id = id)
                new_user.is_active = True
                new_user.role = role
                new_user.save()
                send_email_to_client(new_user.email)
            
        if request.POST.get("user_id_remove"):
            id = request.POST.get("user_id_remove")
            delete_user = User.objects.get(id = id)
            delete_user.delete()
    
    context = {}    
    context["pending_users"] = User.objects.filter(is_active = False)
    context["all_users"] = User.objects.filter(is_active = True)
    context['p_users'] = User.objects.filter(is_active = False).count()
    context['s_requests'] = StockEdit.objects.filter(approved = False).count()
    
    return render(request, "Canteen/admin_users.html", context)



@login_required(redirect_field_name='next', login_url="Canteen:signin")
@role_required(allowed_roles=['Admin'])
def admin_stock(request):    
    if request.method == "POST":
        id = request.POST.get("stock_change_id")
        stock = StockEdit.objects.get(id = id)
        product = Product.objects.get(id = stock.product_id)
        if "stock_change_approved" in request.POST:
            product.stock_quantity += stock.change
            stock.approved = True
            product.save()
            stock.save()
        if "stock_change_denied" in request.POST:
            stock.delete()
            print("denied")
    
    context = {}    
    context["stock_changes"] = StockEdit.objects.filter(approved = False)
    context['p_users'] = User.objects.filter(is_active = False).count()
    context['s_requests'] = StockEdit.objects.filter(approved = False).count()
    
    return render(request, "Canteen/admin_stock.html", context)