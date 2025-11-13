from django.db import models

class Product(models.Model):
    # فیلدهای پایه
    token = models.CharField(max_length=50, unique=True, null=True, blank=True)
    title = models.CharField(max_length=500)
    price = models.CharField(max_length=100)
    image_url = models.URLField(blank=True, null=True)
    link = models.URLField()
    search_query = models.CharField(max_length=200)
    seller_name = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # اطلاعات جزئی
    details_scraped = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    
    # مشخصات خودرو
    year = models.CharField(max_length=20, blank=True, null=True)  # سال ساخت
    mileage = models.CharField(max_length=50, blank=True, null=True)  # کارکرد
    color = models.CharField(max_length=50, blank=True, null=True)  # رنگ
    fuel_type = models.CharField(max_length=50, blank=True, null=True)  # نوع سوخت
    phone = models.CharField(max_length=50, blank=True, null=True)  # شماره تماس
    
    # فیلدهای جدید
    brand = models.CharField(max_length=200, blank=True, null=True)  # برند
    body_type = models.CharField(max_length=100, blank=True, null=True)  # تیپ (صندوق‌دار، سدان، وغیره)
    gearbox = models.CharField(max_length=50, blank=True, null=True)  # گیربکس
    insurance = models.CharField(max_length=100, blank=True, null=True)  # بیمه
    
    # وضعیت فیزیکی
    engine_condition = models.CharField(max_length=100, blank=True, null=True)  # وضعیت موتور
    chassis_condition = models.CharField(max_length=100, blank=True, null=True)  # وضعیت شاسی
    body_condition = models.CharField(max_length=100, blank=True, null=True)  # وضعیت بدنه

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
