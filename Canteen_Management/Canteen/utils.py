from django.shortcuts import redirect
from django.db.models import Sum
from django.core.mail import send_mail
from django.core.files import File
from django.conf import settings
from django.http import HttpResponse
from barcode.writer import ImageWriter
from reportlab.lib import pagesizes, units
from reportlab.pdfgen import canvas
from functools import wraps
from datetime import timedelta
from .models import *
from io import BytesIO

import barcode, os


def generate_report_pdf():
    pass


def generate_bill_pdf(personal_no, due_orders):
    # Create a response object with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{personal_no}_{timezone.localtime().now().strftime("%d-%b-%Y")}.pdf"'
    
    # Get the Order Items
    items = OrderItem.objects.filter(order__in = due_orders, order__status = 'Complete').order_by('order__timestamp')
    
    # Create a canvas object to draw on the PDF
    page_size = pagesizes.LEGAL
    pdf = canvas.Canvas(response, pagesize=pagesizes.portrait(page_size))
    page_width, page_height = pagesizes.portrait(page_size)
    
    # All texts
    title = "STC&S OFFRS' MESS CAFE"
    subtitle = "BILL OF PAYMENT"
    
    user = User.objects.get(personal_no = personal_no)
    info = ["Personal No:", "Rank:", "Name:", "Wg/Unit:", "Mobile:"]
    info_data = [personal_no, user.first_name, user.last_name, user.unit, user.phone or "None"]
    
    bill = due_orders.aggregate(Sum('total'))['total__sum']
    total = f"Total Bill Due:"
    profit = f"Bar Profit (2%):"
    pay = f"Net Payable Bill:"
    
    time = timezone.localtime().now()
    billing_date = f"Billing Date: {time.strftime('%A')}, {time.strftime('%d-%b-%Y')}"
    note = "NB: This bill is automatically generated by Django Server"
    sign = "Cafe Officer:"
    
    
    def new_bill_page(order_no=0, item_no=0, product_no=0, page_no=1, pdf=None):
        
        # Drawing the pdf Header
        image_path = os.path.join(settings.BASE_DIR, 'static', 'assets', 'img', 'logo.png')
        pdf.drawImage(image_path, 40, page_height-80, 45, 45, mask='auto')
        
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawCentredString(page_width/2, page_height-50, title) # write text in page
        
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawCentredString(page_width/2, page_height-75, subtitle)
        
        pdf.setFont("Helvetica", 8)
        pdf.drawRightString(page_width-30, page_height-45, f"Page {page_no}")
        
        pdf.line(30, page_height-95, page_width-30, page_height-95)
        
        # Drawing the user info section
        s = ""
        for i in range(len(info)):
            pdf.setFont("Helvetica", 10)
            pdf.drawString(35 + pdf.stringWidth(s, "Helvetica-Bold", 10), page_height-115, info[i])
            s = s + info[i]
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(35 + pdf.stringWidth(s, "Helvetica-Bold", 10), page_height-115, info_data[i])
            s = s + info_data[i] + "      "
        
        # Drawing the table
        gaps = 160
        prev_order = None
        page_over = complete = False
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(40, page_height-gaps, "Sr.")
        pdf.drawString(70, page_height-gaps, "Date")       
        pdf.drawString(160, page_height-gaps, "Product Name")
        pdf.drawString(page_width-275, page_height-gaps, "Rate")
        pdf.drawString(page_width-210, page_height-gaps, "Qnt.")
        pdf.drawString(page_width-170, page_height-gaps, "Total")
        pdf.drawString(page_width-100, page_height-gaps, "Order Total")
        gaps += 10
        pdf.line(35, page_height-gaps, page_width-35, page_height-gaps)
        gaps += 10
        pdf.setFont("Helvetica", 10)
        pdf.setStrokeColorRGB(0.8, 0.8, 0.8)
        for i in range(item_no, len(items)):
            if page_height-gaps-15 < 160:
                item_no = i
                page_over = True
                if items[i].order.id != prev_order:
                    product_no = 0
                    order_no += 1                    
                break
                
            if items[i].order.id != prev_order:
                gaps -= 10
                prev_order = items[i].order.id
                if i-item_no:
                    pdf.line(35, page_height-gaps, page_width-35, page_height-gaps)
                    product_no = 0
                    order_no += 1
                gaps += 15
                pdf.drawString(40, page_height-gaps, f"{order_no+1}.")
                pdf.drawString(70, page_height-gaps, f"{items[i].order.timestamp.strftime('%d-%b-%Y')}")
                pdf.drawString(page_width-100, page_height-gaps, f"{items[i].order.total} Tk")
                
            pdf.drawString(160, page_height-gaps, f"{product_no+1}. {items[i].name[:25]}")
            pdf.drawString(page_width-275, page_height-gaps, f"{items[i].price} Tk")
            pdf.drawString(page_width-205, page_height-gaps, f"{items[i].quantity}")
            pdf.drawString(page_width-170, page_height-gaps, f"{items[i].total} Tk")
            gaps += 15
            product_no += 1
        
        gaps -= 5
        pdf.setStrokeColorRGB(0, 0, 0)
        pdf.rect(35, page_height-gaps, page_width-70, gaps-145)
        # print(page_height-gaps)

        if not page_over:
            # Drawing the total Bills
            gaps += 25
            pdf.drawString(490-pdf.stringWidth(total, "Helvetica", 10), page_height-gaps, total)
            pdf.drawString(510, page_height-gaps, f"{bill} Tk")
            gaps += 15
            pdf.drawString(490-pdf.stringWidth(profit, "Helvetica", 10), page_height-gaps, profit)
            pdf.drawString(510, page_height-gaps, f"{bill*2/100} Tk")
            gaps += 15
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(490-pdf.stringWidth(pay, "Helvetica-Bold", 10), page_height-gaps, pay)
            pdf.drawString(510, page_height-gaps, f"{bill*102/100} Tk")
            complete = True
        
        # Drawing the pdf Footer
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(30, 60, billing_date[:13])
        pdf.stringWidth(billing_date[:13], "Helvetica-Bold", 10)
        pdf.setFont("Helvetica", 10)
        pdf.drawString(30 + 5 + pdf.stringWidth(billing_date[:13], "Helvetica-Bold", 10), 60, billing_date[14:])
        
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawString(30, 45, note[:3])
        pdf.setFont("Helvetica", 9)
        pdf.drawString(30 + 5 + pdf.stringWidth(note[:3], "Helvetica-Bold", 10), 45, note[4:])
        
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(page_width-250, 50, sign)
        pdf.line(page_width-250+pdf.stringWidth(sign, "Helvetica-Bold", 12)+5, 50, page_width-30, 50)
        pdf.showPage()
        current_page = pdf
        if not complete:
            new_bill_page(order_no, item_no, product_no, page_no+1, current_page)

    # Save the PDF and close the canvas
    
    new_bill_page(pdf=pdf)
    pdf.save()

    return response
    
    
    
def generate_barcode_pdf(path, name):
    
    # Create a response object with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{name}_barcode.pdf"'
    
    # Create a canvas object to draw on the PDF
    pdf = canvas.Canvas(response, pagesize=pagesizes.portrait(pagesizes.A4))
    
    # Define the size of each barcode image (50x25 mm)
    image_width = 40 * units.mm
    image_height = 24 * units.mm

    # Calculate the number of rows and columns based on the page size and image size
    page_width, page_height = pagesizes.portrait(pagesizes.A4)
    num_columns = int(page_width / image_width)
    num_rows = int(page_height / image_height)
    
    left_margin = (page_width % image_width) / 2
    top_margin = (page_height % image_height) / 2
    # print(page_width, page_height, image_width, image_height, num_columns, num_rows)

    # Load the barcode image (replace 'barcode.png' with your actual image path)
    barcode_image_path = os.path.join(settings.MEDIA_ROOT, 'barcodes', path.split('/')[-1])

    # Loop through rows and columns to place the barcode images
    for row in range(num_rows):
        for col in range(num_columns):
            x = (col * image_width) + int(left_margin)
            y = (page_height - (row + 1) * image_height) - int(top_margin)
            pdf.drawImage(barcode_image_path, x, y, image_width, image_height)

    # Save the PDF and close the canvas
    pdf.save()

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
    top_sales = OrderItem.objects.filter(order__timestamp__gte=start_time, order__timestamp__lte=today).values('name').annotate(total_sold=Sum('quantity')).order_by('-total_sold')[:5]
    top_products = [{
        'sold': item['total_sold'], 
        'product': Product.objects.get(name = item['name']),
        'revenue': Product.objects.get(name = item['name']).selling_price * item['total_sold']
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
        
    
    return {
        'sales':sales_list, 
        'revenue':revenue_list, 
        'checkout': customer_list, 
        'time':time_list, 
        'total_sales': sum(sales_list), 
        'total_revenue': round(sum(revenue_list)*100), 
        'total_checkout':sum(customer_list),
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

