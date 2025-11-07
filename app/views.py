from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from .forms import UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from .models import Profile
def index(request):
    return render(request, 'index.html')

from django.shortcuts import render
from .models import Product

def product_list(request):
    products = Product.objects.all()
    categories = ['Technology', 'Audio', 'Fashion', 'Grocery']
    categorized_products = {cat: products.filter(category=cat) for cat in categories}
    return render(request, 'products.html', {'categorized_products': categorized_products})

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'product_detail.html', {'product': product})



def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password!")

    return render(request, 'login.html')


def logout_view(request):
    auth_logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile')  # ✅ show updated profile after save
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'profile': profile,
        'editing': request.method == 'POST' or request.GET.get('edit') == 'true',
    }
    return render(request, 'profile.html', context)


@login_required
def cart(request):
    # Initialize cart in session if it doesn't exist
    cart = request.session.get('cart', {})

    if request.method == 'POST':
        product_id = str(request.POST.get('product_id'))
        action = request.POST.get('action')

        if action == 'remove' and product_id in cart:
            del cart[product_id]
        elif action == 'update':
            qty = int(request.POST.get('quantity', 1))
            if qty > 0:
                cart[product_id] = qty
            else:
                del cart[product_id]

        request.session['cart'] = cart
        return redirect('cart')

    # Prepare cart items for template
    products_in_cart = []
    total_price = 0
    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=pid)
        subtotal = product.price * qty
        total_price += subtotal
        products_in_cart.append({
            'product': product,
            'quantity': qty,
            'subtotal': subtotal
        })

    return render(request, 'cart.html', {'cart_items': products_in_cart, 'total_price': total_price})


@login_required
def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)
    cart = request.session.get('cart', {})  # get existing cart

    # Add product to cart or increase quantity
    if str(product.id) in cart:
        cart[str(product.id)] += 1
    else:
        cart[str(product.id)] = 1

    request.session['cart'] = cart  # save cart back to session
    return redirect('cart')  # redirect to cart page

@login_required
def thankyou(request):
    return render(request, 'thankyou.html')


@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    products_in_cart = []
    total_price = 0

    # Prepare cart items
    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=pid)
        subtotal = float(product.price) * qty  # convert Decimal to float
        total_price += subtotal
        products_in_cart.append({
            'product_id': product.id,
            'title': product.title,
            'quantity': qty,
            'subtotal': subtotal,
            'price': float(product.price)
        })

    if request.method == 'POST':
        # Collect shipping info from form
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        # Collect payment info from form
        payment_method = request.POST.get('payment_method')
        card_number = request.POST.get('card_number', '')
        expiry = request.POST.get('expiry', '')
        cvv = request.POST.get('cvv', '')

        # Save order info to session for displaying in thank you page
        request.session['last_order'] = {
            'name': name,
            'email': email,
            'phone': phone,
            'address': address,
            'payment_method': payment_method,
            'card_number': card_number,
            'expiry': expiry,
            'cvv': cvv,
            'cart': products_in_cart,  # now JSON-serializable
            'total_price': float(total_price)
        }

        # Clear cart
        request.session['cart'] = {}

        messages.success(request, "Order placed successfully!")
        return redirect('thankyou')  # Redirect to Thank You page

    return render(request, 'checkout.html', {
        'cart_items': products_in_cart,
        'total_price': total_price
    })
    
    
def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        print(f"New message from {name} ({email}): {message}")
        messages.success(request, "Message sent successfully!")
    return render(request, 'contact.html')


def portfolio(request):
    return render(request, 'portfolio.html')