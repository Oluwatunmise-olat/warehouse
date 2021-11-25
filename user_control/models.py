from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class CustomManager(BaseUserManager):
    def create_user(self, email, password, *args, **kwargs):
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=kwargs["first_name"],
            last_name=kwargs["last_name"]
        )
        user.set_password(password)
        user.is_superuser, user.is_admin, user.is_worker, user.role, user.is_staff = (
            kwargs["is_superuser"], kwargs["is_admin"], kwargs["is_worker"], kwargs["role"], kwargs["is_staff"]
        )
        user.save()
        return user

    def create_adminuser(self, email, password, **extrafields):
        extrafields.setdefault('is_admin', True)
        extrafields.setdefault('is_superuser', True)
        extrafields.setdefault('is_staff', True)
        extrafields.setdefault('is_worker', False)
        extrafields.setdefault('role', 'Admin')
        return self.create_user(email, password, **extrafields)

    def create_superuser(self, email, password, **extrafields):
        extrafields.setdefault('is_admin', True)
        extrafields.setdefault('is_superuser', True)
        extrafields.setdefault('is_staff', True)
        extrafields.setdefault('is_worker', False)
        extrafields.setdefault('role', 'Admin')
        return self.create_user(email, password, **extrafields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE = (('ADMIN', 'Admin'), ('WORKER', 'Worker'))
    email = models.EmailField(help_text="email address", unique=True)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    role = models.CharField(max_length=10, choices=ROLE, default=None)
    is_admin = models.BooleanField(default=False)
    is_worker = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomManager()

    class Meta:
        ordering = ('-created_at', )
        verbose_name_plural = "CustomUser"

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self) -> str:
        fullname = self.get_full_name()
        return f'{self.role} {fullname}'
