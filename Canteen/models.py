from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    ROLES = (
        ('Admin', 'Admin'),
        ('Bar NCO', 'Bar NCO'),
        ('Customer', 'Customer'),
    )

    ba = models.CharField(blank=True, null=True, max_length=6)
    unit = models.CharField(blank=True, null=True, max_length=32)
    role = models.CharField(max_length=10, choices=ROLES, default='Customer')
    image = models.ImageField(default='default.jpg', upload_to='profile_pics', blank=True, null=True)

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
    # barcode = models.CharField(max_length=50, unique=True)
    # description = models.TextField(blank=True, null=True)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    def calculate_profit(self):
        return self.selling_price - self.buying_price
