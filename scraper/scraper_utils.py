from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
from bs4 import BeautifulSoup


def human_like_scroll(driver):
    """
    اسکرول مثل انسان (سرعت و مقدار تصادفی)
    """
    scroll_amount = random.randint(400, 900)
    steps = random.randint(4, 8)
    
    for i in range(steps):
        driver.execute_script(f"window.scrollBy(0, {scroll_amount // steps});")
        time.sleep(random.uniform(0.15, 0.5))
    
    time.sleep(random.uniform(1.0, 2.5))


def click_load_more_button(driver):
    """
    کلیک روی دکمه "آگهی‌های بیشتر"
    """
    try:
        load_more_btn = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.post-list__load-more-btn-be092"))
        )
        
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", load_more_btn)
        time.sleep(random.uniform(1.0, 2.0))
        
        actions = ActionChains(driver)
        actions.move_to_element(load_more_btn).pause(random.uniform(0.3, 0.7)).click().perform()
        
        print(f"   ✅ دکمه 'آگهی‌های بیشتر' کلیک شد!")
        time.sleep(random.uniform(3, 5))
        
        return True
    
    except Exception as e:
        print(f"   ⚠️ دکمه 'بیشتر' پیدا نشد")
        return False


def extract_products_from_page(driver, seen_tokens):
    """
    استخراج آگهی‌ها از صفحه فعلی
    """
    products = []
    link_elements = driver.find_elements(By.CSS_SELECTOR, "a.kt-post-card__action")
    
    new_count = 0
    
    for link_elem in link_elements:
        try:
            href = link_elem.get_attribute("href")
            
            if href and "/v/" in href:
                parts = href.split("/")
                token = parts[-1] if parts else ""
                
                if token in seen_tokens:
                    continue
                
                seen_tokens.add(token)
                new_count += 1
                
                try:
                    title_elem = link_elem.find_element(By.CSS_SELECTOR, "h2.kt-post-card__title")
                    title = title_elem.text.strip()
                except:
                    title = f"آگهی"
                
                try:
                    price_elems = link_elem.find_elements(By.CSS_SELECTOR, "div.kt-post-card__description")
                    price = "نامشخص"
                    for elem in price_elems:
                        text = elem.text.strip()
                        if "تومان" in text:
                            price = text
                            break
                except:
                    price = "نامشخص"
                
                try:
                    img_elem = link_elem.find_element(By.CSS_SELECTOR, "img.kt-image-block__image")
                    image_url = img_elem.get_attribute("src") or img_elem.get_attribute("data-src")
                except:
                    image_url = ""
                
                full_link = f"https://divar.ir{href}" if not href.startswith("http") else href
                
                products.append({
                    'token': token,
                    'link': full_link,
                    'title': title,
                    'price': price,
                    'image': image_url,
                    'location': 'تبریز',
                    'seller': 'فروشنده'
                })
        
        except:
            continue
    
    return products, new_count


def scrape_divar_cars_100_scrolls(search_query, max_scrolls=100):
    """
    استخراج با 100 اسکرول و مکث کافی
    """
    all_products = []
    driver = None
    
    try:
        print(f"\n🚀 باز کردن مرورگر...")
        
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"✅ مرورگر باز شد!")
        time.sleep(random.uniform(1, 2))
        
        print(f"🚗 رفتن به دسته ماشین تبریز...")
        driver.get("https://divar.ir/s/tabriz/car")
        time.sleep(random.uniform(3, 5))
        
        print(f"✅ صفحه لود شد!")
        
        if search_query:
            print(f"🔍 جستجو برای: {search_query}")
            time.sleep(random.uniform(1, 2))
            
            try:
                search_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='جستجو']"))
                )
                
                search_box.clear()
                time.sleep(random.uniform(0.3, 0.7))
                
                for char in search_query:
                    search_box.send_keys(char)
                    time.sleep(random.uniform(0.1, 0.3))
                
                time.sleep(random.uniform(0.5, 1.5))
                search_box.send_keys("\n")
                
                print(f"✅ جستجو شد!")
                time.sleep(random.uniform(4, 6))
                
            except Exception as e:
                print(f"⚠️ جستجو انجام نشد: {str(e)}")
        
        print(f"🌐 URL: {driver.current_url}")
        
        print(f"\n{'='*60}")
        print(f"📜 شروع {max_scrolls} بار اسکرول و جمع‌آوری آگهی‌ها...")
        print(f"{'='*60}\n")
        
        seen_tokens = set()
        
        for scroll_num in range(max_scrolls):
            print(f"🔽 اسکرول {scroll_num + 1}/{max_scrolls}")
            
            human_like_scroll(driver)
            
            print(f"   ⏳ مکث برای جمع‌آوری...")
            time.sleep(random.uniform(1.5, 3.0))
            
            new_products, new_count = extract_products_from_page(driver, seen_tokens)
            all_products.extend(new_products)
            
            if new_count > 0:
                print(f"   ✅ {new_count} آگهی جدید | مجموع: {len(all_products)}")
            else:
                print(f"   📊 مجموع: {len(all_products)}")
            
            if (scroll_num + 1) % 10 == 0:
                print(f"\n   🖱️  بررسی دکمه 'آگهی‌های بیشتر'...")
                time.sleep(random.uniform(1, 2))
                
                if click_load_more_button(driver):
                    print(f"   ✅ محتوای بیشتری لود شد!")
                    time.sleep(random.uniform(2, 4))
            
            if random.random() < 0.2:
                pause = random.uniform(2, 5)
                print(f"   ⏸️  مکث {pause:.1f} ثانیه...")
                time.sleep(pause)
            
            time.sleep(random.uniform(0.5, 1.5))
        
        print(f"\n{'='*60}")
        print(f"🎉 جمع‌آوری تمام شد!")
        print(f"📊 مجموع {len(all_products)} آگهی یونیک استخراج شد!")
        print(f"{'='*60}\n")
        
        print(f"📋 نمونه آگهی‌های استخراج شده:\n")
        for i, product in enumerate(all_products[:10], 1):
            print(f"{i}. {product['title'][:55]}")
            print(f"   💰 {product['price']}")
            print(f"   🔗 {product['link']}\n")
        
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            print(f"🔒 بستن مرورگر...")
            time.sleep(3)
            try:
                driver.quit()
            except:
                pass
    
    return all_products


def scrape_divar(search_query):
    """
    تابع اصلی
    """
    print(f"\n{'='*60}")
    print(f"🚗 جستجوی هوشمند در دیوار تبریز")
    print(f"🔍 کلمه کلیدی: {search_query}")
    print(f"📜 اسکرول: 100 بار")
    print(f"{'='*60}")
    
    products = scrape_divar_cars_100_scrolls(search_query, max_scrolls=100)
    
    return products


def scrape_product_details(product_link):
    """
    رفتن به صفحه آگهی و استخراج اطلاعات کامل با تمام فیلدهای جدید
    """
    driver = None
    details = {
        'token': '',
        'title': '',
        'price': '',
        'brand': '',  # برند
        'body_type': '',  # تیپ (صندوق‌دار، سدان)
        'year': '',  # سال ساخت
        'mileage': '',  # کارکرد
        'color': '',  # رنگ
        'fuel_type': '',  # نوع سوخت
        'gearbox': '',  # گیربکس
        'insurance': '',  # بیمه
        'engine_condition': '',  # وضعیت موتور
        'chassis_condition': '',  # وضعیت شاسی
        'body_condition': '',  # وضعیت بدنه
        'description': '',  # توضیحات
        'location': '',  # موقعیت
        'seller': '',  # فروشنده
        'phone': '',  # شماره تماس
        'images': []  # عکس‌ها
    }
    
    try:
        print(f"\n🔗 رفتن به: {product_link}")
        
        # استخراج token از لینک
        if '/v/' in product_link:
            details['token'] = product_link.split('/v/')[-1]
        
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get(product_link)
        time.sleep(random.uniform(4, 6))
        
        # **۱. عنوان**
        try:
            title_elem = driver.find_element(By.CSS_SELECTOR, "h1.kt-page-title__title")
            details['title'] = title_elem.text.strip()
            print(f"   📝 عنوان: {details['title']}")
        except:
            print(f"   ⚠️ عنوان یافت نشد")
        
        # **۲. موقعیت و زمان**
        try:
            location_elem = driver.find_element(By.CSS_SELECTOR, "div.kt-page-title__subtitle")
            details['location'] = location_elem.text.strip()
            print(f"   📍 موقعیت: {details['location']}")
        except:
            pass
        
        # **۳. قیمت**
        try:
            price_rows = driver.find_elements(By.CSS_SELECTOR, "div.kt-unexpandable-row")
            for row in price_rows:
                try:
                    title_text = row.find_element(By.CSS_SELECTOR, "p.kt-unexpandable-row__title").text.strip()
                    if 'قیمت' in title_text:
                        value_elem = row.find_element(By.CSS_SELECTOR, "p.kt-unexpandable-row__value")
                        details['price'] = value_elem.text.strip()
                        print(f"   💰 قیمت: {details['price']}")
                        break
                except:
                    pass
        except:
            print(f"   ⚠️ قیمت یافت نشد")
        
        # **۴. جدول اطلاعات (کارکرد، مدل، رنگ)**
        try:
            table_rows = driver.find_elements(By.CSS_SELECTOR, "table.kt-group-row tbody tr")
            for row in table_rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 3:
                    details['mileage'] = cells[0].text.strip()
                    details['year'] = cells[1].text.strip()
                    details['color'] = cells[2].text.strip()
                    
                    print(f"   🛣️ کارکرد: {details['mileage']}")
                    print(f"   📅 سال: {details['year']}")
                    print(f"   🎨 رنگ: {details['color']}")
                    break
        except:
            print(f"   ⚠️ جدول اطلاعات یافت نشد")
        
        # **۵. سایر ویژگی‌ها (برند، بیمه، گیربکس، سوخت، تیپ)**
        try:
            unexpandable_rows = driver.find_elements(By.CSS_SELECTOR, "div.kt-unexpandable-row")
            
            for row in unexpandable_rows:
                try:
                    title_elem = row.find_element(By.CSS_SELECTOR, "p.kt-unexpandable-row__title")
                    title_text = title_elem.text.strip()
                    
                    # برند و تیپ
                    if 'برند' in title_text or 'تیپ' in title_text:
                        try:
                            value_elem = row.find_element(By.CSS_SELECTOR, "a.kt-unexpandable-row__action")
                            value = value_elem.text.strip()
                            
                            if 'برند' in title_text:
                                details['brand'] = value
                                print(f"   🚙 برند: {value}")
                            else:  # تیپ
                                details['body_type'] = value
                                print(f"   🚗 تیپ: {value}")
                        except:
                            # اگر link نبود، مستقیم value بخونید
                            try:
                                value_elem = row.find_element(By.CSS_SELECTOR, "p.kt-unexpandable-row__value")
                                value = value_elem.text.strip()
                                
                                if 'برند' in title_text:
                                    details['brand'] = value
                                    print(f"   🚙 برند: {value}")
                                else:
                                    details['body_type'] = value
                                    print(f"   🚗 تیپ: {value}")
                            except:
                                pass
                    
                    # بیمه
                    elif 'بیمه' in title_text:
                        try:
                            value_elem = row.find_element(By.CSS_SELECTOR, "p.kt-unexpandable-row__value")
                            details['insurance'] = value_elem.text.strip()
                            print(f"   🛡️  بیمه: {details['insurance']}")
                        except:
                            pass
                    
                    # گیربکس
                    elif 'گیربکس' in title_text:
                        try:
                            value_elem = row.find_element(By.CSS_SELECTOR, "p.kt-unexpandable-row__value")
                            details['gearbox'] = value_elem.text.strip()
                            print(f"   ⚙️  گیربکس: {details['gearbox']}")
                        except:
                            pass
                    
                    # سوخت
                    elif 'سوخت' in title_text:
                        try:
                            value_elem = row.find_element(By.CSS_SELECTOR, "p.kt-unexpandable-row__value")
                            details['fuel_type'] = value_elem.text.strip()
                            print(f"   ⛽ سوخت: {details['fuel_type']}")
                        except:
                            pass
                
                except:
                    continue
        except:
            print(f"   ⚠️ ویژگی‌های اضافی یافت نشد")
        
        # **۶. ارزیابی فروشنده (وضعیت موتور، شاسی، بدنه)**
        try:
            score_rows = driver.find_elements(By.CSS_SELECTOR, "div.kt-score-row")
            
            for row in score_rows:
                try:
                    title_elem = row.find_element(By.CSS_SELECTOR, "p.kt-score-row__title")
                    title_text = title_elem.text.strip()
                    
                    value_elem = row.find_element(By.CSS_SELECTOR, "div.kt-score-row__score")
                    value_text = value_elem.text.strip()
                    
                    if 'موتور' in title_text:
                        details['engine_condition'] = value_text
                        print(f"   🔧 موتور: {value_text}")
                    elif 'شاسی' in title_text:
                        details['chassis_condition'] = value_text
                        print(f"   🛠️  شاسی: {value_text}")
                    elif 'بدنه' in title_text:
                        details['body_condition'] = value_text
                        print(f"   🚗 بدنه: {value_text}")
                
                except:
                    continue
        except:
            print(f"   ⚠️ ارزیابی فروشنده یافت نشد")
        
        # **۷. توضیحات (۵ روش)**
        description_found = False
        
        # روش 1
        try:
            desc_elem = driver.find_element(By.CSS_SELECTOR, "p.kt-description-row__text")
            details['description'] = desc_elem.text.strip()
            if details['description']:
                description_found = True
                print(f"   📄 توضیحات (روش 1): {details['description'][:80]}...")
        except:
            pass
        
        # روش 2
        if not description_found:
            try:
                desc_elem = driver.find_element(By.CSS_SELECTOR, "div.kt-description-row p")
                details['description'] = desc_elem.text.strip()
                if details['description']:
                    description_found = True
                    print(f"   📄 توضیحات (روش 2): {details['description'][:80]}...")
            except:
                pass
        
        # روش 3
        if not description_found:
            try:
                desc_elem = driver.find_element(By.XPATH, "//p[contains(@class, 'kt-description-row__text')]")
                details['description'] = desc_elem.text.strip()
                if details['description']:
                    description_found = True
                    print(f"   📄 توضیحات (روش 3): {details['description'][:80]}...")
            except:
                pass
        
        # روش 4
        if not description_found:
            try:
                all_p = driver.find_elements(By.TAG_NAME, "p")
                for p in all_p:
                    text = p.text.strip()
                    if len(text) > 100 and any(keyword in text for keyword in ['پراید', 'مدل', 'فروش', 'خودرو', 'ماشین']):
                        details['description'] = text
                        description_found = True
                        print(f"   📄 توضیحات (روش 4): {details['description'][:80]}...")
                        break
            except:
                pass
        
        # روش 5 - BeautifulSoup
        if not description_found:
            try:
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                desc_div = soup.find('div', class_='kt-description-row')
                if desc_div:
                    desc_p = desc_div.find('p')
                    if desc_p:
                        details['description'] = desc_p.get_text(strip=True)
                        if details['description']:
                            description_found = True
                            print(f"   📄 توضیحات (روش 5): {details['description'][:80]}...")
            except:
                pass
        
        if not description_found:
            print(f"   ⚠️ توضیحات یافت نشد!")
        
        # **۸. تصاویر**
        try:
            image_elements = driver.find_elements(By.CSS_SELECTOR, "img.kt-image-block__image")
            for img in image_elements[:4]:
                src = img.get_attribute('src')
                if src and 'divarcdn.com' in src:
                    details['images'].append(src)
            
            print(f"   🖼️  تعداد عکس‌ها: {len(details['images'])}")
        except:
            pass
        
        # **۹. شماره تماس (اختیاری)**
        try:
            phone_elems = driver.find_elements(By.CSS_SELECTOR, "a[href^='tel:']")
            if phone_elems:
                phone = phone_elems[0].text.strip()
                if phone:
                    details['phone'] = phone
                    print(f"   📞 تلفن: {phone}")
        except:
            pass
        
        # **۱۰. نام فروشنده**
        try:
            seller_elem = driver.find_element(By.CSS_SELECTOR, "a.kt-user-card__contact")
            details['seller'] = seller_elem.text.strip()
            print(f"   👤 فروشنده: {details['seller']}")
        except:
            pass
        
        print(f"   ✅ جزئیات کامل استخراج شد!")
        
    except Exception as e:
        print(f"   ❌ خطا: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
    
    return details
