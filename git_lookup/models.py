from django.db import models

# Create your models here.


class Packages(models.Model):
    name = models.CharField(max_length=254)
    version = models.CharField(max_length=254, default='')
    count = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now_add=True)


class Repo(models.Model):
    repo_name = models.CharField(max_length=254)
    package = models.ManyToManyField(Packages, null=True)
    owner = models.CharField(max_length=254)

    class Meta:
        unique_together = ('repo_name', 'owner')

