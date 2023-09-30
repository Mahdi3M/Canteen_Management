from django.shortcuts import redirect
from django.db.models import Sum
from django.core.mail import send_mail
from django.core.files import File
from django.conf import settings
from django.http import HttpResponse
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes, units
from functools import wraps
from datetime import timedelta
from .models import *
from io import BytesIO

import barcode, os
    
    
def generate_barcode_pdf(path):
    
    # Create a response object with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="barcode_sheet.pdf"'
    
    # Create a canvas object to draw on the PDF
    c = canvas.Canvas(response, pagesize=pagesizes.portrait(pagesizes.A4))
    
    # Define the size of each barcode image (50x25 mm)
    image_width = 40 * units.mm
    image_height = 24 * units.mm

    # Calculate the number of rows and columns based on the page size and image size
    page_width, page_height = pagesizes.portrait(pagesizes.A4)
    num_columns = int(page_width / image_width)
    num_rows = int(page_height / image_height)
    
    left_margin = (page_width % image_width) / 2
    top_margin = (page_height % image_height) / 2
    print(page_width, page_height, image_width, image_height, num_columns, num_rows)

    # Load the barcode image (replace 'barcode.png' with your actual image path)
    barcode_image_path = os.path.join(settings.MEDIA_ROOT, 'barcodes', path.split('/')[-1])

    # Loop through rows and columns to place the barcode images
    for row in range(num_rows):
        for col in range(num_columns):
            x = (col * image_width) + int(left_margin)
            y = (page_height - (row + 1) * image_height) - int(top_margin)
            c.drawImage(barcode_image_path, x, y, image_width, image_height)

    # Save the PDF and close the canvas
    c.save()

    return response


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
    

def get_barcode(product):
    category_id = str(product.category.id).zfill(2)
    subcategory_id = str(product.subcategory.id).zfill(4)
    product_id = str(product.id).zfill(6)
    barcode_id = category_id+subcategory_id+product_id
    
    EAN = barcode.get_barcode_class('ean13')
    ean = EAN(barcode_id, writer = ImageWriter())
    buffer = BytesIO()
    ean.write(buffer)
    product.barcode.save(f'{product.name}.png', File(buffer), save=False)
    
    product.save()

