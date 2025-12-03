from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_staff', 'date_joined')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Thông tin bổ sung', {'fields': ('user_type', 'phone')}),
    )


@admin.register(ArtistProfile)
class ArtistProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bank_name', 'bank_account_number')
    search_fields = ('user__username', 'bank_name')


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('-created_at',)


@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ('title', 'service_type', 'display_order', 'created_at')
    list_filter = ('service_type',)
    search_fields = ('title',)
    ordering = ('display_order', '-created_at')


@admin.register(TermsOfService)
class TermsOfServiceAdmin(admin.ModelAdmin):
    list_display = ('version', 'is_active', 'created_at', 'updated_by')
    list_filter = ('is_active',)
    ordering = ('-created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer', 'service_type', 'status', 'price', 'created_at')
    list_filter = ('status', 'service_type', 'created_at')
    search_fields = ('order_id', 'customer__username')
    readonly_fields = ('order_id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('order_id', 'customer', 'service_type', 'status')
        }),
        ('Chi tiết đơn hàng', {
            'fields': ('description', 'brief_file', 'price')
        }),
        ('Ghi chú', {
            'fields': ('admin_note',)
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at', 'approved_at', 'completed_at')
        }),
    )


@admin.register(OrderProgress)
class OrderProgressAdmin(admin.ModelAdmin):
    list_display = ('order', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('order__order_id',)
    ordering = ('-created_at',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'status', 'created_at', 'verified_by')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_id', 'transaction_id')
    readonly_fields = ('created_at', 'verified_at')
    ordering = ('-created_at',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('order', 'sender', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at', 'sender__user_type')
    search_fields = ('order__order_id', 'sender__username', 'content')
    ordering = ('-created_at',)