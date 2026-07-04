from django.urls import path
from .views import (
    ProductListCreate, ProductDetail, 
    CombinationLookup, CombinationUpdate, PlaceOrder,
    ProductCombinationList, VariantTypeCreate, 
    VariantOptionCreate, VariantTypeDelete, VariantOptionDelete
)

urlpatterns = [
    # Storefront
    path('products/', ProductListCreate.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetail.as_view(), name='product-detail'),
    path('products/<int:pk>/combinations/lookup/', CombinationLookup.as_view(), name='combination-lookup'),
    path('orders/', PlaceOrder.as_view(), name='place-order'),
    
    
    # Admin
    path('products/<int:pk>/combinations/', ProductCombinationList.as_view(), name='product-combinations'),
    
    
    path('products/<int:pk>/variants/', VariantTypeCreate.as_view(), name='variant-type-create'),
    path('products/<int:pk>/variants/<int:vid>/', VariantTypeDelete.as_view(), name='variant-type-delete'),
    
    
    path('products/<int:pk>/variants/<int:vid>/options/', VariantOptionCreate.as_view(), name='variant-option-create'),
    path('variants/options/<int:oid>/', VariantOptionDelete.as_view(), name='variant-option-delete'),
    
    
    path('combinations/<int:pk>/', CombinationUpdate.as_view(), name='combination-update'),
]