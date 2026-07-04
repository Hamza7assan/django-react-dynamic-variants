from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    
    # Route any request starting with /api to --> ("products.urls" file)
    path('api/', include('products.urls')),
]