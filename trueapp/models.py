from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import PermissionsMixin

# Create your models here.


class UserManager(BaseUserManager):

    def create_user(self, phone, name, password=None, is_active=True, is_staff=False, is_admin=False):
        if not phone:
            raise ValueError('User must have the phone number')
        if not password:
            raise ValueError('User must have the password ')
        user_obj = self.model(
            phone=phone,
            name=name,
        )
        user_obj.set_password(password)
        user_obj.admin = is_admin
        user_obj.active = is_active
        user_obj.staff = is_staff
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, phone, password=None):
        user = self.create_user(
            phone=phone,
            password=password,
            is_staff=True,
        )
        return user

    def create_superuser(self, phone, name, password=None):
        user = self.create_user(
            phone,
            name,
            is_staff=True,
            password=password,
            is_admin=True,
        )
        return user


class User(AbstractBaseUser, PermissionsMixin):
    phone_regex = RegexValidator(regex=r'^[6-9][0-9]{9}$',
                                 message='phone number must be entered in the format: "9999999999')
    phone = models.CharField(validators=[phone_regex], max_length=15, unique=True)
    name = models.CharField(max_length=20)
    email = models.EmailField(max_length=50, null=True, blank=True)
    first_login = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    spam = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self):
        return self.phone

    def get_full_name(self):
        if self.name:
            return self.name
        return self.phone

    def get_short_name(self):
        return self.phone

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin


class Contact(models.Model):
    name = models.CharField(max_length=100, null=False)
    phone = models.CharField(max_length=15, null=False)
    email = models.EmailField(max_length=100, null=True)
    spam = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserContactMapping(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=False)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user) + '->' + str(self.contact)