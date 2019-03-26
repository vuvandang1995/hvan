from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.utils import timezone

from django.core.cache import cache 
import datetime
from SmartClass import settings


def get_truong(name):
    try:
        truong = Truong.objects.get(ten=name)
    except:
        return None
    return truong


class MyUserManager(BaseUserManager):
    def create_student(self, email, username, fullname, password, gioi_tinh):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            fullname=fullname,
            gioi_tinh=gioi_tinh,
            # truong_id=get_truong(truong),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_teacher(self, email, username, fullname, password, gioi_tinh):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_student(
            email,
            password=password,
            username=username,
            fullname=fullname,
            gioi_tinh=gioi_tinh,
            # truong=truong,
        )
        user.position = 1
        user.save(using=self._db)
        return user

    def create_admin(self, email, username, fullname, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_student(
            email,
            password=password,
            username=username,
            fullname=fullname,
            # truong=truong,
        )
        user.position = 2
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    fullname = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    noti_noti = models.IntegerField(default=0)
    noti_chat = models.IntegerField(default=0)
    position = models.IntegerField(default=0)
    # 0 : student
    # 1 : teacher
    # 2 : admin
    truong_id = models.ForeignKey('Truong', models.CASCADE, db_column='truong_id', null=True)
    gioi_tinh = models.IntegerField(null=True)

    objects = MyUserManager()

    USERNAME_FIELD = 'username'

    class Meta:
        managed = True
        db_table = 'my_user'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def last_seen(self):
        return cache.get('seen_%s' % self.username)

    def online(self):
        if self.last_seen():
            now = datetime.datetime.now()
            if now > self.last_seen() + datetime.timedelta(
                        seconds=settings.USER_ONLINE_TIMEOUT):
                return False
            else:
                return True
        else:
            return False 


class Truong(models.Model):
    ten = models.CharField(max_length=255)
    mo_ta = models.TextField()

    class Meta:
        managed = True
        db_table = 'truong'


class Lop(models.Model):
    ten = models.CharField(max_length=255)
    truong_id = models.ForeignKey('Truong', models.CASCADE, db_column='truong_id')
    khoa_id = models.ForeignKey('Khoa', models.SET_NULL, null=True, db_column='khoa_id')
    nien_khoa_id = models.ForeignKey('NienKhoa', models.SET_NULL, null=True, db_column='nien_khoa_id')

    class Meta:
        managed = True
        db_table = 'lop'


class ChiTietLop(models.Model):
    lop_id = models.ForeignKey('Lop', models.CASCADE, db_column='lop_id')
    myuser_id = models.ForeignKey('MyUser', models.CASCADE, null=True, db_column="myuser_id")

    class Meta:
        managed = True
        db_table = 'chi_tiet_lop'


class Mon(models.Model):
    ten = models.CharField(max_length=255)
    lop = models.IntegerField()
    mo_ta = models.TextField()

    class Meta:
        managed = True
        db_table = 'mon'


class GiaoVienMon(models.Model):
    myuser_id = models.ForeignKey('MyUser', models.CASCADE, null=True, db_column="myuser_id")
    mon_id = models.ForeignKey('Mon', models.CASCADE, db_column='mon_id')

    class Meta:
        managed = True
        db_table = 'giao_vien_mon'


class De(models.Model):
    ten = models.CharField(max_length=255)
    myuser_id = models.ForeignKey('MyUser', models.CASCADE, null=True, db_column="myuser_id")
    mon_id = models.ForeignKey('Mon', models.CASCADE, db_column='mon_id')
    ngay_tao = models.DateField(default=timezone.now)
    dung_lam = models.CharField(max_length=255)
    cau_truc = models.CharField(max_length=255)
    so_luong = models.IntegerField()
    chi_tiet_so_luong = models.CharField(max_length=255)
    thoi_gian = models.IntegerField(null=True)

    class Meta:
        managed = True
        db_table = 'de'


class ChiTietDe(models.Model):
    de_id = models.ForeignKey('De', models.CASCADE, db_column='de_id')
    cau_hoi_id = models.ForeignKey('CauHoi', models.CASCADE, db_column='cau_hoi_id', null=True)
    cau_hoi_da_id = models.ForeignKey('CauHoiDa', models.CASCADE, db_column='cau_hoi_da_id', null=True)
    diem = models.FloatField()

    class Meta:
        managed = True
        db_table = 'chi_tiet_de'


class CauHoi(models.Model):
    myuser_id = models.ForeignKey('MyUser', models.CASCADE, null=True, db_column="myuser_id")
    mon_id = models.ForeignKey('Mon', models.CASCADE, db_column='mon_id')
    ngay_tao = models.DateField(default=timezone.now)
    noi_dung = models.TextField()
    do_kho = models.IntegerField()# 0: dễ, 1: trung bình, 2: khó
    chu_de = models.CharField(max_length=255)
    dang_cau_hoi = models.CharField(max_length=255)
    dinh_kem = models.FileField(null=True, blank=True, upload_to='question_upload')
    don = models.BooleanField()
    dung_lam = models.CharField(max_length=255)
    so_dap_an_dung = models.IntegerField(default=1)

    class Meta:
        managed = True
        db_table = 'cau_hoi'


class DapAn(models.Model):
    cau_hoi_id = models.ForeignKey('CauHoi', models.CASCADE, db_column='cau_hoi_id')
    mon_id = models.ForeignKey('Mon', models.CASCADE, db_column='mon_id')
    noi_dung = models.TextField()
    dap_an_dung = models.BooleanField()
    dinh_kem = models.FileField(null=True, blank=True, upload_to='question_upload')

    class Meta:
        managed = True
        db_table = 'dap_an'


class BaiLamHocSinh(models.Model):
    de_id = models.ForeignKey('De', models.CASCADE, db_column='de_id')
    cau_hoi_id = models.ForeignKey('CauHoi', models.CASCADE, db_column='cau_hoi_id')
    myuser_id = models.ForeignKey('MyUser', models.CASCADE, null=True, db_column="myuser_id")
    dap_an = models.CharField(max_length=255)

    class Meta:
        managed = True
        db_table = 'bai_lam_hoc_sinh'


class DiemSo(models.Model):
    de_id = models.ForeignKey('De', models.SET_NULL, null=True, db_column='de_id')
    myuser_id = models.ForeignKey('MyUser', models.CASCADE, db_column="myuser_id")
    ngay_lam = models.DateField(default=timezone.now)
    mon_id = models.ForeignKey('Mon', models.CASCADE, db_column='mon_id')
    loai_diem = models.CharField(max_length=255)
    diem_auto = models.FloatField(null=True)
    diem_cham_tay = models.FloatField(default=0)
    bai_lam = models.TextField(default=0)
    da_cham_diem = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'diem_so'


class Nhom(models.Model):
    ten_nhom = models.CharField(max_length=255)
    myuser_id = models.ForeignKey('MyUser', models.CASCADE, null=True, db_column="myuser_id")
    lop_id = models.ForeignKey('Lop', models.CASCADE, null=True, db_column="lopid")


    class Meta:
        managed = True
        db_table = 'nhom'


class ChiTietNhom(models.Model):
    nhom_id = models.ForeignKey('Nhom', models.CASCADE, db_column='nhom_id')
    myuser_id = models.ForeignKey('MyUser', models.CASCADE, null=True, db_column="myuser_id")

    class Meta:
        managed = True
        db_table = 'chi_tiet_nhom'


class Khoa(models.Model):
    ten_khoa = models.CharField(max_length=255)
    mo_ta = models.CharField(max_length=255)

    class Meta:
        managed = True
        db_table = 'khoa'


class NienKhoa(models.Model):
    ten_nien_khoa = models.CharField(max_length=255)
    nam_hoc = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'nien_khoa'


class CauHoiDa(models.Model):
    myuser_id = models.ForeignKey('MyUser', models.CASCADE, null=True, db_column="myuser_id")
    mon_id = models.ForeignKey('Mon', models.CASCADE, db_column='mon_id')
    ngay_tao = models.DateField(default=timezone.now)
    noi_dung = models.TextField()
    do_kho = models.IntegerField()  # 0: dễ, 1: trung bình, 2: khó
    chu_de = models.CharField(max_length=255)
    dang_cau_hoi = models.CharField(max_length=255)
    dinh_kem = models.FileField(null=True, blank=True, upload_to='question_upload')
    so_cau_hoi = models.IntegerField()
    dung_lam = models.CharField(max_length=255)

    class Meta:
        managed = True
        db_table = 'cau_hoi_da'


class ChiTietCauHoiDa(models.Model):
    cau_hoi_id = models.ForeignKey('CauHoi', on_delete=models.CASCADE, db_column='cau_hoi_id')
    cau_hoi_da_id = models.ForeignKey('CauHoiDa', on_delete=models.CASCADE, db_column='cau_hoi_da_id')

    class Meta:
        managed = True
        db_table = 'chi_tiet_cau_hoi_da'
