from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db.models import CharField, BooleanField, JSONField, Model, ForeignKey, DateTimeField, TextField, AutoField, \
    CASCADE, IntegerField
from django.db.models.enums import TextChoices

from apps.manager import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    class Type(TextChoices):
        WORKER = 'worker', 'Worker'
        STAFF_MANAGER = 'staff_manager', 'Staff Manager'
        CONTROLLER = 'controller', 'Controller'
        ADMIN = 'admin', 'Admin'
        ACCOUNTANT = 'accountant', 'Accountant'

    username = None

    jshshir = CharField(max_length=14, unique=True)
    login = CharField(max_length=255, blank=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(null=True, blank=True)
    last_updated_at = DateTimeField(null=True, blank=True)
    first_name = CharField(max_length=255, blank=True)
    last_name = CharField(max_length=255, blank=True)
    middle_name = CharField(max_length=255, blank=True)
    full_name = CharField(max_length=255, blank=True)
    avatar = CharField(max_length=255, blank=True)
    domain = CharField(max_length=255, blank=True)
    birth_date = DateTimeField(null=True, blank=True)
    gender = CharField(max_length=10, blank=True)
    education = CharField(max_length=255, blank=True)
    nationality = CharField(max_length=255, blank=True)
    phone = CharField(max_length=20, blank=True)
    birth_place = CharField(max_length=255, blank=True)
    current_place = CharField(max_length=255, blank=True)
    positions = TextField(default="[]")
    roles = JSONField(default=list)

    objects = CustomUserManager()

    USERNAME_FIELD = 'jshshir'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'


class Company(Model):
    id = AutoField(primary_key=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(null=True, blank=True)
    last_updated_at = DateTimeField(null=True, blank=True)
    type = CharField(max_length=10, blank=True)
    code = CharField(max_length=10, blank=True)

    def __str__(self):
        return f"{self.type} {self.code}"


class CompanyName(Model):
    company = ForeignKey(Company, related_name='names', on_delete=CASCADE)
    data = CharField(max_length=255, blank=True)
    lang = CharField(max_length=10, blank=True)

    def __str__(self):
        return f"{self.company} {self.lang}"


class CompanyKorxona(Model):
    id = IntegerField(primary_key=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField()
    last_updated_at = DateTimeField()
    type = CharField(max_length=50)

    class Meta:
        db_table = 'company_korxona'


class CompanyKorxonaName(Model):
    id = IntegerField(primary_key=True)
    company_korxona = ForeignKey(
        CompanyKorxona,
        on_delete=CASCADE,
        related_name='company_names'
    )
    data = CharField(max_length=255)
    lang = CharField(max_length=10)

    class Meta:
        db_table = 'company_korxona_name'
