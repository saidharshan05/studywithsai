from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cart/', views.cart, name='cart'),
    path('register/', views.register, name='register'), 
    path('search/', views.search, name='search'),# <-- NEW URL
    path('account/', views.my_account, name='my_account'),       # My Account Dashboard
    path('account/edit/', views.edit_profile, name='edit_profile'),
    path('decrease_cart/<slug:product_slug>/', views.decrease_cart, name='decrease_cart'),
    path('remove_cart/<slug:product_slug>/', views.remove_cart, name='remove_cart'),
    path('add_cart/<slug:product_slug>/', views.add_cart, name='add_cart'), 
    path('my_orders/', views.my_orders, name='my_orders'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_complete/<str:order_number>/', views.order_complete, name='order_complete'),
    path('order_detail/<str:order_number>/', views.order_detail, name='order_detail'),
    path('<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:category_slug>/', views.products_by_category, name='products_by_category'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('order_detail/<str:order_number>/', views.order_detail, name='order_detail'),
]