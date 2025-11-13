from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # فیلدهایی که در لیست نمایش داده می‌شوند
    list_display = [
        'id',
        'title_short', 
        'price', 
        'year', 
        'mileage', 
        'color',
        'fuel_type',
        'gearbox',
        'details_scraped', 
        'created_at'
    ]
    
    # فیلترهای سمت راست
    list_filter = [
        'details_scraped', 
        'search_query',
        'year',
        'fuel_type',
        'gearbox',
        'created_at'
    ]
    
    # فیلدهایی که قابل جستجو هستند
    search_fields = [
        'title', 
        'token', 
        'location', 
        'brand',
        'color'
    ]
    
    # فیلدهایی که می‌توان مستقیم ویرایش کرد
    list_editable = ['details_scraped']
    
    # ترتیب نمایش
    ordering = ['-created_at']
    
    # تعداد آیتم در هر صفحه
    list_per_page = 50
    
    # گروه‌بندی فیلدها در صفحه ویرایش
    fieldsets = (
        ('🔗 اطلاعات پایه', {
            'fields': ('token', 'title', 'link', 'search_query')
        }),
        ('💰 قیمت و موقعیت', {
            'fields': ('price', 'location', 'seller_name', 'phone')
        }),
        ('🚗 مشخصات خودرو', {
            'fields': ('brand', 'year', 'mileage', 'color', 'fuel_type', 'gearbox', 'insurance')
        }),
        ('✅ ارزیابی', {
            'fields': ('engine_condition', 'chassis_condition', 'body_condition')
        }),
        ('📝 جزئیات', {
            'fields': ('description',)
        }),
        ('🖼️ تصویر', {
            'fields': ('image_url',),
            'classes': ('collapse',)  # پنهان شدن به صورت پیش‌فرض
        }),
        ('📊 وضعیت', {
            'fields': ('details_scraped', 'created_at')
        }),
    )
    
    # فیلدهای فقط خواندنی
    readonly_fields = ['created_at', 'token', 'link']
    
    # تابع برای نمایش عنوان کوتاه
    def title_short(self, obj):
        if len(obj.title) > 50:
            return obj.title[:50] + '...'
        return obj.title
    title_short.short_description = 'عنوان'
    
    # رنگ‌بندی برای وضعیت استخراج
    def details_scraped_colored(self, obj):
        if obj.details_scraped:
            return '✅ بله'
        return '❌ خیر'
    details_scraped_colored.short_description = 'استخراج شده'
    
    # اکشن‌های دسته‌جمعی
    actions = ['mark_as_scraped', 'mark_as_not_scraped', 'delete_selected']
    
    def mark_as_scraped(self, request, queryset):
        updated = queryset.update(details_scraped=True)
        self.message_user(request, f'{updated} آگهی به عنوان "استخراج شده" علامت زده شد.')
    mark_as_scraped.short_description = 'علامت زدن به عنوان استخراج شده'
    
    def mark_as_not_scraped(self, request, queryset):
        updated = queryset.update(details_scraped=False)
        self.message_user(request, f'{updated} آگهی به عنوان "استخراج نشده" علامت زده شد.')
    mark_as_not_scraped.short_description = 'علامت زدن به عنوان استخراج نشده'
