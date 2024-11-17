from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(
            self, email, display_name, username, password=None, **extra_fields
            ):
        
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')
        if not display_name:
            raise ValueError('Users must have a display name')
        
        email = self.normalize_email(email)

        user = self.model(
            email=email, display_name=display_name, username=username, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, display_name, username, password=None, **extra_fields):

        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get("is_staff") is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get("is_admin") is not True:
            raise ValueError('Superuser must have is_admin=True.')
        
        return self.create_user(email, display_name, username, password, **extra_fields)
    
class User(AbstractBaseUser):
    email = models.EmailField(max_length=254, unique=True)
    display_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    avatar = models.ImageField(upload_to='avatars', blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    date_joined = models.DateTimeField(default=timezone.now)
    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "display_name"]

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        return self.is_superuser