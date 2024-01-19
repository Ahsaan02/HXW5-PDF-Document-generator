from django.urls import path

from . import views

urlpatterns = [
    # path(route="", view=views.index, name="Home"),
    path(route="second", view=views.second, name="second"),
    path(route="", view=views.index, name="homepage")
]