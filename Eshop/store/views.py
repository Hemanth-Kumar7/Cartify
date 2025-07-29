
from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse
from django.views.generic import View

from .models import Category, Customer, Products, Order #store = package
from django.contrib.auth.hashers import make_password, check_password
import requests
# Create your views here.

class Index(View):
    def get(self, request):

        try:
            response = requests.get('https://fakestoreapi.com/products')
            products = response.json()

        except requests.exceptions.RequestException as e:   # When Connection is not proper
            print("API ERROR:", e)  # Log to console for debugging
            error_message = "⚠️ Oops! We couldn't load products. Please check your internet connection."
            return render(request,'store/notfound.html',{'error_message':error_message})
            #return HttpResponse("<div><h3>⚠️ Oops! We couldn't load products. Please check your internet connection.</h3></div>")


        print("Index API Executed")
        for item in products:
            category_obj, created = Category.objects.get_or_create(
                name=item['category']
            )
            Products.objects.get_or_create(
                category = category_obj,
                name = item['title'],
                description = item['description'],
                image = item['image'],
                price = item['price']
            )

        cart = request.session.get('cart', {})  #If session is availabe use it,otherwise create empty session
        cart_item_count = sum(cart.values())
        print(cart)

        '''cart = request.session.get('cart')
        if not cart:
            request.session['cart'] = {} '''

        categories = Category.get_all_categories()  # Get all objects in categories table
        print('Categories :',categories)

        categoryID = request.GET.get('category')   # Category=? Getting from template
        if categoryID:
            products = Products.get_all_products_by_categoryid(categoryID)  # Display products related to that category_id
        else:
            products = Products.get_all_products()

        data = {}
        data['products'] = products  # dictobj['key']=val
        data['categories'] = categories
        data['cart_item_count'] = cart_item_count

        print('you are : ', request.session.get('email'))
        return render(request, 'store/index.html', data)

    #When a user clicks “Add to Cart”, the product is added to the session cart, and you want to
    # display the cart item count( or value) next to the Cart link in base.html.

    def post(self, request):
        print("Index POST executed")
        # Retrieve product_id from post request and whether it's a removal
        product = request.POST.get('product') # when we click on add-to-cart, than we get product_id
        print('Product_ID :',product)  # 2
        remove = request.POST.get('remove')
        # Get or initialize the cart
        cart = request.session.get('cart',{}) # getting cart from session
        if cart:
            quantity = cart.get(product) #cart is dictobj, cart[product] = 1
            if quantity:    # quantity = 1 True
                if remove:
                    if quantity <= 1:
                        cart.pop(product)
                    else:
                        cart[product] = quantity-1
                else:
                    cart[product] = quantity+1
            else:
                cart[product] = 1 #product = product.id
        else:
            cart = {}
            cart[product] = 1  #than product.id = 1, is stored in empty cart

        request.session['cart'] = cart  #adding cart_obj to session
        print('cart', request.session['cart'])
        return redirect('homepage')

def category(request):
    categories_list = Category.get_all_categories()  # objects in categories table

    category_name = request.GET.get('category')
    print('category_name :',category_name)

    # Filter products by category name
    products = Products.objects.filter(category__name__iexact=category_name)

    return render(request,'store/products.html',{'categories_list':categories_list,'products': products})



# Login class
class Login(View):
    return_url = None

    def get(self, request):
        print('Login Get Executed')
        Login.return_url = request.GET.get('return_url')
        return render(request, 'store/login.html')

    def post(self, request):
        print('Login Post Executed')
        email = request.POST.get('email') # get email
        password = request.POST.get('password')  # get password
        #customer = Customer.get_customer_by_email(email) #get customer using email
        customer = Customer.get_customer_by_email(email)  #customer = obj
        error_message = None

        if customer:    #customer = True or False
            print('Passowrd :',customer.password)
            print('Customer ID :',customer.id)
            flag = check_password(password, customer.password) #check_password(raw_password, hashed_password)
            print(flag)     # False or True
            if flag:
                # Successful login: store customer ID in session
                request.session['customer'] = customer.id # customer.id = id in customer

                if Login.return_url:
                    return HttpResponseRedirect(Login.return_url)
                else:
                    Login.return_url = None
                    return redirect('homepage')  #if password matches than redirect to index.html
            else:
                error_message = 'Invalid credentials !!'
        else:
            error_message = 'Invalid credentials !!'

        print(email, password)
        return render(request, 'store/login.html', {'error': error_message})


def logout(request):
    request.session.clear()
    return render(request,'store/logout.html')


# Signup class
class Signup(View):
    def get(self, request):
        print('Signup Get executed')
        return render(request, 'store/signup.html')

    def post(self, request):    #post method retrieves data from POST request
        print('Signup Post executed')
        postData = request.POST
        first_name = postData.get('firstname')
        last_name = postData.get('lastname')
        phone = postData.get('phone')
        email = postData.get('email')
        #password = make_password(postData.get('password'))
        password = make_password(postData.get('password'))
        # validation
        '''value = {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'email': email
        }
        error_message = None '''
        #Adding user details to customer model class
        customer = Customer(first_name=first_name,
                            last_name=last_name,
                            phone=phone,
                            email=email,
                            password=password)

        if customer.isExists(): #retrieves email & check whether user exists or not customer table
            return render(request, 'store/signup.html', {'error': "Email address already registered"})
        customer.register()
        return redirect('login')

    '''error_message = self.validate_Customer(customer)
        print("Exists?", customer.isExists())

        if not error_message:
                print(first_name, last_name, phone, email, password)
                # hashes the plain text password before saving it.
                customer.password = make_password(customer.password)
                customer.register()     #register()
                print("Customer saved!")
                return redirect('homepage')
        else:
            data = {
                'error': error_message,
                'values': value
            }
            return render(request, 'store/signup.html', data)

    def validate_Customer(self, customer):
        error_message = None
        if (not customer.first_name): #customer.first_name not contains
            error_message = "Please Enter your First Name !!"
        elif len(customer.first_name) < 3:
            error_message = 'First Name must be 3 char long or more'
        elif not customer.last_name:
            error_message = 'Please Enter your Last Name'
        elif len(customer.last_name) < 3:
            error_message = 'Last Name must be 3 char long or more'
        elif not customer.phone:
            error_message = 'Enter your Phone Number'
        elif len(customer.phone) < 10:
            error_message = 'Phone Number must be 10 char Long'
        elif len(customer.password) < 5:
            error_message = 'Password must be 5 char long'
        elif len(customer.email) < 5:
            error_message = 'Email must be 5 char long'
        elif customer.isExists():
            error_message = 'Email Address Already Registered..'
        # saving

        return error_message '''

# Cart class
class Cart(View):
    def get(self, request):
        print('Cart Get Executed')

        cart = request.session.get('cart')
        cart_item_count = sum(cart.values())
        product_ids = list(cart.keys())
        products = Products.get_products_by_id(product_ids)  # keys = products.id
        print('products id: ',products) # products = dict_obj
        # products = particular products_obj

        for product in products:  # each product in product_obj
            print(cart.get(str(product.id)))  # product contains id
        return render(request, 'store/cart.html',{'products':products,'cart': cart,'cart_item_count':cart_item_count})

    def post(self,request):
        product = request.POST.get('product')
        remove = request.POST.get('remove')
        # Get or initialize the cart
        cart = request.session.get('cart')  # getting cart from session
        print("Cart_det :" ,cart)
        if cart:
            quantity = cart.get(product)  # cart is dictobj, cart[product] = 1
            print(quantity)
            if quantity:  # quantity = 1 True
                if remove:
                    if quantity <= 1:
                        cart.pop(product)
                    else:
                        cart[product] = quantity - 1
                else:
                    cart[product] = quantity + 1

            else:
                cart[product] = 1  # product = product.id

            request.session['cart'] = cart  # adding cart_obj to session
            print('cart', request.session['cart'])
            return redirect('homepage')


# CheckoutView class
class CheckOut(View):
    def get(self,request):
        print('Buy Get Executed')
        return render(request,'store/checkout.html')

    def post(self, request):
        print('Buy Post Executed')
        address = request.POST.get('address')
        print('Address :', address)
        phone = request.POST.get('phone')
        print('Phone :', phone)
        customer_id = request.session.get('customer')  # customer contains 'customer id'
        print('customer_id:',customer_id)
        cart = request.session.get('cart')  # customer cart

        #products = Products.get_products_by_id(list(cart.keys())) #keys = products.id
        products = Products.objects.filter(id__in = list(cart.keys()))
        # products = particular product_obj
        print(address, phone, customer_id, cart, products)

        customer_obj = Customer.objects.get(id=customer_id)
        print('Customer_Obj :', customer_obj)

        for product in products:    # product in product_obj
            print(product.id)
            print('Order Placing Executing')
            print(cart.get(str(product.id)))    # product contains id, img.. etc
            order = Order(
                          customer=customer_obj,
                          product=product, #product = particular product_obj
                          price=product.price,
                          address=address,
                          phone=phone,
                          quantity=cart.get(str(product.id)))
            order.save()
            print('Order Placed Successfully')
        request.session['cart'] = {}
        return redirect('/orders')


# OrderView
class OrderView(View):

    def get(self, request):
        print('Order Get Executed')
        customer_id = request.session.get('customer')  # customer = customer_id
        orders = Order.get_orders_by_customer(customer_id)
        print(' Query_Set :', orders)
        #return redirect('orders.html')
        return render(request, 'store/orders.html', {'orders': orders})

class Product(View):
    def get(self, request):
        products = Products.objects.all()
        return render(request,'store/products.html',{'products':products})

    def post(self, request):
        print("Index POST executed")
        # Retrieve product_id from post request and whether it's a removal
        product = request.POST.get('product') # when we click on add-to-cart, than we get product_id
        print(product)  # 2
        remove = request.POST.get('remove')
        # Get or initialize the cart
        cart = request.session.get('cart') # getting cart from session
        if cart:
            quantity = cart.get(product) #cart is dictobj, cart[product] = 1
            if quantity:    # quantity = 1 True
                if remove:
                    if quantity <= 1:
                        cart.pop(product)
                    else:
                        cart[product] = quantity-1
                else:
                    cart[product] = quantity+1

            else:
                cart[product] = 1 #product = product.id
        else:
            cart = {}
            cart[product] = 1  #than product.id = 1 is stored in empty cart

        request.session['cart'] = cart  #adding cart_obj to session
        print('cart', request.session['cart'])
        return redirect('homepage')

