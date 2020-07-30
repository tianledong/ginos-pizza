from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.forms import PasswordChangeForm

from .form import *
from .models import *
import os
import stripe
from stripe import error

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def index(request):
    return render(request, 'orders/home.html')


def signup(request):
    if request.method == 'GET':
        form = UserSignUpForm()
        context = {'form': form}
        return render(request, 'orders/signup.html', context)
    elif request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            try:
                user = User.objects.create_user(username, email, password)
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                login(request, user)
                messages.add_message(request, messages.SUCCESS, f'Welcome! {first_name}')
                return render(request, 'orders/home.html')
            except:
                messages.add_message(request, messages.ERROR, 'Username has been taken!')
                context = {'form': form}
                return render(request, 'orders/signup.html', context)
        else:
            messages.add_message(request, messages.ERROR, 'It is not valid!')
            context = {'form': form}
            return render(request, 'orders/signup.html', context)


def signin(request):
    if request.method == 'GET':
        form = UserLoginForm()
        context = {'form': form}
        return render(request, 'orders/signin.html', context)
    elif request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.add_message(request, messages.SUCCESS,
                                     f'Welcome, <strong>{request.user.username}</strong>')
                return render(request, 'orders/home.html')
            else:
                messages.add_message(request, messages.ERROR, 'Invalid Username/Password.')
                return render(request, 'orders/signin.html', {'form': UserLoginForm()})
        return render(request, 'orders/signin.html', {'form': UserLoginForm()})


@login_required(login_url='signin')
def logout_view(request):
    logout(request)
    messages.info(request, 'You have logged out.')
    return render(request, 'orders/home.html')


def menu(request):
    product = Product.objects.all()
    topping = Topping.objects.all()
    additional = Additional.objects.all()
    category = Category.objects.all()
    context = {'product': product, 'topping': topping, 'additional': additional, 'category': category}
    return render(request, 'orders/menu.html', context)


def detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    topping = Topping.objects.all()
    additional = Additional.objects.all()
    context = {'product': product, 'topping': topping, 'additional': additional}
    return render(request, 'orders/detail.html', context)


@login_required(login_url='signin')
def add_to_cart(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        size = request.POST['size']
        quantity = int(request.POST['quantity'])
        # if user submitted unqualified number
        if quantity <= 0 or quantity > 5:
            messages.error(request, 'One time purchase quantity cannot be <strong>negative</strong> or '
                                    '<strong>over 5</strong>. Please order again!')
            return redirect(f'detail/{product_id}')

        order_product = OrderProduct.objects.create(user=request.user, product=product, size=size,
                                                    quantity=quantity)
        # add toppings
        if product.topping_num:
            topping = request.POST.getlist('toppings')
            for top in topping:
                top_item = get_object_or_404(Topping, name=top)
                order_product.toppings.add(top_item)
        # add extra
        if product.is_allowed_additional:
            additional = request.POST.getlist('additional')
            for a in additional:
                a_item = get_object_or_404(Additional, name=a)
                order_product.additional.add(a_item)
        # get oder's Queryset by user and it should be unfinished order
        order_qs = Order.objects.filter(user=request.user, finished=False)
        if order_qs.exists():
            order = order_qs[0]
            for o in order.orderProduct.all():
                identical = True
                # check toppings
                if len(o.toppings.all()) == len(order_product.toppings.all()):
                    for i in range(len(o.toppings.all())):
                        if o.toppings.all()[i] != order_product.toppings.all()[i]:
                            identical = False
                            break
                else:
                    identical = False
                # check additional
                if len(o.additional.all()) == len(order_product.additional.all()):
                    for j in range(len(o.additional.all())):
                        if o.additional.all()[j] != order_product.additional.all()[j]:
                            identical = False
                            break
                else:
                    identical = False
                # if there is the exact same order product, increase the quantity
                if identical and o.ordered is False and o.user == request.user and o.size == order_product.size \
                        and o.product.id == order_product.product.id:
                    o.quantity += order_product.quantity
                    o.save()
                    order_product.delete()
                    order.save()
                    messages.add_message(request, messages.SUCCESS, f'<strong>{order_product.product.name}</strong> '
                                                                    f'has been updated: + {order_product.quantity}')
                    return redirect('cart_view')
            # No exact same order product, add a new one
            order.orderProduct.add(order_product)
        # no unfinished order of this user, create a new order and add product
        else:
            order = Order.objects.create(user=request.user)
            order.orderProduct.add(order_product)

        messages.success(request, f'<strong>{order_product.product.name}</strong> x {order_product.quantity} '
                                  f'has been add to cart')
        return redirect('cart_view')


# helper function to find specific product by id
def find_product_helper(request, order_product_id):
    order_qs = Order.objects.filter(user=request.user, finished=False)
    if order_qs.exists():
        order = order_qs[0]
        order_product_qs = order.orderProduct.filter(id=order_product_id, ordered=False)
        if order_product_qs.exists():
            order_product = order_product_qs[0]
            return order_product
    return None


@login_required(login_url='signin')
def remove_cart_item(request, order_product_id):
    order_product = find_product_helper(request, order_product_id)
    if order_product:
        order_product_name = str(order_product.product.name)
        order_product.delete()
        messages.add_message(request, messages.SUCCESS,
                             f'<strong>{order_product_name}</strong> successfully removed!')
        return redirect('cart_view')
    messages.add_message(request, messages.ERROR, 'No item found')
    return redirect('cart_view')


@login_required(login_url='signin')
def plus_cart_item(request, order_product_id):
    order_product = find_product_helper(request, order_product_id)
    if order_product:
        order_product_name = str(order_product.product.name)
        order_product.quantity += 1
        order_product.save()
        messages.add_message(request, messages.SUCCESS,
                             f'<strong>{order_product_name}</strong> successfully added 1!')
        return redirect('cart_view')
    messages.add_message(request, messages.ERROR, 'No item found')
    return redirect('cart_view')


@login_required(login_url='signin')
def minus_cart_item(request, order_product_id):
    order_product = find_product_helper(request, order_product_id)
    if order_product:
        order_product_name = str(order_product.product.name)
        order_product.quantity -= 1
        # if quantity <= 0 delete it
        if order_product.quantity <= 0:
            order_product.delete()
        else:
            order_product.save()
        messages.add_message(request, messages.SUCCESS,
                             f'<strong>{order_product_name}</strong> successfully subtracted 1!')
        return redirect('cart_view')
    messages.add_message(request, messages.ERROR, 'No item found')
    return redirect('cart_view')


@login_required(login_url='signin')
def cart_view(request):
    order_qs = Order.objects.filter(user=request.user, finished=False)
    if order_qs.exists():
        context = {'order': order_qs[0]}
        return render(request, 'orders/cart.html', context)
    return render(request, 'orders/cart.html')


@login_required(login_url='signin')
def clear_cart(request):
    order_qs = Order.objects.filter(user=request.user, finished=False)
    if order_qs.exists():
        order = order_qs[0]
        for i in order.orderProduct.all():
            i.delete()
        order.delete()
        messages.success(request, 'Your cart has been cleared')
        return redirect('cart_view')
    messages.error(request, 'No item found')
    return redirect('cart_view')


@login_required(login_url='signin')
def checkout(request):
    order_qs = Order.objects.filter(user=request.user, finished=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.total_price() <= 0:
            messages.error(request, "You have nothing to check out!")
            return redirect('cart_view')

        if request.method == 'GET':
            return render(request, 'orders/checkout.html')
        elif request.method == 'POST':
            try:
                token = request.POST.get('stripeToken')
                amount = int(order.total_price() * 100)  # value in cents
                stripe_charge = stripe.Charge.create(amount=amount, currency="usd", source=token,
                                                     description=f"charge for order #{order.id} at Gino's"
                                                     )
                name_on_card = request.POST.get('name-on-card')
                address = request.POST.get('address')
                address1 = request.POST.get('address1')
                city = request.POST.get('city')
                state = request.POST.get('state')
                zip_code = request.POST.get('zip')

                # Check the address is already exist.
                billing_address, created = BillingAddress.objects.get_or_create(name_on_card=name_on_card,
                                                                                address=address,
                                                                                address1=address1, city=city,
                                                                                state=state,
                                                                                zip=zip_code, user=request.user)

                for product in order.orderProduct.all():
                    product.ordered = True
                    product.save()
                order.finished = True
                order.orderTime = timezone.now()
                order.save()

                Payment.objects.create(order=order, stripe_id=stripe_charge['id'], user=request.user,
                                       billing_address=billing_address, amount=amount)

                context = {'orders': order}
                return render(request, 'orders/success.html', context)
            except stripe.error.CardError as e:
                # Since it's a decline, stripe.error.CardError will be caught
                body = e.json_body
                err = body.get('error', {})
                messages.warning(request, f"{err.get('message')}")
                return redirect("/")

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(request, "Rate limit error")
                return redirect("/")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                messages.warning(request, "Invalid parameters")
                return redirect("/")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(request, "Not authenticated")
                return redirect("/")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(request, "Network error")
                return redirect("/")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user
                messages.warning(request, "Something went wrong. You were not charged. Please try again.")
                return redirect("/")

            except Exception as e:
                messages.warning(request, "A serious error occurred. You were not charged.")
                return redirect("/")

    messages.error(request, "You have nothing to check out!")
    return redirect('cart_view')


@login_required(login_url='signin')
def order_history(request):
    order_qs = Order.objects.filter(user=request.user, finished=True)
    return render(request, 'orders/order_history.html', {'orders': order_qs})


@login_required(login_url='signin')
def order_history_detail(request, order_id):
    order_qs = Order.objects.filter(user=request.user, finished=True, id=order_id)
    if order_qs.exists():
        return render(request, 'orders/order_history_detail.html', {'orders': order_qs[0]})
    messages.error(request, "Cannot check this history for you...")
    return redirect('order_history')


def about_us(request):
    return render(request, 'orders/about_us.html')


def contact(request):
    return render(request, 'orders/contact.html')


@login_required(login_url='signin')
def change_password(request):
    if request.method == "GET":
        form = PasswordChangeForm(request.user)
        return render(request, 'orders/change_password.html', {'form': form})
    elif request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Success! Your password has been updated!")
            return redirect('change_password')
        else:
            messages.error(request, "Sorry, either your old password is incorrect or your new password does not match!")
            return redirect('change_password')


@login_required(login_url='signin')
def change_email(request):
    if request.method == "GET":
        form = ChangeEmail()
        return render(request, 'orders/change_email.html', {'form': form})
    elif request.method == "POST":
        form = ChangeEmail(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            email1 = form.cleaned_data.get('email_confirm')
            if email == email1:
                request.user.email = email
                request.user.save()
                messages.success(request, "Success! Your email has been updated!")
                return redirect('change_email')

        messages.error(request, "Sorry, Your new email does not match!")
        return redirect('change_email')
