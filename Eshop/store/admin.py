from django.contrib import admin
from store.models import Category,Customer,Products,Order

# Register your models here.

# Category
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
admin.site.register(Category,CategoryAdmin)

# Customer
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone', 'email', 'password']
admin.site.register(Customer,CustomerAdmin)

# Products
class ProductsAdmin(admin.ModelAdmin):
    list_display = ['name','price','category','description','image']
admin.site.register(Products,ProductsAdmin)

# Order
class OrderAdmin(admin.ModelAdmin):
    list_display = ['product','customer','quantity','price','address','phone','date','status']
admin.site.register(Order,OrderAdmin)




