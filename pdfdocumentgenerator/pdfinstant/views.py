from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

# Create your views here.
# def index(request):
#     return HttpResponse("This is the PDF Instant App.\n<h1>To Goto the second page click <a href='/second'>here</a></h1>")

def index(request):
    page = loader.get_template("pdfinstant/homepage.html")
    return HttpResponse(page.render(request=request))


def second(request):
    page = loader.get_template("pdfinstant/second.html")
    return HttpResponse(page.render(request=request))