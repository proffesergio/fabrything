from django.shortcuts import render, redirect
from userauthapp.forms import UserRegisterForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from userauthapp.models import User

# User = settings.AUTH_USER_MODEL

# Create your views here.
def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:index') 

    if request.method == "POST":
        form = UserRegisterForm(request.POST or None)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Hey {username}, Your account was created successfully!")
            new_user = authenticate(username=form.cleaned_data['email'], password = form.cleaned_data['password1'])
            login(request, new_user)

            return redirect('core:index')

        print("User registration successful")
    else:
        print("User cannot be registered.")
        form = UserRegisterForm()
    
    
    context = {
        'form': form,

    }
    return render(request, 'userauthapp/sign-up.html', context)

def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, f"Hey, you're already logged in!")
        print("Logged in already!")
        return redirect('core:index')
    
    if request.method == "POST":
        email = request.POST.get('email') #user passed email
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
            #auto login user
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Logged in {email} successfully!")
                return redirect('core:index')
            else:
                messages.warning(request, f"{email} Does Not Exist!")
        except:
            messages.warning(request, f"User with {email} doesn't exist!")

     
    return render(request, "userauthapp/sign-in.html")

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, f"Logged out successfully!")
        return redirect("userauthapp:sign-in")