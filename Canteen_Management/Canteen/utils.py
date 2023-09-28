from django.shortcuts import redirect
from django.db.models import Sum
from django.core.mail import send_mail
from django.conf import settings
from functools import wraps
from datetime import timedelta
from .models import *

def send_email_to_client(email):
    subject = "STC&S Officers Mess Cafe Verification"
    message = "You are verified by the Admin. Congrats!!!"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    
    send_mail(subject, message, from_email, recipient_list)    


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
    today = timezone.localtime().now() #timezone.localtime(timezone.now())
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
        sales = OrderItem.objects.filter(order__timestamp__gte=ti, order__timestamp__lte=next_ti, order__status='Complete').aggregate(
            sold=Sum('quantity'), 
            revenue=Sum('total')
        )        
        sales['customer'] = Order.objects.filter(timestamp__gte=ti,timestamp__lte=next_ti, status='Complete').count()
        
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