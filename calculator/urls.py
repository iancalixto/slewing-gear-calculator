from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_datasheet, name='upload_datasheet'),
    path('save/', views.save_calculation, name='save_calculation'),
    path('suppliers/', views.suppliers, name='suppliers'),
    path('suppliers/StandardPF/', views.suppliers, {'crane_filter': 'standard_pf'}, name='suppliers_standard_pf'),
    path('suppliers/PF-XXL/', views.suppliers, {'crane_filter': 'pf_xxl'}, name='suppliers_pf_xxl'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/<int:pk>/delete/', views.delete_calculation, name='delete_calculation'),
    path('formulas/', views.formulas, name='formulas'),
]
