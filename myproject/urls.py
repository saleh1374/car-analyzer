from django.contrib import admin
from django.urls import path
from users import views as users_views
from scraper import views as scraper_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', users_views.register, name='register'),
    path('login/', users_views.login_view, name='login'),
    path('logout/', users_views.logout_view, name='logout'),
    path('', scraper_views.home, name='home'),
    path('scrape-details/', scraper_views.scrape_details, name='scrape_details'),
    path('api/scrape-details/', scraper_views.scrape_details_api, name='scrape_details_api'),  # ← API جدید برای AJAX
    path('analyze/', scraper_views.analyze_product, name='analyze_product'),
]