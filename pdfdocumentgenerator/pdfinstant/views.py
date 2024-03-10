import csv
from io import StringIO
from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .forms import CSVUploadForm

@csrf_exempt
def upload_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            dataset = csv_file.read().decode('UTF-8')
            processed_csv_data = parse_csv(dataset)
            request.session['csv_data'] = processed_csv_data
            return redirect('generatepdfsin')
    else:
        form = CSVUploadForm()
    return render(request, 'csv_upload.html', {'form': form})

def parse_csv(csv_content):
    csv_data = []
    f = StringIO(csv_content)
    reader = csv.DictReader(f)
    for row in reader:
        cleaned_row = {key.lstrip('\ufeff').replace(' ', '_').strip(): value for key, value in row.items()}
        csv_data.append(cleaned_row)
    return csv_data

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

@login_required
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
