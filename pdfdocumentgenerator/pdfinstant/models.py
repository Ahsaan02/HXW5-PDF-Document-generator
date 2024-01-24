from django.db import models

# Create your models here.

class User(models.Model):
    useremail = models.EmailField(unique=True)
    userpassword = models.CharField(max_length=100)
    userconfirmpassword = models.CharField(max_length=100)

class Meta:
    db_table ="user"