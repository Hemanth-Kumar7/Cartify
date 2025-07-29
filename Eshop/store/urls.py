from django.urls import path
from .views import Index, Signup, Login, logout, Cart, OrderView, CheckOut, Product, category


urlpatterns = [
    path('', Index.as_view(), name='homepage'),
    path('products/', Product.as_view(), name='products'),
    path('cart/', Cart.as_view(), name='cart'),
    path('signup/', Signup.as_view(), name='signup'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', logout, name='logout'),
    path('checkout/', CheckOut.as_view(), name='checkout'),
    path('orders/',OrderView.as_view(), name='orders'),
    path('category/',category, name='category')
]