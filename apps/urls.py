from django.urls import path

from apps.views import FetchUserAPIView, FetchCompanyDataAPIView, CompanyKorxonaAPIView, FilteredCompanyKorxonaAPIView

urlpatterns = [
    path('login/', FetchUserAPIView.as_view(), name='login'),
    path('company-mtu/', FetchCompanyDataAPIView.as_view(), name='company-mtu'),
    path('company-korxona/', CompanyKorxonaAPIView.as_view(), name='company-korxona'),
    path('company-korxona-filter/<int:id>/<str:is_active>/', FilteredCompanyKorxonaAPIView.as_view(),
         name='company-korxona-filter-by-id-active')
]
