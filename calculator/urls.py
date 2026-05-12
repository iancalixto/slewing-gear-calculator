from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('save/', views.save_calculation, name='save_calculation'),
    path('suppliers/', views.suppliers, name='suppliers'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/<int:pk>/delete/', views.delete_calculation, name='delete_calculation'),
    path('formulas/', views.formulas, name='formulas'),
]
