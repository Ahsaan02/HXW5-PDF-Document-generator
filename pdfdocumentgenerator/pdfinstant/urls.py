from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('download_zip/<int:file_id>/', views.download_zip, name='download_zip'),
    path('delete_zip/<int:file_id>/', views.delete_zip, name='delete_zip'),
    path('acprofile/', views.acprofile, name='acprofile'),
    path('send-test-email/', views.send_test_email, name='send_test_email'),

    path(route="index", view=views.index, name="index"),

    path(route="aboutpage", view=views.aboutpage, name="aboutpage"),
    path(route="homepage", view=views.homepage, name="homepage"),
    path(route="generatepdfs", view=views.generatepdfs, name="generatepdfs"),
    path(route="generatepdfsin", view=views.generatepdfsin, name="generatepdfsin"),
    path(route="signin", view=views.signin, name="signin"),
    path(route="signup", view=views.signup, name="signup"),

    path(route="createaccount", view=views.createaccount, name="createaccount"),

    path(route="signinaccount", view=views.signinaccount, name="signinaccount"),

    path(route="signout", view=views.signout, name="signout"),

    # path(route="upload/", view=views.upload_csv, name="upload_csv"),
    path(route="upload-csv", view=views.upload_csv, name="upload_csv"),
    # path(route="cwf_template_1", view=views.cwf_template_1, name="cwf_template_1")
    # path(route="view_function", view=views.view_function, name="view_function"),
    # path(route="template_choices", view=views.template_choices, name="template_choices")
    path('template-choices/', views.template_choices, name='template_choices'),
    path('process-csv/', views.process_csv, name='process_csv'),

    path('acprofile/', views.acprofile, name='acprofile')

]