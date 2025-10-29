from django.contrib import admin
from .models import Product, Cart, CartItem, Product, Cart, CartItem, Order, OrderItem, Category

# Customizing how the Product model appears in the Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Which fields to display on the main list page
    list_display = ['name', 'price', 'stock', 'is_available', 'created_at']
    
    # Fields that can be filtered in the sidebar
    list_filter = ['is_available', 'created_at', 'updated_at']
    
    # Fields that can be searched
    search_fields = ['name', 'description']
    
    # Automatically populate the 'slug' field based on the 'name' field
    prepopulated_fields = {'slug': ('name',)}
    
    # Fields to group/display when editing a single product
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'image')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock', 'is_available')
        }),
    )

# --- NEW ADMIN REGISTRATION ---

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'date_added',)
    search_fields = ('cart_id',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity', 'is_active')
    list_editable = ('is_active',) # Allows editing this field right from the list view

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # Only use fields that exist on the Category model
    list_display = ('name', 'slug') 
    prepopulated_fields = {'slug': ('name',)}