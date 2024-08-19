from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages

from django.contrib.auth import get_user_model

from django.contrib.auth.forms import AuthenticationForm #add this
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import SignupForm

User = get_user_model()

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('/')  # Redirect to the competition list or another page
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})


def signin(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "You are now logged in!")
            return redirect('/')  # Redirect to the competition list or another page
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/signin.html', {'form': form})

def signout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('signin')  # Redirect to the sign-in page or another page

def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful." )
            return redirect("quizes:main-view")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render (request=request, template_name="accounts/register.html", context={"register_form":form})
    #Login
def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("quizes:main-view")
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="accounts/login.html", context={"login_form":form})

# Signup

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
