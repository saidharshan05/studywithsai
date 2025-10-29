# store/context_processors.py

from .models import Cart, CartItem
from .views import _get_cart_id # Import the helper function

def cart_counter(request):
    """Injects the total count of items in the current cart into the context."""
    cart_count = 0
    
    if 'cart_id' in request.session:
        try:
            # Use the cart_id from the session to retrieve the cart
            cart_id = _get_cart_id(request)
            cart = Cart.objects.get(cart_id=cart_id)
            
            # Sum the quantity of all active items in that cart
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            for item in cart_items:
                cart_count += item.quantity
                
        except Cart.DoesNotExist:
            cart_count = 0 # If cart is not found, count is zero
            
    # Return the dictionary to be added to the template context
    return dict(cart_count=cart_count)