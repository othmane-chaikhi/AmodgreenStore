"""amodIgren URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns  # 👈 ضروري لدعم i18n
from django.conf.urls import handler404, handler500
from store.views import views_errors

handler404 = views_errors.handler404
handler500 = views_errors.handler500

urlpatterns = [
    # هذا ضروري لتفعيل POST لتغيير اللغة من الفورم
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    # مسارات موقعك ستتأثر باللغة المختارة
    path('', include('store.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
)

# ملفات الميديا عند التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# تخصيص لوحة الإدارة
admin.site.site_header = "AmodGreen Administration"
admin.site.site_title = "AmodGreen Admin"
admin.site.index_title = "Bienvenue dans l'administration AmodGreen"
