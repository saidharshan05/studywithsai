from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    # Basic Product Information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Inventory/Status
    is_available = models.BooleanField(default=True)
    stock = models.IntegerField(default=1)
    
    # Identification for URLs/Links (e.g., mysite.com/product/the-book-slug)
    slug = models.SlugField(max_length=200, unique=True)
    
    # Visuals (Requires Pillow package for image handling)
    image = models.ImageField(upload_to='product_images', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Define the default order of products when retrieved from the database
        ordering = ('name',)
        # Name displayed in the Django Admin
        verbose_name_plural = 'Products'

    def __str__(self):
        # This is what will be displayed when referencing a Product object (e.g., in the admin)
        return self.name
    
    # --- CART MODELS ---

class Cart(models.Model):
    # A unique identifier for the cart, used for session-based carts (anonymous users)
    cart_id = models.CharField(max_length=250, blank=True)
    # The date/time the cart was created
    date_added = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'Cart'
        ordering = ['date_added']
        verbose_name_plural = 'Carts'

    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    # Links the item to a specific Cart
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    # Links the item to a specific Product
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # The quantity of this product in the cart
    quantity = models.IntegerField()
    # To check if this item is currently active in the cart
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'CartItem'
        verbose_name_plural = 'Cart Items'

    def sub_total(self):
        """Calculates the subtotal for this specific cart item (price * quantity)."""
        return self.product.price * self.quantity

    def __str__(self):
        return self.product.name


class Order(models.Model):
    # Links the order to a registered user
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Unique order identifier
    order_number = models.CharField(max_length=20, unique=True)
    
    # Billing and Shipping details
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    
    # Financial and Status
    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, default='New')
    is_ordered = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # store/models.py (Inside class Order(models.Model):)

    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'), 
        ('Refunded', 'Refunded'),   
    )
    # ...

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    # Links the item to a specific Order
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def sub_total(self):
        price = self.product_price if self.product_price is not None else 0
        qty = self.quantity if self.quantity is not None else 0
        
        return price * qty

    def __str__(self):
        return self.product.name
    

class Category(models.Model):

    ccategory = models.ForeignKey(Product, on_delete=models.CASCADE) 
    
    # Basic Product Information (Existing fields)
    name = models.CharField(max_length=200)    
    # A URL-friendly identifier for category pages (e.g., mysite.com/categories/books)
    slug = models.SlugField(max_length=100, unique=True)
    
    # Optional: A short description for the category page
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        # Categories will be ordered alphabetically by name
        ordering = ('name',)

    def __str__(self):
        return self.name
    
