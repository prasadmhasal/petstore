from django.shortcuts import render , HttpResponseRedirect , HttpResponse
from .models import Product , Cart ,Address , Order
from .forms import ProductForm
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate ,login ,logout
from django.core.mail import send_mail 
from django.conf import settings
from datetime import date , timedelta , datetime
import uuid
import razorpay
from django.views.decorators.csrf import csrf_exempt



# Create your views here.
def Email (request):
    send_mail('welcome', 'Nothing.. special ',settings.EMAIL_HOST_USER,['manojraulo58@gmail.com'])
    return  HttpResponse('Mail Sending ')

def Index(request):
    if request.user.is_superuser and request.user.is_authenticated:
        if request.method=="POST":
            pass
            fm = ProductForm(request.POST,request.FILES)
            if fm.is_valid():
                fm.save()
                return HttpResponseRedirect ('/display/')
                fm = ProductForm()
        else:
            fm = ProductForm()
        return render(request,'admin/index1.html')
    else:
        return HttpResponseRedirect('/display/')


def Display(request):
    data = Product.objects.all()
    print(data)
    return render(request,'admin/display.html',{'data':data})


def Delete(request ,id):
    if request.method == "POST":
        os = Product.objects.get(pk=id)
        os.delete()
        messages.success(request,"Data Delete successfully")
        return HttpResponseRedirect('/display/')
    

def Update(request,id):
    if request.method == 'POST':
        os = Product.objects.get(pk=id)
        fm = ProductForm (request.POST , request.FILES , instance = os)
        if fm.is_valid():
            fm.save()
            messages.success(request,"Data Update successfully")
            return HttpResponseRedirect('/display/')
    else:
        os = Product.objects.get(pk=id)
        print(os)
        fm = ProductForm(instance = os)
    return render(request,'admin/update.html',{'Updateform':fm})


def UserBase(request):
    if request.user.is_authenticated:
        count = Cart.objects.filter(user_id=request.user).count()
        print(count)
        return render(request,'user/base.html' ,{'count':count})
    else:
        return HttpResponseRedirect('/')

def UserIndex(request):
    if request.user.is_authenticated:
        count = Cart.objects.filter(user_id=request.user).count()
        order1 = Order.objects.all()
        data = Product.objects.all()
        date1=date.today()
        days = timedelta(days=7)
        delivery_date=(date1+days)
        order_productid = Order.objects.all().values_list('product_id',flat=True)
        return render(request,'user/index.html',{'data':data ,'count':count,'date':delivery_date ,'order1':order1 ,'opid':order_productid})
    else:
        return HttpResponseRedirect('/')
    

def AddToCart(request):
    if request.user.is_authenticated:
        if request.method=="POST":
            cid = request.POST.get('cid')
            filter1 = Cart.objects.filter(user_id = request.user).values_list('Product_id',flat=True)
            print(filter1)
            if int(cid) not in filter1:
                 Cart.objects.create(Product_id=cid ,user=request.user)
                 return HttpResponseRedirect('/cart/')
            else:
                messages.success(request,'This Product Is Already In Cart')
        cid = Cart.objects.filter(user_id=request.user).values_list('Product_id',flat=True)
        cartdata = Product.objects.filter(id__in=cid)
        amount = Product.objects.filter(id__in=cid).values_list('price',flat=True)
        count = Cart.objects.filter(user_id=request.user).count()
        print(amount)
        amt=0
        for i in amount:
            amt=amt+i
        return render(request,'user/cart.html',{'cdata':cartdata,'amt':amt ,'count':count}) 
    else:
        return HttpResponseRedirect('/')


def RemoveCart(request,id):  
    if request.user.is_authenticated:
        if request.method == 'POST':
            Cart.objects.filter(Product_id=id).delete()
            return HttpResponseRedirect('/cart/')
    else:
        return HttpResponseRedirect('/')

def ComponentSearch(request):
    if request.user.is_authenticated:
        count = Cart.objects.filter(user_id=request.user).count()
        try:
            if request.method == "POST":
                search = request.POST.get('search')
                sdata = Product.objects.filter(Q(category=search) | Q(pname=search) | Q(desc__contains=search) | Q(price__contains=search))
                print(sdata)
            return render(request,'user/search.html',{'sdata':sdata , 'count':count})
        except:
            return HttpResponseRedirect('/userindex/')
    else:
        return HttpResponseRedirect('/')


def Details(request,id):
    if request.user.is_authenticated:
        count = Cart.objects.filter(user_id=request.user).count()
        data_detail = Product.objects.filter(pk=id)
        print(id)
        return render(request,'user/details.html',{'data':data_detail,'count':count})
    else:
        return HttpResponseRedirect('/')



def Signup(request):
    if request.method == "POST":
        uname=request.POST.get('uname')
        email=request.POST.get('email')
        pass1=request.POST.get('pass')
        print(uname,email,pass1)
        User.objects.create_user(uname,email,pass1)

        subject = f'Welcome to petstore {uname}'
        message = f""" 
                  Dear {uname},

                  You have suceesfully register to The_Pet_Store 
                  with {email} this email ,

                  Thank You for selecting The_Pet_Store

                  Happy Shopping..Keep Shopping..Stay In Touch 

                  'Note : please do not replay to this email because it is auto generted'
                   
                 """
        mail_form = settings.EMAIL_HOST_USER
        mail_to = email
        send_mail(subject,message,mail_form,[mail_to])

        messages.success(request,"Signup Successfully.....")
    return render(request,'user/signup.html')


def Login(request):
    if request.method == "POST":
        username = request.POST.get('uname')
        password = request.POST.get('pass')
        user = authenticate(request,username=username, password=password )
        if user is not None:
            login(request,user)
            return HttpResponseRedirect('/userindex/')
    return render(request,'user/login.html')


def Logout(request):
    logout(request)
    return HttpResponseRedirect("/")


def address(request,id):
    if request.user.is_authenticated:
        order_id  = Order.objects.all().values_list('product_id',flat=True)
        if id not in list(order_id):
            if request.method == 'POST':
                cname = request.POST.get('cname')
                flat = request.POST.get('flat')
                landmark = request.POST.get('landmark')
                city = request.POST.get('city')
                state = request.POST.get('state')
                pincode = request.POST.get('pincode')
                contact = request.POST.get('contact')
                acontact = request.POST.get('acontact')
                Address.objects.create(user=request.user,name=cname,flat=flat,landmark=landmark,city=city,state=state,pincode=pincode,contact=contact,contactA=acontact)
                
                # here we are fetaching data form address table 
            product_id = id 
            data = Address.objects.filter(user_id=request.user)
            return render(request,'user/address.html' ,{'adata':data,'product_id':product_id})
        else:
            messages.success(request,"This Product is Already sold ")
            return HttpResponseRedirect('/userindex/')
    else:
        return HttpResponseRedirect('/')



def Pre_order(request,aid,pid):
    address_data = Address.objects.filter(pk=aid)
    product_data = Product.objects.filter(pk=pid)
    date1=date.today()
    days = timedelta(days=5)
    delivery_date=(date1+days)
    # print(address_data,product_data)
    return render(request,'user/pre_order.html',{'adata':address_data,'pdata':product_data,'date':delivery_date,'aid':aid,'pid':pid})

@csrf_exempt
def Order_Confirm(request,aid,pid):
    try:
        product_id = pid
        address_id = aid 
        date1 = datetime.now()
        datef=date1.strftime('%Y%m%d%H%M%S')
        unique_id = (str(uuid.uuid4().hex)[:6:])
        order_id=f'PS{datef}-{unique_id}'
        Order.objects.create(user=request.user,product_id=product_id,order_id=order_id)
        return render(request,'user/order_confirm.html')
    except:
        return render(request,'user/confirmation.html')


def Payment(request,aid,pid):
    client = razorpay.Client(auth=("rzp_test_VPel75yVZnzpbD", "SYoHmR95xmbUb7BNW1SSLzBc"))
    product_amt= Product.objects.filter(id=pid).values_list('price',flat=True)
    print(product_amt[0])
    amount = product_amt[0]
    data = { "amount": amount, "currency": "INR", "receipt": "order_rcptid_11" }
    payment = client.order.create(data=data)
    context = {}
    context['amt']= amount*100
    context['aid'] = aid
    context['pid'] = pid
    
    return render(request,'user/pay.html',context)



def AdminSignUp(request):
    if request.method=="POST":
        uname=request.POST.get('uname')
        email=request.POST.get('email')
        password=request.POST.get('pass')
        user=User.objects.create_user(uname,email,password)
        user.is_staff=True
        user.is_superuser=True
        user.save()
    return render(request,"admin/adminsignup.html")


def AdminLogin(request):
    if request.method == "POST":
        username = request.POST.get('uname')
        password = request.POST.get('pass')
        user = authenticate(request,username=username, password=password )
        if user is not None:
            login(request,user)
            return HttpResponseRedirect('/index/')
    return render(request,'admin/adminlogin.html')

