"""
Script để tạo dữ liệu mẫu cho website
Chạy: python manage.py shell < init_data.py
"""

from core.models import User, ArtistProfile, ServiceType, TermsOfService
from django.contrib.auth.hashers import make_password

print("🚀 Bắt đầu tạo dữ liệu mẫu...")

# 1. Tạo Artist User
print(" Tạo tài khoản Artist...")
artist, created = User.objects.get_or_create(
    username='duyhoang',
    defaults={
        'email': 'duyhoang@example.com',
        'user_type': 'artist',
        'is_staff': True,
        'is_superuser': True,
        'password': make_password('admin123')  # Password: admin123
    }
)

if created:
    print(f"✅ Đã tạo Artist: {artist.username}")
    print(f"   Username: duyhoang")
    print(f"   Password: admin123")
else:
    print(f"ℹ️  Artist đã tồn tại: {artist.username}")


# 2. Tạo Artist Profile
print("\n2️⃣ Tạo Artist Profile...")
profile, created = ArtistProfile.objects.get_or_create(
    user=artist,
    defaults={
        'bio': 'Xin chào! Tôi là Duy Hoàng, một nghệ sĩ commission chuyên về tranh sketch và digital art.',
        'bank_name': 'Vietcombank',
        'bank_account_number': '3337586730',
        'bank_account_name': 'NGUYEN DUY HOANG'
    }
)

if created:
    print("✅ Đã tạo Artist Profile")
else:
    print("ℹ️  Artist Profile đã tồn tại")

# 3. Tạo Service Types
print("\n3️⃣ Tạo các loại dịch vụ...")

services_data = [
    {
        'name': 'Sketch Gacha Scan',
        'description': 'Tranh sketch gacha scan đến bust up. Phong cách sketch truyền thống với nét vẽ tự nhiên.',
        'price': 90000,
        'is_active': True
    },
    {
        'name': 'Sketch Color Gacha',
        'description': 'Tranh sketch color gacha đến bust up. Có màu sắc và chi tiết phong phú hơn.',
        'price': 280000,
        'is_active': True
    }
]

for service_data in services_data:
    service, created = ServiceType.objects.get_or_create(
        name=service_data['name'],
        defaults=service_data
    )
    if created:
        print(f"✅ Đã tạo dịch vụ: {service.name} - {service.price:,.0f}đ")
    else:
        print(f"ℹ️  Dịch vụ đã tồn tại: {service.name}")

# 4. Tạo Terms of Service
print("\n4️⃣ Tạo điều khoản dịch vụ...")

tos_content = """
ĐIỀU KHOẢN DỊCH VỤ - DUY HOÀNG ART

1. PHẠM VI DỊCH VỤ
- Tôi cung cấp dịch vụ vẽ tranh commission theo yêu cầu
- Các loại dịch vụ: Sketch Gacha Scan và Sketch Color Gacha
- Phạm vi: Đến bust up (đầu và vai)

2. QUY TRÌNH ĐẶT HÀNG
- Khách hàng đặt đơn và mô tả yêu cầu chi tiết
- Tôi sẽ xem xét và duyệt đơn trong vòng 24-48 giờ
- Sau khi duyệt, khách hàng thanh toán theo hướng dẫn
- Tôi bắt đầu vẽ sau khi xác nhận thanh toán

3. THANH TOÁN
- Thanh toán 100% trước khi bắt đầu vẽ
- Chuyển khoản ngân hàng với mã đơn hàng trong nội dung
- Không hoàn tiền sau khi đã bắt đầu vẽ

4. THỜI GIAN HOÀN THÀNH
- Sketch Gacha Scan: 3-5 ngày làm việc
- Sketch Color Gacha: 5-7 ngày làm việc
- Thời gian có thể thay đổi tùy độ phức tạp và số lượng đơn

5. YÊU CẦU VỀ NỘI DUNG
- Không nhận vẽ nội dung 18+, bạo lực, chính trị
- Không nhận vẽ nhân vật có bản quyền (trừ fan art cá nhân)
- Khách hàng chịu trách nhiệm về tính hợp pháp của yêu cầu

6. BẢN QUYỀN
- Khách hàng sở hữu bản vẽ sau khi hoàn thành
- Tôi giữ quyền sử dụng tác phẩm để quảng bá (portfolio, mạng xã hội)
- Không sử dụng cho mục đích thương mại mà không thỏa thuận trước

7. CHỈNH SỬA
- Sketch Gacha Scan: Không chỉnh sửa
- Sketch Color Gacha: Tối đa 2 lần chỉnh sửa nhỏ
- Chỉnh sửa lớn sẽ tính phí thêm

8. LIÊN HỆ VÀ HỖ TRỢ
- Liên hệ qua hệ thống tin nhắn trong website
- Phản hồi trong vòng 24 giờ (trừ cuối tuần)

Cảm ơn bạn đã tin tưởng và ủng hộ!
Duy Hoàng Art
"""

tos, created = TermsOfService.objects.get_or_create(
    version='v1.0',
    defaults={
        'content': tos_content,
        'is_active': True,
        'updated_by': artist
    }
)

if created:
    print("✅ Đã tạo Terms of Service v1.0")
else:
    print("ℹ️  Terms of Service đã tồn tại")

# 5. Tạo Customer mẫu
print("\n5️⃣ Tạo tài khoản khách hàng mẫu...")
customer, created = User.objects.get_or_create(
    username='customer01',
    defaults={
        'email': 'customer01@example.com',
        'user_type': 'customer',
        'password': make_password('customer123'),  # Password: customer123
        'phone': '0912345678'
    }
)

if created:
    print(f"✅ Đã tạo Customer: {customer.username}")
    print(f"   Username: customer01")
    print(f"   Password: customer123")
else:
    print(f"ℹ️  Customer đã tồn tại: {customer.username}")

print("\n" + "="*50)
print("🎉 HOÀN THÀNH! Dữ liệu  đã được tạo")
print("="*50)
print("\n📝 THÔNG TIN ĐĂNG NHẬP:")
print("\n👨‍🎨 ARTIST (Duy Hoàng):")
print("   URL: http://127.0.0.1:8000/login/")
print("   Username: duyhoang")
print("   Password: admin123")
print("\n👤 CUSTOMER (Khách hàng mẫu):")
print("   URL: http://127.0.0.1:8000/login/")
print("   Username: customer01")
print("   Password: customer123")
print("\n" + "="*50)