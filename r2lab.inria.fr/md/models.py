from django.db import models

# Create your models here.

class Page(models.Model):
    markdown_file = models.CharField("md filename", max_length=128)
