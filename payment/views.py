from django.shortcuts import redirect, render
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import Product, Profile
import datetime
from django.urls import reverse
from django.conf import settings
import uuid


from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.models.customer_details import CustomerDetails
from cashfree_pg.models.order_meta import OrderMeta
from cashfree_pg.api_client import Cashfree

from cashfree_pg.api_client import Cashfree
Cashfree.XClientId = settings.CASHFREE_APP_ID
Cashfree.XClientSecret = settings.CASHFREE_SECRET_KEY
Cashfree.XEnvironment = Cashfree.SANDBOX if settings.CASHFREE_ENVIRONMENT == "TEST" else Cashfree.PRODUCTION


import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from cashfree_pg.api_client import Cashfree
from payment.models import Order

@csrf_exempt
def cashfree_webhook(request):
    if request.method == "POST":
        signature = request.headers.get("x-webhook-signature")
        timestamp = request.headers.get("x-webhook-timestamp")
        raw_body = request.body.decode("utf-8")

        try:
            # Verify signature (throws exception if invalid)
            Cashfree().PGVerifyWebhookSignature(signature, raw_body, timestamp)
        except Exception as e:
            return HttpResponse(status=400)

        try:
            data = json.loads(raw_body)
        except json.JSONDecodeError:
            return HttpResponse(status=400)

        # We only care about successful payment events
        if data.get("type") == "PAYMENT_SUCCESS_WEBHOOK":
            order_data = data.get("data", {}).get("order", {})
            cf_order_id = order_data.get("order_id")  # e.g., "order_19_7211d0b5"

            if cf_order_id and cf_order_id.startswith("order_"):
                # Extract your local order PK
                parts = cf_order_id.split("_")
                if len(parts) >= 2:
                    local_order_id = parts[1]
                    try:
                        order = Order.objects.get(pk=local_order_id)
                        order.paid = True
                        # Optional: store Cashfree payment ID
                        order.payment_id = order_data.get("cf_payment_id")
                        order.save()
                    except Order.DoesNotExist:
                        pass  # Invalid order, ignore

        return HttpResponse(status=200)

    return HttpResponse(status=405)


def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        order = Order.objects.get(id=pk)
        items = OrderItem.objects.filter(order=pk)

        if request.POST:
            status = request.POST['shipping_status']
            if status == "true":
                order = Order.objects.filter(id=pk)
                now = datetime.datetime.now()
                order.update(shipped=True, date_shipped=now)
            else:
                order = Order.objects.filter(id=pk)
                now = datetime.datetime.now()
                order.update(shipped=False, date_shipped=now)
            messages.success(request,"Shipping Status Updated")
            return redirect('home')

        return render(request, 'payment/orders.html', {"order":order, "items":items})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')

def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)

        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            order = Order.objects.filter(id=num)
            now = datetime.datetime.now()
            order.update(shipped=True, date_shipped=now)
            messages.success(request, "Shipping Status Updated")
            return redirect('home')

        return render(request, 'payment/not_shipped_dash.html', {"orders": orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)

        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            order = Order.objects.filter(id=num)
            now = datetime.datetime.now()
            order.update(shipped=False, date_shipped=now)
            messages.success(request, "Shipping Status Updated")
            return redirect('home')

        return render(request, 'payment/shipped_dash.html', {"orders": orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')

def process_order(request):
    
    if request.method == "POST":
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()
        
        payment_form = PaymentForm(request.POST or None)
        my_shipping = request.session.get('my_shipping')
        
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_pincode']}\n{my_shipping['shipping_country']}\n"
        amount_paid = totals

        if request.user.is_authenticated:
            # logged in
            user = request.user
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            order_id = create_order.pk
            for product in cart_products:
                product_id = product.id

                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price

                for key, value in quantities.items(): 
                    if int(key) == product.id:
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
                        create_order_item.save()


            for key in list(request.session.keys()):
                if key == "session_key":
                    del request.session[key]
            
            current_user = Profile.objects.filter(user__id=request.user.id)
            current_user.update(old_cart="")
            messages.success(request, "Order Placed")
            return redirect('home')
    
        else:
            # not logged in
            create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            order_id = create_order.pk
            for product in cart_products:
                product_id = product.id

                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price

                for key, value in quantities.items(): 
                    if int(key) == product.id:
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price)
                        create_order_item.save()
            
            for key in list(request.session.keys()):
                if key == "session_key":
                    del request.session[key]
            
            messages.success(request, "Order Placed")
            return redirect('home')
    else:
        messages.success(request,"Access Denied!")
        return redirect('home')
    
    
def billing_info(request):
    if request.method == "POST":
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()

        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping
        
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_pincode']}\n{my_shipping['shipping_country']}\n"
        amount_paid = totals

        # Create your local Order (same as before)
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None

        create_order = Order(
            user=user,
            full_name=full_name,
            email=email,
            shipping_address=shipping_address,
            amount_paid=amount_paid
        )
        create_order.save()

        order_id = create_order.pk

        # Create OrderItems
        for product in cart_products:
            product_id = product.id
            price = product.sale_price if product.is_sale else product.price

            for key, value in quantities.items():
                if int(key) == product.id:
                    OrderItem.objects.create(
                        order_id=order_id,
                        product_id=product_id,
                        user=user,
                        quantity=value,
                        price=price
                    )

        # Clear old cart for logged-in users
        if request.user.is_authenticated:
            Profile.objects.filter(user__id=request.user.id).update(old_cart="")

        # --- Cashfree Integration Starts Here ---
        cf_order_id = f"order_{create_order.pk}_{uuid.uuid4().hex[:8]}"  # Unique for Cashfree
        if request.user.is_authenticated:
            customer_id = f"user_{request.user.id}"        # e.g., user_1
        else:
            customer_id = f"guest_{create_order.pk}"

        customer_details = CustomerDetails(
            customer_id=customer_id,
            customer_name=full_name,
            customer_email=email,
            customer_phone=my_shipping.get('shipping_phone', '9999999999')  # Add phone to checkout form if possible
        )

        order_meta = OrderMeta(
           return_url=f"https://inefficacious-diamagnetically-agatha.ngrok-free.dev{reverse('payment_success')}?cf_order_id={cf_order_id}",
           notify_url="https://inefficacious-diamagnetically-agatha.ngrok-free.dev/payment/webhook/",
            # notify_url will be your webhook (recommended for confirmation)
        )

        create_order_request = CreateOrderRequest(
            order_id=cf_order_id,
            order_amount=float(totals),  # Must be float
            order_currency="INR",
            customer_details=customer_details,
            order_meta=order_meta
        )

        try:
            api_response = Cashfree().PGCreateOrder(
                settings.CASHFREE_API_VERSION,
                create_order_request,
                None,  # idempotency_key optional
                None
            )
            payment_session_id = api_response.data.payment_session_id
        except Exception as e:
            messages.error(request, "Payment gateway error. Please try again later.")
            return redirect('checkout')

        billing_form = PaymentForm()
      

        context = {
            "cart_products": cart_products,
            "quantities": quantities,
            "totals": totals,
            "shipping_info": my_shipping,
            "billing_form": billing_form,
            "payment_session_id": payment_session_id,
            "cf_order_id": cf_order_id,
            "cashfree_mode": "sandbox" if settings.CASHFREE_ENVIRONMENT == "TEST" else "production",
        }

        return render(request, 'payment/billing_info.html', context)

    else:
        messages.success(request, "Access Denied!")
        return redirect('home')

def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()

    if request.user.is_authenticated:
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user) 
        return render(request, 'payment/checkout.html', {"cart_products": cart_products , "quantities":quantities, "totals":totals, "shipping_form": shipping_form})
    else:
        shipping_form = ShippingForm(request.POST or None) 
        return render(request, 'payment/checkout.html', {"cart_products": cart_products , "quantities":quantities, "totals":totals })



def payment_success(request):

    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()

    for key in list(request.session.keys()):
        if key == "session_key":
            del request.session[key]

    messages.success(request, "Payment successful! Thank you for your order.")
    return render(request, "payment/payment_success.html", {})

def payment_failed(request):
    messages.success(request, "Payment Failed!!!")
    return render(request, "payment/payment_failed.html", {})

# Create your views here.
