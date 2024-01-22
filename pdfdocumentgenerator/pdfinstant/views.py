from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

# Create your views here.
# def index(request):
#     return HttpResponse("This is the PDF Instant App.\n<h1>To Goto the second page click <a href='/second'>here</a></h1>")


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

def signin(request):
    page = loader.get_template("pdfinstant/signin.html")
    return HttpResponse(page.render(request=request))

def register(request):
    page = loader.get_template("pdfinstant/register.html")
    return HttpResponse(page.render(request=request))