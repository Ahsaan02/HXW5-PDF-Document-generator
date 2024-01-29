from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required


def index(request):
    page = loader.get_template("pdfinstant/index.html")
    return HttpResponse(page.render(request=request))

def homepage(request):
    page = loader.get_template("pdfinstant/homepage.html")
    return HttpResponse(page.render(request=request))


def aboutpage(request):
    page = loader.get_template("pdfinstant/aboutpage.html")
    return HttpResponse(page.render(request=request))

def generatepdfs(request):
    page = loader.get_template("pdfinstant/generatepdfs.html")
    return HttpResponse(page.render(request=request))

def generatepdfsin(request):
    page = loader.get_template("pdfinstant/generatepdfsin.html")
    return HttpResponse(page.render(request=request))

def signin(request):
    page = loader.get_template("pdfinstant/signin.html")
    return HttpResponse(page.render(request=request))

def signup(request):
    page = loader.get_template("pdfinstant/signup.html")
    return HttpResponse(page.render(request=request))

def createaccount(request):
    error_message_context = {'alert': False, 'message': ''}

    if request.method == 'POST':
        useremail = request.POST.get('useremail')
        userpassword = request.POST.get('userpassword')
        userconfirmpassword = request.POST.get('userconfirmpassword')

        if userpassword != userconfirmpassword:
            error_message_context['alert'] = True
            error_message_context['message'] = 'The Passwords you have entered do not match'
            return render(request, 'pdfinstant/signup.html', error_message_context)

        if User.objects.filter(email=useremail).exists():
            error_message_context['alert'] = True
            error_message_context['message'] = 'The Email you have entered is already registered'
            return render(request, 'pdfinstant/signup.html', error_message_context)

        userpassword_secure = make_password(userpassword)
        create_new_account = User(username=useremail, email=useremail, password=userpassword_secure)
        create_new_account.save()
        return redirect('signin')

    return render(request, 'pdfinstant/signup.html', error_message_context)



def signinaccount(request):
    error_message_context = {'alert': False, 'message': ''}

    if request.method == 'POST':
        useremail = request.POST.get('useremail')
        userpassword = request.POST.get('userpassword')
        user = authenticate(request, username=useremail, password=userpassword)

        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            error_message_context['alert'] = True
            error_message_context['message'] = 'Incorrect sign in details have been provided'
            return render(request, 'pdfinstant/signin.html', error_message_context)

    return render(request, 'pdfinstant/signin.html', error_message_context)

@login_required
def signout(request):
    logout(request)
    return redirect('signin') 
