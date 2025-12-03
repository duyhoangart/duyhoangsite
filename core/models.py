from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

class User(AbstractUser):
    """Mở rộng User model để phân quyền"""
    USER_TYPE_CHOICES = (
        ('artist', 'Artist'),
        ('customer', 'Customer'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class ArtistProfile(models.Model):
    """Thông tin cá nhân của artist"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='artist_profile')
    bio = models.TextField(blank=True, help_text="Giới thiệu về bản thân")
    avatar = models.ImageField(upload_to='artist/avatar/', blank=True)
    bank_name = models.CharField(max_length=100, default="")
    bank_account_number = models.CharField(max_length=50, default="")
    bank_account_name = models.CharField(max_length=100, default="")
    bank_qr_code = models.ImageField(upload_to='artist/qr/', blank=True, help_text="Mã QR thanh toán")
    
    def __str__(self):
        return f"Profile của {self.user.username}"


class ServiceType(models.Model):
    """Loại dịch vụ commission"""
    name = models.CharField(max_length=100, help_text="VD: Sketch Gacha Scan")
    description = models.TextField(help_text="Mô tả chi tiết")
    price = models.DecimalField(max_digits=10, decimal_places=0, help_text="Giá (VNĐ)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.price:,.0f}đ"


class Sample(models.Model):
    """Mẫu tranh của artist"""
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, related_name='samples')
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='samples/')
    description = models.TextField(blank=True)
    display_order = models.IntegerField(default=0, help_text="Thứ tự hiển thị")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['display_order', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.service_type.name})"


class TermsOfService(models.Model):
    """Điều khoản dịch vụ"""
    content = models.TextField(help_text="Nội dung TOS")
    version = models.CharField(max_length=20, unique=True, help_text="VD: v1.0")
    is_active = models.BooleanField(default=False, help_text="TOS đang sử dụng")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def save(self, *args, **kwargs):
        if self.is_active:
            # Chỉ có 1 TOS active
            TermsOfService.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"TOS {self.version}"


class Order(models.Model):
    """Đơn hàng commission"""
    STATUS_CHOICES = (
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt - Chờ thanh toán'),
        ('paid', 'Đã thanh toán - Chờ vẽ'),
        ('in_progress', 'Đang thực hiện'),
        ('completed', 'Đã hoàn thành'),
        ('cancelled', 'Đã hủy'),
    )
    
    order_id = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT)
    
    # Thông tin yêu cầu
    description = models.TextField(help_text="Mô tả chi tiết yêu cầu")
    brief_file = models.FileField(upload_to='briefs/', blank=True, help_text="File brief/reference")
    
    # Trạng thái và giá
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    price = models.DecimalField(max_digits=10, decimal_places=0, help_text="Giá cuối cùng")
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Ghi chú của admin
    admin_note = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            # Tạo OrderID: DH-YYYYMMDD-XXXXX
            today = timezone.now().strftime('%Y%m%d')
            count = Order.objects.filter(
                created_at__date=timezone.now().date()
            ).count() + 1
            self.order_id = f"DH-{today}-{count:05d}"
        super().save(*args, **kwargs)
    
    def get_short_order_id(self):
        """Trả về mã ngắn để chuyển khoản: DH00023"""
        parts = self.order_id.split('-')
        if len(parts) == 3:
            return f"DH{parts[2]}"
        return self.order_id
    
    def __str__(self):
        return f"{self.order_id} - {self.customer.username}"


class OrderProgress(models.Model):
    """Cập nhật tiến độ đơn hàng"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='progress_updates')
    image = models.ImageField(upload_to='progress/', help_text="Ảnh tiến độ")
    note = models.TextField(blank=True, help_text="Ghi chú về tiến độ")
    is_final = models.BooleanField(default=False, help_text="Đánh dấu là bản hoàn thiện cuối cùng")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Progress {self.order.order_id} - {self.created_at.strftime('%d/%m/%Y')}"


class Payment(models.Model):
    """Thanh toán đơn hàng"""
    STATUS_CHOICES = (
        ('pending', 'Chờ xác thực'),
        ('verified', 'Đã xác thực'),
        ('rejected', 'Bị từ chối'),
    )
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=0, help_text="Số tiền đã chuyển")
    transaction_id = models.CharField(max_length=100, blank=True, help_text="Mã giao dịch")
    proof_image = models.ImageField(upload_to='payments/', help_text="Ảnh chứng từ")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    admin_note = models.TextField(blank=True, help_text="Ghi chú của admin")
    
    def __str__(self):
        return f"Payment {self.order.order_id} - {self.amount:,.0f}đ"


class Message(models.Model):
    """Tin nhắn giữa artist và khách hàng"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    image = models.ImageField(upload_to='messages/', blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"