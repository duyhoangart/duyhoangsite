from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *

class CustomerRegistrationForm(UserCreationForm):
    """Form đăng ký khách hàng"""
    email = forms.EmailField(required=True, label="Email")
    phone = forms.CharField(max_length=15, required=False, label="Số điện thoại")
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Tên đăng nhập"
        self.fields['password1'].label = "Mật khẩu"
        self.fields['password2'].label = "Xác nhận mật khẩu"
        
        # Thêm class CSS
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class OrderForm(forms.ModelForm):
    """Form tạo đơn hàng"""
    class Meta:
        model = Order
        fields = ('service_type', 'description', 'brief_file')
        labels = {
            'service_type': 'Loại dịch vụ',
            'description': 'Mô tả chi tiết yêu cầu',
            'brief_file': 'File brief/reference (tùy chọn)',
        }
        widgets = {
            'service_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Vui lòng mô tả chi tiết yêu cầu của bạn...'
            }),
            'brief_file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class PaymentForm(forms.ModelForm):
    """Form upload chứng từ thanh toán"""
    class Meta:
        model = Payment
        fields = ('amount', 'transaction_id', 'proof_image')
        labels = {
            'amount': 'Số tiền đã chuyển (VNĐ)',
            'transaction_id': 'Mã giao dịch (tùy chọn)',
            'proof_image': 'Ảnh chứng từ chuyển khoản',
        }
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'VD: 90000'
            }),
            'transaction_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mã giao dịch (nếu có)'
            }),
            'proof_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }


class ArtistProfileForm(forms.ModelForm):
    """Form cập nhật thông tin artist"""
    class Meta:
        model = ArtistProfile
        fields = ('bio', 'avatar', 'bank_name', 'bank_account_number', 'bank_account_name', 'bank_qr_code')
        labels = {
            'bio': 'Giới thiệu về bản thân',
            'avatar': 'Ảnh đại diện',
            'bank_name': 'Tên ngân hàng',
            'bank_account_number': 'Số tài khoản',
            'bank_account_name': 'Chủ tài khoản',
            'bank_qr_code': 'Mã QR thanh toán',
        }
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: Vietcombank'}),
            'bank_account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: 1234567890'}),
            'bank_account_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: NGUYEN VAN A'}),
            'bank_qr_code': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }


class ServiceTypeForm(forms.ModelForm):
    """Form quản lý loại dịch vụ"""
    class Meta:
        model = ServiceType
        fields = ('name', 'description', 'price', 'is_active')
        labels = {
            'name': 'Tên dịch vụ',
            'description': 'Mô tả',
            'price': 'Giá (VNĐ)',
            'is_active': 'Đang hoạt động',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: Sketch Gacha Scan'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'VD: 90000'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SampleForm(forms.ModelForm):
    """Form thêm sample"""
    class Meta:
        model = Sample
        fields = ('service_type', 'title', 'image', 'description', 'display_order')
        labels = {
            'service_type': 'Loại dịch vụ',
            'title': 'Tiêu đề',
            'image': 'Ảnh sample',
            'description': 'Mô tả',
            'display_order': 'Thứ tự hiển thị',
        }
        widgets = {
            'service_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
        }


class TermsOfServiceForm(forms.ModelForm):
    """Form quản lý TOS"""
    class Meta:
        model = TermsOfService
        fields = ('content', 'version', 'is_active')
        labels = {
            'content': 'Nội dung điều khoản',
            'version': 'Phiên bản',
            'is_active': 'Kích hoạt',
        }
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 15}),
            'version': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: v1.0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class OrderApprovalForm(forms.Form):
    """Form duyệt đơn hàng"""
    approve = forms.BooleanField(required=False, label="Duyệt đơn")
    price = forms.DecimalField(
        max_digits=10, 
        decimal_places=0,
        label="Giá cuối cùng (VNĐ)",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    admin_note = forms.CharField(
        required=False,
        label="Ghi chú",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )


class OrderStatusForm(forms.Form):
    """Form cập nhật trạng thái đơn hàng"""
    STATUS_CHOICES = (
        ('in_progress', 'Đang thực hiện'),
        ('completed', 'Đã hoàn thành'),
        ('cancelled', 'Hủy đơn'),
    )
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        label="Trạng thái",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    admin_note = forms.CharField(
        required=False,
        label="Ghi chú",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )


class OrderProgressForm(forms.ModelForm):
    """Form thêm tiến độ"""
    class Meta:
        model = OrderProgress
        fields = ('image', 'note', 'is_final')
        labels = {
            'image': 'Ảnh tiến độ',
            'note': 'Ghi chú',
            'is_final': 'Đánh dấu là bản hoàn thiện cuối cùng',
        }
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_final': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PaymentVerificationForm(forms.Form):
    """Form xác thực thanh toán"""
    verify = forms.BooleanField(required=False, label="Xác thực thanh toán")
    reject = forms.BooleanField(required=False, label="Từ chối thanh toán")
    admin_note = forms.CharField(
        required=False,
        label="Ghi chú",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )