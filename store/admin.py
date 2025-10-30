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

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    # Display these fields in a read-only table
    readonly_fields = ('product', 'quantity', 'product_price', 'sub_total')
    extra = 0 # Don't show extra blank rows
    can_delete = False # Prevent accidental deletion of history

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': (('order_number', 'created_at'), 'status', 'order_total', 'is_ordered'),
        }),
        ('Customer Details', {
            'fields': ('user', 'email', 'phone'),
        }),
        ('Shipping Address', {
            'fields': ('first_name', 'last_name', 'address_line_1', 'city', 'country'),
        }),
    )
    
    # Make sure key historical fields are read-only
    readonly_fields = ('order_number', 'order_total', 'created_at', 'user')

def cancel_and_return_stock(self, request, queryset):
    # Iterate through all selected orders
    for order in queryset:
        # Only process orders that are marked as ordered and haven't already been processed
        if order.is_ordered and order.status not in ('Cancelled', 'Refunded'):
            
            # 1. Update Order Status
            order.status = 'Cancelled'
            order.save()
            
            # 2. Return Stock for each item
            order_items = OrderItem.objects.filter(order=order)
            for item in order_items:
                product = item.product
                product.stock += item.quantity # Add the quantity back to stock
                product.save()
                
    # Send a confirmation message back to the administrator
    self.message_user(request, f"{queryset.count()} order(s) successfully marked as Cancelled and stock returned.", level='success')

# 🛑 2. DEFINE THE ACTION NAME AND REGISTER 🛑
cancel_and_return_stock.short_description = "Cancel Order and Return Stock"

# Register the action with the Admin
actions = ['cancel_and_return_stock']