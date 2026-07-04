from django.contrib import admin
from .models import Product, VariantType, VariantOption, Combination, Order

class ProductAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.refresh_combinations()

class VariantTypeAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.product.refresh_combinations()
        
    def delete_model(self, request, obj):
        product = obj.product
        super().delete_model(request, obj)
        product.refresh_combinations()

class VariantOptionAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.variant_type.product.refresh_combinations()

    def delete_model(self, request, obj):
        product = obj.variant_type.product
        super().delete_model(request, obj)
        product.refresh_combinations()

admin.site.register(Product, ProductAdmin)
admin.site.register(VariantType, VariantTypeAdmin)
admin.site.register(VariantOption, VariantOptionAdmin)
admin.site.register(Combination)
admin.site.register(Order)