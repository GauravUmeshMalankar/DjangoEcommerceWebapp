from django.db import models
from django.contrib.auth.models import User
from store.models import Product
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import datetime



# Create your models here.

class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True)
    shipping_full_name = models.CharField(max_length=255)
    shipping_email = models.CharField(max_length=255)
    shipping_address1 = models.CharField(max_length=255)
    shipping_address2 = models.CharField(max_length=255,blank=True, null=True)
    shipping_city = models.CharField(max_length=255)
    shipping_state = models.CharField(max_length=255,blank=True, null=True)
    shipping_pincode = models.CharField(max_length=200,blank=True, null=True)
    shipping_country = models.CharField(max_length=200,blank=True, null=True)
 
    class Meta:
        verbose_name_plural = "Shipping Address"
    def __str__(self):
        return f'Shipping Address - {str(self.id)}' 

def create_shipping(sender, instance, created, **kwargs):
    if created:
        user_shipping = ShippingAddress(user=instance)
        user_shipping.save()

post_save.connect(create_shipping, sender=User)
# Create your models here.

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=250)
    shipping_address = models.TextField(max_length=15000)
    amount_paid = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)
    shipped = models.BooleanField(default=False)
    date_shipped = models.DateTimeField(blank=True, null=True)
    #PayPal
    invoice = models.CharField(max_length=200, null=True, blank=True)
    paid = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.BooleanField(default=False)


    def __str__(self):
        return f'Order - {str(self.id)}'

@receiver(pre_save, sender=Order)
def set_shipped_date_on_update(sender, instance, **kwargs):
    if instance.pk:
        now = datetime.datetime.now()
        obj = sender._default_manager.get(pk=instance.pk)
        if instance.shipped and not obj.shipped:
            instance.date_shipped = now
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True)
    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order Item- {str(self.id)}'
    

