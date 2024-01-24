from django.urls import path

from . import views

urlpatterns = [
    path(route="index", view=views.index, name="index"),

    path(route="aboutpage", view=views.aboutpage, name="aboutpage"),
    path(route="homepage", view=views.homepage, name="homepage"),
    path(route="generatepdfs", view=views.generatepdfs, name="generatepdfs"),
    path(route="generatepdfsin", view=views.generatepdfsin, name="generatepdfsin"),
    path(route="signin", view=views.signin, name="signin"),
    path(route="signup", view=views.signup, name="signup"),

    path(route="createaccount", view=views.createaccount, name="createaccount")
]