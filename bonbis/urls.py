from django.urls import include, path, re_path
from django.contrib import admin
from bis.views import bis, companies, passengers

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
	path(r'admin/', admin.site.urls),
    path('', include('bis.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('accounts/signup/', bis.SignUpView.as_view(), name='signup'),
    path('accounts/signup/companies/forms/', companies.register_companies, name='company_signup'),
    path('accounts/signup/companies/', companies.CompanySignUpView.as_view(), name='company_signup1'),
    path('accounts/signup/passengers/', passengers.PassengerSignUpView.as_view(), name='passenger_signup'),
    path('qr_code/', include('qr_code.urls', namespace="qr_code")),
]


admin.site.site_header = "Administration de BusHaiti"
admin.site.site_title = "BusHaiti"
admin.site.index_title = "Bienvenue Admin"

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
