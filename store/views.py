from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required # For restricting access
from django.utils.crypto import get_random_string # For generating order number
from .models import Product, Cart, CartItem, Order, OrderItem # All your models
from .models import Product, Category
from .forms import UserProfileForm
from .forms import OrderForm, RegistrationForm # The form you created
from django.contrib import messages

def home(request):
    # Retrieve all products where 'is_available' is True, 
    # ordering them by their name (as defined in the model Meta class)
    products = Product.objects.filter(is_available=True)
    
    # Define the context dictionary to pass data to the template
    context = {
        'products': products
    }
    
    # Render the home.html template, passing the products in the context
    return render(request, 'home.html', context)

def product_detail(request, product_slug):
    # Use get_object_or_404 to retrieve the product by its slug.
    # If a product with that slug is not found, Django automatically returns a 404 error.
    product = get_object_or_404(
        Product, 
        slug=product_slug, 
        is_available=True
    )
    
    context = {
        'product': product,
    }
    
    return render(request, 'store/product_detail.html', context)

# Helper function to get the current cart ID from the session
def _get_cart_id(request):
    """Retrieves the cart_id from the session or generates a new one."""
    cart_id = request.session.get('cart_id')
    if not cart_id:
        # If no cart_id exists in the session, create a new one
        # and store it in the session
        request.session.create()
        cart_id = request.session.session_key
        request.session['cart_id'] = cart_id
    return cart_id

def add_cart(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    cart_id = _get_cart_id(request)
    
    try:
        cart = Cart.objects.get(cart_id=cart_id)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=cart_id)
        cart.save()
    
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        
        # 🛑 STOCK CHECK LOGIC 🛑
        if cart_item.quantity < product.stock:
            # Only increment if the total quantity in the cart is less than available stock
            cart_item.quantity += 1
            cart_item.save()
        else:
            # If quantity is maxed out, send a message
            messages.info(request, f"Sorry, only {product.stock} items of {product.name} are available in stock.")
            
    except CartItem.DoesNotExist:
        # If it's a new item, check if stock is > 0 before creating
        if product.stock > 0:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart
            )
            cart_item.save()
        else:
             messages.error(request, f"{product.name} is currently out of stock.")
    
    # Conditional redirect logic remains the same
    if 'cart' in request.META.get('HTTP_REFERER', ''):
        return redirect('cart')
    else:
        return redirect('product_detail', product_slug=product_slug)


def cart(request, total=0, quantity=0, cart_items=None):
    """
    Renders the shopping cart page, calculating the total price and quantity.
    """
    try:
        # 1. Get the current cart based on the session ID
        cart_id = _get_cart_id(request)
        cart_obj = Cart.objects.get(cart_id=cart_id)
        
        # 2. Retrieve all active items linked to this cart
        cart_items = CartItem.objects.filter(cart=cart_obj, is_active=True)
        
        # 3. Calculate the total price and total quantity
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
            
    except Cart.DoesNotExist:
        # If the cart doesn't exist, items and totals remain 0
        pass

    # 4. Prepare the context to send to the template
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items
    }
    
    return render(request, 'store/cart.html', context)


def remove_cart(request, product_slug):
    """
    Handles removing a single CartItem instance entirely from the cart.
    """
    # 1. Get the product to be removed
    product = get_object_or_404(Product, slug=product_slug)
    
    # 2. Get the current Cart object
    cart_id = _get_cart_id(request)
    cart = Cart.objects.get(cart_id=cart_id)
    
    # 3. Find the CartItem associated with the product and cart
    try:
        cart_item = CartItem.objects.get(
            product=product,
            cart=cart
        )
        # 4. Delete the CartItem from the database
        cart_item.delete()
        
    except CartItem.DoesNotExist:
        # If the item doesn't exist, just pass (or show a message)
        pass 
        
    # 5. Redirect back to the cart page
    return redirect('cart')


def decrease_cart(request, product_slug):
    """
    Handles decreasing the quantity of a product in the cart by one.
    If quantity becomes zero, the item is removed.
    """
    # 1. Get the product to be modified
    product = get_object_or_404(Product, slug=product_slug)
    
    # 2. Get the current Cart object
    cart_id = _get_cart_id(request)
    cart = Cart.objects.get(cart_id=cart_id)
    
    # 3. Find the CartItem
    try:
        cart_item = CartItem.objects.get(
            product=product,
            cart=cart
        )
        
        # 4. Decrease quantity or remove item
        if cart_item.quantity > 1:
            # Decrease quantity by 1
            cart_item.quantity -= 1
            cart_item.save()
        else:
            # If quantity is 1, delete the item entirely
            cart_item.delete()
            
    except CartItem.DoesNotExist:
        # If the item doesn't exist, just pass
        pass 
        
    # 5. Redirect back to the cart page
    return redirect('cart')



@login_required(login_url='login') 
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_get_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for item in cart_items:
            total += item.sub_total()
            quantity += item.quantity
            
    except Cart.DoesNotExist:
        return redirect('home')

    if request.method == 'POST':
        form = OrderForm(request.POST) 
        if form.is_valid():
            data = Order()
            data.user = request.user 
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.city = form.cleaned_data['city']
            data.country = form.cleaned_data['country']
            data.order_total = total
            
            order_number = get_random_string(20).upper()
            data.order_number = order_number
            data.is_ordered = True 
            data.save() 

            for item in cart_items:
    # 3a. Create the OrderItem record
                OrderItem.objects.create(
                order=data,
                product=item.product,
                quantity=item.quantity,
                product_price=item.product.price,
                is_ordered=True
            )
    
    # 3b. 🛑 INVENTORY DEDUCTION LOGIC 🛑
                product = item.product # Get the Product instance
                product.stock -= item.quantity # Reduce stock by purchased quantity
                product.save() # Save the updated stock back to the database
    
    # 4. Clear the cart after order creation (as before)
                cart_items.delete() 
            # Pass order_number to the completion page to display details
            return redirect('order_complete', order_number=order_number) 
    else:
        form = OrderForm()
        
    context = {
        'form': form,
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
    }
    return render(request, 'store/checkout.html', context)


@login_required(login_url='login')
def order_complete(request, order_number):
    """
    Renders a success page and displays the order details using the order_number passed in the URL.
    """
    try:
        order = Order.objects.get(user=request.user, order_number=order_number, is_ordered=True)
        order_items = OrderItem.objects.filter(order=order)
    except Order.DoesNotExist:
        return redirect('home') # Redirect if the order isn't found or doesn't belong to the user
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'store/order_complete.html', context)


@login_required(login_url='login')
def my_orders(request):
    """Retrieves all orders placed by the currently logged-in user."""
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'store/my_orders.html', context)


@login_required(login_url='login')
def order_detail(request, order_number):
    """
    Retrieves and displays a single order and its items, verifying ownership.
    """
    try:
        order = Order.objects.get(user=request.user, order_number=order_number, is_ordered=True)
        order_items = OrderItem.objects.filter(order=order)
        
    except Order.DoesNotExist:
        return redirect('my_orders') 

    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'store/order_detail.html', context)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Save the new user
            user = form.save(commit=False)
            user.email = form.cleaned_data['email'] # Save email
            user.save()
            
            # Optionally log the user in or show success message
            return redirect('login') # Redirect to login page after successful registration
    else:
        form = RegistrationForm()

    context = {'form': form, 'title': 'Register'}
    return render(request, 'registration/register.html', context)


def home(request):
    # Retrieve all available products
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories, # <-- Pass categories to the template
    }
    
    return render(request, 'home.html', context)

def products_by_category(request, category_slug=None):
    # 1. Fetch the selected category object
    current_category = get_object_or_404(Category, slug=category_slug)
    
    # 2. Filter products that belong to this category
    products = Product.objects.filter(category=current_category, is_available=True)
    
    # 3. Fetch all categories again (for the navbar/sidebar)
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': current_category,
    }
    return render(request, 'home.html', context)

def search(request):
    products = None
    keyword = None
    
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            # Use Q objects (OR logic) to search for the keyword in either name OR description
            products = Product.objects.order_by('name').filter(
                Q(description__icontains=keyword) | Q(name__icontains=keyword),
                is_available=True
            )
            
    context = {
        'products': products,
        'keyword': keyword,
    }
    # We will reuse the home.html template to display search results
    return render(request, 'home.html', context)


@login_required(login_url='login')
def my_account(request):
    """Renders the user account dashboard, showing basic links."""
    return render(request, 'store/my_account.html')

@login_required(login_url='login')
def edit_profile(request):
    """Allows the user to view and update their first name, last name, and email."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('my_account')
    else:
        # Load the form with the user's existing data
        form = UserProfileForm(instance=request.user)
        
    context = {'form': form, 'title': 'Edit Profile'}
    return render(request, 'store/edit_profile.html', context)