from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count  # ← QUAN TRỌNG!
from django.utils import timezone
from .models import *
from .forms import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# ============= HELPER FUNCTIONS =============
def is_artist(user):
    return user.is_authenticated and user.user_type == 'artist'

def is_customer(user):
    return user.is_authenticated and user.user_type == 'customer'

# ============= PUBLIC VIEWS =============
def home(request):
    """Trang chủ - hiển thị samples và giá với filter"""
    services = ServiceType.objects.filter(is_active=True)
    
    # Lấy service filter từ URL parameter
    selected_service = request.GET.get('service')
    
    # Lọc samples theo service nếu có
    if selected_service:
        try:
            selected_service = int(selected_service)
            samples_list = Sample.objects.filter(
                service_type_id=selected_service
            ).select_related('service_type').order_by('display_order', '-id')
        except (ValueError, TypeError):
            # Nếu service ID không hợp lệ, hiện tất cả
            samples_list = Sample.objects.select_related('service_type').order_by('display_order', '-id')
            selected_service = None
    else:
        # Hiện tất cả samples
        samples_list = Sample.objects.select_related('service_type').order_by('display_order', '-id')
        selected_service = None
    
    # Pagination: 12 samples per page
    paginator = Paginator(samples_list, 12)
    page = request.GET.get('page')
    
    try:
        samples = paginator.page(page)
    except PageNotAnInteger:
        samples = paginator.page(1)
    except EmptyPage:
        samples = paginator.page(paginator.num_pages)
    
    tos = TermsOfService.objects.filter(is_active=True).first()
    
    context = {
        'services': services,
        'samples': samples,
        'tos': tos,
        'selected_service': selected_service,  # ← THÊM DÒNG NÀY
    }
    return render(request, 'home.html', context)

def register(request):
    """Đăng ký tài khoản khách hàng"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'customer'
            user.save()
            login(request, user)
            messages.success(request, 'Đăng ký thành công!')
            return redirect('customer_dashboard')
    else:
        form = CustomerRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    """Đăng nhập"""
    if request.user.is_authenticated:
        if request.user.user_type == 'artist':
            return redirect('artist_dashboard')
        return redirect('customer_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.user_type == 'artist':
                return redirect('artist_dashboard')
            return redirect('customer_dashboard')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
    
    return render(request, 'registration/login.html')

def user_logout(request):
    """Đăng xuất"""
    logout(request)
    messages.success(request, 'Đã đăng xuất thành công.')
    return redirect('home')

def tos_view(request):
    """Xem điều khoản dịch vụ"""
    tos = TermsOfService.objects.filter(is_active=True).first()
    return render(request, 'tos.html', {'tos': tos})

# ============= CUSTOMER VIEWS =============
from django.db.models import Count, Q

@login_required
@user_passes_test(is_customer)
def customer_dashboard(request):
    """Dashboard khách hàng"""
    # Lấy orders và annotate số tin nhắn chưa đọc từ artist
    orders = Order.objects.filter(customer=request.user).select_related('service_type').annotate(
        unread_count=Count(
            'messages',
            filter=Q(messages__sender__user_type='artist', messages__is_read=False)
        )
    )
    
    # Đếm số đơn hoàn thành
    completed_count = orders.filter(status='completed').count()
    
    # Đếm tổng tin nhắn chưa đọc
    unread_messages = Message.objects.filter(
        order__customer=request.user,
        sender__user_type='artist',
        is_read=False
    ).count()
    
    context = {
        'orders': orders,
        'completed_count': completed_count,
        'unread_messages': unread_messages,
    }
    return render(request, 'customer/dashboard.html', context)

@login_required
@user_passes_test(is_customer)
def create_order(request):
    """Tạo đơn hàng mới"""
    if request.method == 'POST':
        form = OrderForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = request.user
            order.price = order.service_type.price
            order.save()
            messages.success(request, f'Đơn hàng {order.order_id} đã được tạo thành công!')
            return redirect('order_detail', order_id=order.id)
    else:
        form = OrderForm()
    
    services = ServiceType.objects.filter(is_active=True)
    tos = TermsOfService.objects.filter(is_active=True).first()
    
    context = {
        'form': form,
        'services': services,
        'tos': tos,
    }
    return render(request, 'customer/create_order.html', context)

@login_required
@user_passes_test(is_customer)
def order_detail(request, order_id):
    """Chi tiết đơn hàng"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    messages_list = order.messages.all()
    progress_updates = order.progress_updates.all()
    
    # Lấy artist profile để hiển thị QR code
    try:
        artist_profile = ArtistProfile.objects.get(user__user_type='artist')
    except ArtistProfile.DoesNotExist:
        artist_profile = None
    
    # Đánh dấu tin nhắn đã đọc
    messages_list.filter(sender__user_type='artist', is_read=False).update(is_read=True)
    
    context = {
        'order': order,
        'messages_list': messages_list,
        'progress_updates': progress_updates,
        'artist_profile': artist_profile,  # ← THÊM DÒNG NÀY
    }
    return render(request, 'customer/order_detail.html', context)

@login_required
@user_passes_test(is_customer)
def upload_payment(request, order_id):
    """Upload chứng từ thanh toán"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    if order.status != 'approved':
        messages.error(request, 'Đơn hàng chưa được duyệt.')
        return redirect('order_detail', order_id=order.id)
    
    if hasattr(order, 'payment'):
        messages.warning(request, 'Bạn đã upload chứng từ thanh toán rồi.')
        return redirect('order_detail', order_id=order.id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.order = order
            payment.save()
            messages.success(request, 'Đã upload chứng từ thanh toán. Vui lòng chờ xác thực.')
            return redirect('order_detail', order_id=order.id)
    else:
        form = PaymentForm()
    
    context = {
        'form': form,
        'order': order,
    }
    return render(request, 'customer/upload_payment.html', context)

@login_required
@user_passes_test(is_customer)
def send_message(request, order_id):
    """Gửi tin nhắn cho artist"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        
        if content or image:
            Message.objects.create(
                order=order,
                sender=request.user,
                content=content or '',
                image=image
            )
            messages.success(request, 'Đã gửi tin nhắn.')
    
    return redirect('order_detail', order_id=order.id)
# ============= ARTIST VIEWS =============
@login_required
@user_passes_test(is_artist)
def artist_dashboard(request):
    """Dashboard artist"""
    pending_orders = Order.objects.filter(status='pending').count()
    pending_payments = Payment.objects.filter(status='pending').count()
    in_progress_orders = Order.objects.filter(status='in_progress').count()
    
    # Lấy orders gần đây và đếm tin nhắn chưa đọc từ customer
    recent_orders = Order.objects.select_related('customer', 'service_type').annotate(
        unread_count=Count(
            'messages',
            filter=Q(messages__sender__user_type='customer', messages__is_read=False)
        )
    ).all()[:10]
    
    unread_messages = Message.objects.filter(
        sender__user_type='customer',
        is_read=False
    ).count()
    
    context = {
        'pending_orders': pending_orders,
        'pending_payments': pending_payments,
        'in_progress_orders': in_progress_orders,
        'recent_orders': recent_orders,
        'unread_messages': unread_messages,
    }
    return render(request, 'artist/dashboard.html', context)


@login_required
@user_passes_test(is_artist)
def artist_profile(request):
    """Quản lý thông tin cá nhân artist"""
    profile, created = ArtistProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ArtistProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật thông tin thành công!')
            return redirect('artist_profile')
    else:
        form = ArtistProfileForm(instance=profile)
    
    return render(request, 'artist/profile.html', {'form': form, 'profile': profile})


@login_required
@user_passes_test(is_artist)
def manage_services(request):
    """Quản lý loại dịch vụ"""
    services = ServiceType.objects.all()
    return render(request, 'artist/services/list.html', {'services': services})


@login_required
@user_passes_test(is_artist)
def add_service(request):
    """Thêm loại dịch vụ mới"""
    if request.method == 'POST':
        form = ServiceTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm dịch vụ mới!')
            return redirect('manage_services')
    else:
        form = ServiceTypeForm()
    
    return render(request, 'artist/services/form.html', {'form': form, 'action': 'add'})


@login_required
@user_passes_test(is_artist)
def edit_service(request, service_id):
    """Chỉnh sửa loại dịch vụ"""
    service = get_object_or_404(ServiceType, id=service_id)
    
    if request.method == 'POST':
        form = ServiceTypeForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật dịch vụ!')
            return redirect('manage_services')
    else:
        form = ServiceTypeForm(instance=service)
    
    return render(request, 'artist/services/form.html', {
        'form': form, 
        'action': 'edit',
        'service': service
    })


@login_required
@user_passes_test(is_artist)
def manage_samples(request):
    """Quản lý samples"""
    samples = Sample.objects.select_related('service_type').all()
    return render(request, 'artist/samples/list.html', {'samples': samples})


@login_required
@user_passes_test(is_artist)
def add_sample(request):
    """Thêm sample mới"""
    if request.method == 'POST':
        form = SampleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm sample mới!')
            return redirect('manage_samples')
    else:
        form = SampleForm()
    
    return render(request, 'artist/samples/form.html', {'form': form})


@login_required
@user_passes_test(is_artist)
def manage_tos(request):
    """Quản lý điều khoản dịch vụ"""
    tos_list = TermsOfService.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        form = TermsOfServiceForm(request.POST)
        if form.is_valid():
            tos = form.save(commit=False)
            tos.updated_by = request.user
            tos.save()
            messages.success(request, 'Đã tạo TOS mới!')
            return redirect('manage_tos')
    else:
        form = TermsOfServiceForm()
    
    return render(request, 'artist/tos/manage.html', {'form': form, 'tos_list': tos_list})


@login_required
@user_passes_test(is_artist)
def artist_orders(request):
    """Danh sách đơn hàng"""
    status_filter = request.GET.get('status', 'all')
    
    orders = Order.objects.select_related('customer', 'service_type').all()
    
    if status_filter != 'all':
        orders = orders.filter(status=status_filter)
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
    }
    return render(request, 'artist/orders/list.html', context)


@login_required
@user_passes_test(is_artist)
def artist_order_detail(request, order_id):
    """Chi tiết đơn hàng (artist view)"""
    order = get_object_or_404(Order, id=order_id)
    messages_list = order.messages.all()
    progress_updates = order.progress_updates.all()
    
    # Đánh dấu tin nhắn đã đọc
    messages_list.filter(sender__user_type='customer', is_read=False).update(is_read=True)
    
    # Form gửi tin nhắn
    if request.method == 'POST' and 'send_message' in request.POST:
        content = request.POST.get('content')
        image = request.FILES.get('image')
        
        if content or image:
            Message.objects.create(
                order=order,
                sender=request.user,
                content=content or '',
                image=image
            )
            messages.success(request, 'Đã gửi tin nhắn.')
            return redirect('artist_order_detail', order_id=order.id)
    
    context = {
        'order': order,
        'messages_list': messages_list,
        'progress_updates': progress_updates,
    }
    return render(request, 'artist/orders/detail.html', context)


@login_required
@user_passes_test(is_artist)
def approve_order(request, order_id):
    """Duyệt đơn hàng"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        form = OrderApprovalForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['approve']:
                order.status = 'approved'
                order.price = form.cleaned_data['price']
                order.admin_note = form.cleaned_data.get('admin_note', '')
                order.approved_at = timezone.now()
                order.save()
                messages.success(request, f'Đã duyệt đơn hàng {order.order_id}!')
            else:
                order.status = 'cancelled'
                order.admin_note = form.cleaned_data.get('admin_note', '')
                order.save()
                messages.warning(request, f'Đã từ chối đơn hàng {order.order_id}.')
            
            return redirect('artist_order_detail', order_id=order.id)
    else:
        form = OrderApprovalForm(initial={'price': order.service_type.price})
    
    return render(request, 'artist/orders/approve.html', {'form': form, 'order': order})


@login_required
@user_passes_test(is_artist)
def update_order_status(request, order_id):
    """Cập nhật trạng thái đơn hàng"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        form = OrderStatusForm(request.POST)
        if form.is_valid():
            order.status = form.cleaned_data['status']
            order.admin_note = form.cleaned_data.get('admin_note', '')
            
            if order.status == 'completed':
                order.completed_at = timezone.now()
            
            order.save()
            messages.success(request, 'Đã cập nhật trạng thái đơn hàng!')
            return redirect('artist_order_detail', order_id=order.id)
    else:
        form = OrderStatusForm()
    
    return render(request, 'artist/orders/update_status.html', {'form': form, 'order': order})


@login_required
@user_passes_test(is_artist)
def add_progress(request, order_id):
    """Thêm tiến độ vẽ"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        form = OrderProgressForm(request.POST, request.FILES)
        if form.is_valid():
            progress = form.save(commit=False)
            progress.order = order
            progress.created_by = request.user
            progress.save()
            messages.success(request, 'Đã cập nhật tiến độ!')
            return redirect('artist_order_detail', order_id=order.id)
    else:
        form = OrderProgressForm()
    
    return render(request, 'artist/orders/add_progress.html', {'form': form, 'order': order})


@login_required
@user_passes_test(is_artist)
def artist_payments(request):
    """Danh sách thanh toán chờ xác thực"""
    payments = Payment.objects.select_related('order', 'order__customer').filter(
        status='pending'
    )
    
    verified_payments = Payment.objects.select_related('order', 'order__customer').filter(
        status='verified'
    )[:20]
    
    context = {
        'payments': payments,
        'verified_payments': verified_payments,
    }
    return render(request, 'artist/payments/list.html', context)


@login_required
@user_passes_test(is_artist)
def verify_payment(request, payment_id):
    """Xác thực thanh toán"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        form = PaymentVerificationForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('verify'):
                payment.status = 'verified'
                payment.verified_at = timezone.now()
                payment.verified_by = request.user
                payment.admin_note = form.cleaned_data.get('admin_note', '')
                payment.save()
                
                # Cập nhật trạng thái đơn hàng
                payment.order.status = 'paid'
                payment.order.save()
                
                messages.success(request, 'Đã xác thực thanh toán!')
            
            elif form.cleaned_data.get('reject'):
                payment.status = 'rejected'
                payment.verified_at = timezone.now()
                payment.verified_by = request.user
                payment.admin_note = form.cleaned_data.get('admin_note', '')
                payment.save()
                
                messages.warning(request, 'Đã từ chối thanh toán.')
            
            return redirect('artist_payments')
    else:
        form = PaymentVerificationForm()
    
    context = {
        'form': form,
        'payment': payment,
    }
    return render(request, 'artist/payments/verify.html', context)


@login_required
@user_passes_test(is_artist)
def manage_customers(request):
    """Quản lý khách hàng"""
    customers = User.objects.filter(user_type='customer').prefetch_related('orders')
    
    customer_data = []
    for customer in customers:
        customer_data.append({
            'user': customer,
            'total_orders': customer.orders.count(),
            'completed_orders': customer.orders.filter(status='completed').count(),
            'total_spent': sum(
                order.price for order in customer.orders.filter(status='completed')
            ),
        })
    
    context = {
        'customer_data': customer_data,
    }
    return render(request, 'artist/customers/list.html', context)

@login_required
@user_passes_test(is_artist)
def artist_messages(request):
    """Xem tất cả đơn hàng có tin nhắn mới"""
    # Lấy tất cả orders có tin nhắn chưa đọc từ customer
    orders_with_messages = Order.objects.select_related('customer', 'service_type').annotate(
        unread_count=Count(
            'messages',
            filter=Q(messages__sender__user_type='customer', messages__is_read=False)
        )
    ).filter(unread_count__gt=0).order_by('-updated_at')
    
    context = {
        'orders': orders_with_messages,
    }
    return render(request, 'artist/messages.html', context)
# THÊM VÀO CUỐI FILE views.py
from django.http import JsonResponse

def check_username(request):
    """API endpoint to check if username exists"""
    username = request.GET.get('username', '')
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})