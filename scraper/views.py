from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Product
from .scraper_utils import scrape_divar, scrape_product_details
import time
import random
import re


def extract_price_number(price_str):
    if not price_str:
        return 0
    numbers = re.findall(r'\d+', price_str.replace(',', ''))
    if numbers:
        return int(''.join(numbers))
    return 0


def extract_mileage_number(mileage_str):
    if not mileage_str:
        return 0
    numbers = re.findall(r'\d+', str(mileage_str).replace(',', ''))
    if numbers:
        return int(''.join(numbers))
    return 0


def extract_year_number(year_str):
    if not year_str:
        return 0
    numbers = re.findall(r'\d{4}', str(year_str))
    if numbers:
        return int(numbers[0])
    return 0


@login_required(login_url='login')
def home(request):
    products = []
    search_query = ''
    message = ''
    if request.method == 'POST':
        search_query = request.POST.get('query', '').strip()
        if search_query:
            try:
                message = '⏳ در حال جمعآوری آگهیها... این کار چند دقیقه طول میکشد'
                scraped_products = scrape_divar(search_query)
                if scraped_products:
                    message = f'✅ {len(scraped_products)} آگهی پیدا شد و در دیتابیس ذخیره شد!'
                    saved_count = 0
                    for product in scraped_products:
                        if not Product.objects.filter(token=product['token']).exists():
                            Product.objects.create(
                                token=product['token'],
                                title=product['title'],
                                price=product['price'],
                                image_url='',
                                link=product['link'],
                                search_query=search_query,
                                seller_name=product.get('seller', ''),
                                location=product.get('location', '')
                            )
                            saved_count += 1
                    message = f'✅ {len(scraped_products)} آگهی پیدا شد | {saved_count} آگهی جدید ذخیره شد!'
                    products = scraped_products
                else:
                    message = '❌ آگهیای یافت نشد'
            except Exception as e:
                message = f'⚠️ خطا: {str(e)}'

    if not products:
        recent_products = Product.objects.order_by('-created_at')[:500]
        products = [{
            'title': p.title,
            'price': p.price,
            'image': '',
            'link': p.link,
            'location': p.location,
            'seller': p.seller_name
        } for p in recent_products]

    context = {
        'products': products,
        'search_query': search_query,
        'message': message,
        'product_count': len(products)
    }

    return render(request, 'scraper/home.html', context)


@login_required(login_url='login')
def scrape_details(request):
    """
    صفحه استخراج جزئیات آگهیها با لود مرحله‌ای (Step by Step)
    """
    message = ''
    stats = {
        'total': Product.objects.count(),
        'scraped': Product.objects.filter(details_scraped=True).count(),
        'remaining': Product.objects.filter(details_scraped=False).count(),
        'current': 0
    }

    if request.method == 'POST':
        # استخراج یک آگهی فقط
        product = Product.objects.filter(details_scraped=False).first()
        
        if not product:
            message = '✅ جزئیات همه آگهیها استخراج شده است!'
        else:
            try:
                print(f"\n🔗 استخراج: {product.title[:40]}...")
                
                # استخراج جزئیات
                details = scrape_product_details(product.link)
                
                if details:
                    # ذخیره‌سازی
                    if details.get('title'):
                        product.title = details['title']
                    if details.get('price'):
                        product.price = details['price']
                    if details.get('description'):
                        product.description = details['description']
                    if details.get('year'):
                        product.year = details['year']
                    if details.get('mileage'):
                        product.mileage = details['mileage']
                    if details.get('color'):
                        product.color = details['color']
                    if details.get('fuel_type'):
                        product.fuel_type = details['fuel_type']
                    if details.get('gearbox'):
                        product.gearbox = details['gearbox']
                    if details.get('brand'):
                        product.brand = details['brand']
                    if details.get('body_type'):
                        product.body_type = details['body_type']
                    if details.get('engine_condition'):
                        product.engine_condition = details['engine_condition']
                    if details.get('chassis_condition'):
                        product.chassis_condition = details['chassis_condition']
                    if details.get('body_condition'):
                        product.body_condition = details['body_condition']
                    if details.get('insurance'):
                        product.insurance = details['insurance']
                    if details.get('phone'):
                        product.phone = details['phone']
                    if details.get('location'):
                        product.location = details['location']
                    if details.get('seller'):
                        product.seller_name = details['seller']
                    
                    product.details_scraped = True
                    product.save()
                    
                    message = f'✅ "{product.title[:30]}..." ذخیره شد!'
                else:
                    message = f'⚠️ نتونستم اطلاعات "{product.title[:30]}" رو بیام'
                
            except Exception as e:
                message = f'❌ خطا: {str(e)}'
                print(f"❌ خطا: {str(e)}")

        # آپدیت آمار
        stats['total'] = Product.objects.count()
        stats['scraped'] = Product.objects.filter(details_scraped=True).count()
        stats['remaining'] = Product.objects.filter(details_scraped=False).count()
        stats['current'] = stats['scraped']

    context = {
        'message': message,
        'stats': stats,
    }

    return render(request, 'scraper/scrape_details.html', context)


@login_required(login_url='login')
def scrape_details_api(request):
    """
    API برای استخراج یک آگهی (برای AJAX)
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        # دریافت یک آگهی که استخراج نشده
        product = Product.objects.filter(details_scraped=False).first()
        
        total = Product.objects.count()
        scraped = Product.objects.filter(details_scraped=True).count()
        remaining = Product.objects.filter(details_scraped=False).count()
        
        if not product:
            return JsonResponse({
                'status': 'completed',
                'message': '✅ تمام آگهی‌ها استخراج شدند!',
                'total': total,
                'scraped': scraped,
                'remaining': remaining,
                'percentage': 100,
            })
        
        # استخراج جزئیات
        details = scrape_product_details(product.link)
        
        if details:
            # ذخیره‌سازی
            if details.get('title'):
                product.title = details['title']
            if details.get('price'):
                product.price = details['price']
            if details.get('description'):
                product.description = details['description']
            if details.get('year'):
                product.year = details['year']
            if details.get('mileage'):
                product.mileage = details['mileage']
            if details.get('color'):
                product.color = details['color']
            if details.get('fuel_type'):
                product.fuel_type = details['fuel_type']
            if details.get('gearbox'):
                product.gearbox = details['gearbox']
            if details.get('brand'):
                product.brand = details['brand']
            if details.get('body_type'):
                product.body_type = details['body_type']
            if details.get('engine_condition'):
                product.engine_condition = details['engine_condition']
            if details.get('chassis_condition'):
                product.chassis_condition = details['chassis_condition']
            if details.get('body_condition'):
                product.body_condition = details['body_condition']
            if details.get('insurance'):
                product.insurance = details['insurance']
            if details.get('phone'):
                product.phone = details['phone']
            if details.get('location'):
                product.location = details['location']
            if details.get('seller'):
                product.seller_name = details['seller']
            
            product.details_scraped = True
            product.save()
            
            # آپدیت آمار
            scraped = Product.objects.filter(details_scraped=True).count()
            remaining = Product.objects.filter(details_scraped=False).count()
            percentage = int((scraped / total) * 100) if total > 0 else 0
            
            return JsonResponse({
                'status': 'success',
                'message': f'✅ "{product.title[:40]}" ذخیره شد',
                'total': total,
                'scraped': scraped,
                'remaining': remaining,
                'percentage': percentage,
            })
        else:
            remaining = Product.objects.filter(details_scraped=False).count()
            return JsonResponse({
                'status': 'error',
                'message': f'⚠️ نتونستم "{product.title[:40]}" رو بیام',
                'total': total,
                'scraped': scraped,
                'remaining': remaining,
                'percentage': int((scraped / total) * 100) if total > 0 else 0,
            })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'❌ خطا: {str(e)}'
        }, status=500)


def expert_analysis(new_product, similar_products):
    """
    تجزیه و تحلیل کارشناسی خودرو
    """
    analysis = {
        'price_status': 'نامشخص',
        'score': 0,
        'advice': '',
        'result_text': '',
        'details': [],
        'score_color': 'secondary',
        'price_analysis': {},
        'condition_analysis': {},
        'mileage_analysis': {},
        'final_recommendation': '',
    }
    
    new_price = extract_price_number(new_product.price)
    new_mileage = extract_mileage_number(new_product.mileage)
    new_year = extract_year_number(new_product.year)
    
    count = similar_products.count()
    
    if count == 0:
        analysis['price_status'] = '📊 داده‌های بازار کافی نیست'
        analysis['advice'] = 'تعداد محصولات مشابه در دیتابیس کم است.'
        analysis['result_text'] = 'امتیاز کارشناسی: 50/100 — نتیجه غیر قطعی'
        analysis['score'] = 50
        analysis['score_color'] = 'warning'
        return analysis
    
    prices = []
    mileages = []
    years = []
    
    for p in similar_products:
        price = extract_price_number(p.price)
        mileage = extract_mileage_number(p.mileage)
        year = extract_year_number(p.year)
        
        if price > 0:
            prices.append(price)
        if mileage > 0:
            mileages.append(mileage)
        if year > 0:
            years.append(year)
    
    avg_price = sum(prices) // len(prices) if prices else 0
    avg_mileage = sum(mileages) // len(mileages) if mileages else 0
    avg_year = sum(years) // len(years) if years else 0
    
    min_price = min(prices) if prices else 0
    max_price = max(prices) if prices else 0
    
    score = 50
    price_percent_diff = 0
    
    if avg_price > 0:
        price_percent_diff = ((new_price - avg_price) / avg_price) * 100
        ratio = new_price / avg_price
        
        analysis['price_analysis'] = {
            'new_price': new_price,
            'avg_price': avg_price,
            'min_price': min_price,
            'max_price': max_price,
            'percent_diff': price_percent_diff,
        }
        
        if ratio < 0.85:
            analysis['price_status'] = '🟢 خیلی عالی - قیمت خوب'
            score += 20
            analysis['score_color'] = 'success'
            price_advice = f'قیمت {abs(price_percent_diff):.0f}% کمتر از میانگین است! ✅'
            
        elif ratio > 1.15:
            analysis['price_status'] = '🔴 گران - توصیه نمی‌شود'
            score -= 20
            analysis['score_color'] = 'danger'
            price_advice = f'قیمت {price_percent_diff:.0f}% بالاتر از میانگین است! ❌'
            
        else:
            analysis['price_status'] = '🟡 معقول - قابل قبول'
            score += 5
            analysis['score_color'] = 'warning'
            price_advice = f'قیمت تقریباً برابر میانگین است. ⚠️'
    else:
        price_advice = 'داده قیمت کافی نیست'
    
    condition_score_bonus = 0
    condition_details = []
    
    if new_product.engine_condition:
        if 'سالم' in new_product.engine_condition:
            condition_score_bonus += 8
            condition_details.append('✅ موتور سالم')
        else:
            condition_score_bonus -= 5
            condition_details.append('⚠️ موتور نیاز به تعمیر دارد')
    
    if new_product.chassis_condition:
        if 'سالم' in new_product.chassis_condition and 'پلمپ' in new_product.chassis_condition:
            condition_score_bonus += 8
            condition_details.append('✅ شاسی سالم و پلمپ')
        elif 'سالم' in new_product.chassis_condition:
            condition_score_bonus += 5
            condition_details.append('✅ شاسی سالم')
        else:
            condition_score_bonus -= 8
            condition_details.append('❌ شاسی مشکل دارد')
    
    if new_product.body_condition:
        if 'دوررنگ' in new_product.body_condition or 'رنگ' in new_product.body_condition:
            condition_score_bonus -= 8
            condition_details.append('⚠️ بدنه دوررنگ')
        elif 'سالم' in new_product.body_condition:
            condition_score_bonus += 5
            condition_details.append('✅ بدنه سالم')
        else:
            condition_score_bonus -= 5
            condition_details.append('⚠️ بدنه نیاز به تعمیر دارد')
    
    analysis['condition_analysis'] = {
        'engine': new_product.engine_condition or 'نامشخص',
        'chassis': new_product.chassis_condition or 'نامشخص',
        'body': new_product.body_condition or 'نامشخص',
        'details': condition_details,
    }
    
    mileage_score_bonus = 0
    mileage_advice = ''
    
    if new_mileage > 0 and avg_mileage > 0:
        mileage_percent_diff = ((new_mileage - avg_mileage) / avg_mileage) * 100
        
        if new_mileage < avg_mileage * 0.85:
            mileage_score_bonus += 10
            mileage_advice = f'کارکرد {abs(mileage_percent_diff):.0f}% کمتر از میانگین است! ✅'
        elif new_mileage > avg_mileage * 1.15:
            mileage_score_bonus -= 10
            mileage_advice = f'کارکرد {mileage_percent_diff:.0f}% بیشتر است. ⚠️'
        else:
            mileage_score_bonus += 3
            mileage_advice = 'کارکرد تقریباً معمولی است'
        
        analysis['mileage_analysis'] = {
            'new_mileage': new_mileage,
            'avg_mileage': avg_mileage,
            'percent_diff': mileage_percent_diff,
            'advice': mileage_advice,
        }
    
    price_per_mileage_bonus = 0
    if new_mileage > 0 and avg_mileage > 0:
        new_price_per_km = new_price / new_mileage if new_mileage > 0 else 0
        avg_price_per_km = avg_price / avg_mileage if avg_mileage > 0 else 0
        
        if new_price_per_km < avg_price_per_km * 0.9:
            price_per_mileage_bonus += 8
        elif new_price_per_km > avg_price_per_km * 1.1:
            price_per_mileage_bonus -= 5
    
    score += condition_score_bonus + mileage_score_bonus + price_per_mileage_bonus
    score = max(0, min(100, score))
    
    if score >= 85:
        analysis['score_color'] = 'success'
    elif score >= 70:
        analysis['score_color'] = 'info'
    elif score >= 50:
        analysis['score_color'] = 'warning'
    else:
        analysis['score_color'] = 'danger'
    
    if score >= 90:
        final_rec = '🟢 خرید فوق‌العاده - بسیار خوب است'
    elif score >= 75:
        final_rec = '🟢 خرید خوبی است - توصیه می‌شود'
    elif score >= 60:
        final_rec = '🟡 خرید قابل قبول - با دقت بررسی کنید'
    elif score >= 45:
        final_rec = '🟡 خرید با ریسک - نیاز به مذاکره قیمت'
    else:
        final_rec = '🔴 توصیه نمی‌شود - خرید نکنید'
    
    analysis['final_recommendation'] = final_rec
    analysis['score'] = score
    analysis['advice'] = price_advice
    analysis['details'] = [
        f'📊 تعداد خودروهای مشابه: {count}',
        f'💰 قیمت آگهی: {new_price:,} تومان',
        f'💰 میانگین بازار: {avg_price:,} تومان',
        f'📈 محدوده قیمت: {min_price:,} تا {max_price:,}',
        f'🛣️ کارکرد آگهی: {new_mileage:,} کیلومتر',
        f'🛣️ میانگین کارکرد: {avg_mileage:,} کیلومتر' if avg_mileage > 0 else '🛣️ اطلاعات کارکرد کافی نیست',
        f'📅 سال ساخت: {new_year}',
        f'📅 میانگین سال: {avg_year}',
    ] + condition_details
    
    analysis['result_text'] = f'🏆 امتیاز کارشناسی: {analysis["score"]}/100 — {final_rec}'
    
    return analysis


@login_required(login_url='login')
def analyze_product(request):
    """
    صفحه تحلیل و مقایسه آگهی جدید
    """
    
    message = ''
    product_data = None
    analysis = None
    similar_products = None
    product_obj = None
    
    if request.method == 'POST':
        product_link = request.POST.get('product_link', '').strip()
        
        if not product_link:
            message = '❌ لطفا لینک آگهی رو وارد کنید'
        else:
            try:
                message = '⏳ در حال استخراج اطلاعات آگهی...'
                
                product_data = scrape_product_details(product_link)
                
                if not product_data or not product_data.get('title'):
                    message = '❌ نتونستم اطلاعات آگهی رو بیام'
                else:
                    message = '✅ اطلاعات استخراج شد! درحال ذخیره و تحلیل...'
                    
                    # ✅ حل: استفاده از filter().first() بجای get_or_create
                    product_obj = Product.objects.filter(link=product_link).first()
                    
                    if product_obj:
                        # اگر قبلاً وجود داشت
                        # آپدیت داده‌های جدید
                        product_obj.token = product_data.get('token', product_obj.token or f'analyze_{int(time.time())}')
                        product_obj.title = product_data.get('title', product_obj.title)
                        product_obj.price = product_data.get('price', product_obj.price)
                        product_obj.brand = product_data.get('brand', product_obj.brand)
                        product_obj.body_type = product_data.get('body_type', product_obj.body_type)
                        product_obj.year = product_data.get('year', product_obj.year)
                        product_obj.mileage = product_data.get('mileage', product_obj.mileage)
                        product_obj.color = product_data.get('color', product_obj.color)
                        product_obj.fuel_type = product_data.get('fuel_type', product_obj.fuel_type)
                        product_obj.gearbox = product_data.get('gearbox', product_obj.gearbox)
                        product_obj.insurance = product_data.get('insurance', product_obj.insurance)
                        product_obj.engine_condition = product_data.get('engine_condition', product_obj.engine_condition)
                        product_obj.chassis_condition = product_data.get('chassis_condition', product_obj.chassis_condition)
                        product_obj.body_condition = product_data.get('body_condition', product_obj.body_condition)
                        product_obj.description = product_data.get('description', product_obj.description)
                        product_obj.phone = product_data.get('phone', product_obj.phone)
                        product_obj.seller_name = product_data.get('seller', product_obj.seller_name)
                        product_obj.location = product_data.get('location', product_obj.location)
                        product_obj.search_query = 'analyze'
                        product_obj.details_scraped = True
                        product_obj.save()
                        message = '✅ آگهی آپدیت شد! درحال تحلیل کارشناسی...'
                    else:
                        # اگر جدید است
                        product_obj = Product.objects.create(
                            link=product_link,
                            token=product_data.get('token', f'analyze_{int(time.time())}'),
                            title=product_data.get('title', 'بدون نام'),
                            price=product_data.get('price', ''),
                            brand=product_data.get('brand', ''),
                            body_type=product_data.get('body_type', ''),
                            year=product_data.get('year', ''),
                            mileage=product_data.get('mileage', ''),
                            color=product_data.get('color', ''),
                            fuel_type=product_data.get('fuel_type', ''),
                            gearbox=product_data.get('gearbox', ''),
                            insurance=product_data.get('insurance', ''),
                            engine_condition=product_data.get('engine_condition', ''),
                            chassis_condition=product_data.get('chassis_condition', ''),
                            body_condition=product_data.get('body_condition', ''),
                            description=product_data.get('description', ''),
                            phone=product_data.get('phone', ''),
                            seller_name=product_data.get('seller', ''),
                            location=product_data.get('location', ''),
                            search_query='analyze',
                            details_scraped=True,
                        )
                        message = '✅ آگهی جدید ذخیره شد! درحال تحلیل کارشناسی...'

                    # تحلیل کارشناسی
                    similar_query = Product.objects.filter(details_scraped=True).exclude(id=product_obj.id)
                    
                    if product_obj.brand:
                        similar_query = similar_query.filter(brand__icontains=product_obj.brand)
                    
                    if product_obj.body_type:
                        similar_query = similar_query.filter(body_type__icontains=product_obj.body_type)
                    
                    if product_obj.year:
                        similar_query = similar_query.filter(year__icontains=product_obj.year)
                    
                    similar_products = similar_query[:15]
                    
                    if similar_products.count() < 3 and product_obj.brand:
                        similar_products = Product.objects.filter(
                            brand__icontains=product_obj.brand,
                            details_scraped=True
                        ).exclude(id=product_obj.id)[:15]
                    
                    analysis = expert_analysis(product_obj, similar_products)
                    message = '✅ تجزیه و تحلیل کارشناسی تمام شد!'
                    
            except Exception as e:
                message = f'⚠️ خطا: {str(e)}'
                import traceback
                traceback.print_exc()
    
    context = {
        'message': message,
        'product_data': product_data,
        'product_obj': product_obj,
        'analysis': analysis,
        'similar_products': similar_products,
    }
    
    return render(request, 'scraper/analyze_product.html', context)
