from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ZipFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='zip_files')
    file_name = models.CharField(max_length=255)
    file_content = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)

    