from django.db import models
from django.contrib.auth.models import User



class Users(models.Model):

    user = models.OneToOneField(User, on_delete = models.CASCADE, null=True)

    username = models.CharField(db_column='username', max_length=255, unique=True)
    password = models.CharField(max_length=255, null=True)

    rollback = models.BooleanField(null=True)

    types = (
        ('QUALITY', 'QUALITY'),
        ('LACHING', 'LACHING'),
        ('TRANSITOR', 'TRANSITOR'),
        ('COMEX', 'COMEX'),
        ('SUPER_COMEX', 'SUPER_COMEX'),
    )

    user_type = models.CharField(max_length=20, choices=types, default=None, null=True)

    def __str__(self):

            return self.username

    class Meta:
        
        managed = True
        
        