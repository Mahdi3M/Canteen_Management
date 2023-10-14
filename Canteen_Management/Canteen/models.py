from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.

class User(AbstractUser):
    ROLES = (
        ('Admin', 'Admin'),
        ('Bar NCO', 'Bar NCO'),
        ('Customer', 'Customer'),
    )

    personal_no = models.CharField(blank=True, null=True, max_length=15)
    unit = models.CharField(blank=True, null=True, max_length=32)
    role = models.CharField(max_length=10, choices=ROLES, default='Customer')
    image = models.ImageField(default='..\\static\\assets\\img\\default_user.jpg', upload_to='profile_pics', blank=True, null=True)
    address = models.CharField(blank=True, null=True, max_length=256)
    phone = models.CharField(blank=True, null=True, max_length=15)

    def __str__(self):
        return self.username
    
    @property
    def name(self):
        words = [self.first_name, self.last_name]
        result = ' '.join([word for word in words if word is not None])
        return result
    


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    

class Subcategory(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    

class Product(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(default='default.jpg', upload_to='products', blank=True, null=True)
    barcode = models.ImageField(upload_to='barcodes', blank=True, null=True)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Complete', 'Complete'),
    )
    name = models.CharField(max_length=255, default="None")
    personal_no = models.CharField(blank=True, null=True, max_length=15)
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS, default='Pending')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    product_id = models.PositiveIntegerField(null=True, blank=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    
class StockEdit(models.Model):
    name = models.CharField(max_length=255)
    product_id = models.PositiveIntegerField(null=True, blank=True)
    change = models.IntegerField(null=True, blank=True)
    comment = models.CharField(max_length=512, blank=True, null=True)
    approved = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)