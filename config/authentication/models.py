from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
import random
import string
from django.conf import settings

# Utility to generate random string
def generate_random():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(12))

# Choices
ROLE_CHOICES = (("Admin", "Admin"), ("User", "User"), ("Vendor", "Vendor"))
VENDOR_STATUS_CHOICES = (
    ("Pending", "Pending"),
    ("Approved", "Approved"),
    ("Rejected", "Rejected"),
)

# User Manager
class AccountManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, name, email, role='User', password=None, phone_number=None, domain=None):
        if not email:
            raise ValueError('User must have an email address')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=name,
            role=role,
            phone_number=phone_number,
            domain=domain,
            is_active=True,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_vendor(self, name, email, role='Vendor', password=None, phone_number=None, domain=None):
        if not email:
            raise ValueError("Vendor must have an email address")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=name,
            role=role,
            phone_number=phone_number,
            domain=domain,
        )
        user.is_active = True
        user.is_staff = False  
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email, password):
        user = self.create_user(
            name=name,
            email=email,
            password=password,
            role='Admin'
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# Domain model
class Domain(models.Model):
    name = models.CharField(max_length=255, unique=True)
    favicon = models.ImageField(upload_to="domain/favicons/", null=True, blank=True)
    logo = models.ImageField(upload_to="domain/logos/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# User model
class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    role = models.CharField(choices=ROLE_CHOICES, max_length=50, db_index=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True, unique=True)
    domain = models.ForeignKey("Domain", on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)



    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = AccountManager()

    def __str__(self):
        return self.email


# Vendor Profile model (one-to-one with User)
class VendorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendor_profile'
    )
    domain = models.ForeignKey(
        'Domain',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    address = models.CharField(max_length=255)
    vendor_status = models.CharField(
        max_length=20,
        choices=VENDOR_STATUS_CHOICES,
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.name} - {self.domain.name if self.domain else 'No Domain'}"
