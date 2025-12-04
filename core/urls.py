from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('tos/', views.tos_view, name='tos'),
    
    # Customer pages
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('customer/order/create/', views.create_order, name='create_order'),
    path('customer/order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('customer/order/<int:order_id>/payment/', views.upload_payment, name='upload_payment'),
    path('customer/order/<int:order_id>/message/', views.send_message, name='send_message'),
    
    # Artist pages
    path('artist/dashboard/', views.artist_dashboard, name='artist_dashboard'),
    path('artist/messages/', views.artist_messages, name='artist_messages'),  # ← THÊM DÒNG NÀY
    path('artist/profile/', views.artist_profile, name='artist_profile'),
    path('artist/services/', views.manage_services, name='manage_services'),
    path('artist/service/add/', views.add_service, name='add_service'),
    path('artist/service/<int:service_id>/edit/', views.edit_service, name='edit_service'),
    path('artist/samples/', views.manage_samples, name='manage_samples'),
    path('artist/sample/add/', views.add_sample, name='add_sample'),
    path('artist/tos/', views.manage_tos, name='manage_tos'),
    path('artist/orders/', views.artist_orders, name='artist_orders'),
    path('artist/order/<int:order_id>/', views.artist_order_detail, name='artist_order_detail'),
    path('artist/order/<int:order_id>/approve/', views.approve_order, name='approve_order'),
    path('artist/order/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('artist/order/<int:order_id>/progress/', views.add_progress, name='add_progress'),
    path('artist/payments/', views.artist_payments, name='artist_payments'),
    path('artist/payment/<int:payment_id>/verify/', views.verify_payment, name='verify_payment'),
    path('artist/customers/', views.manage_customers, name='manage_customers'),

     path('check-username/', views.check_username, name='check_username'),
]