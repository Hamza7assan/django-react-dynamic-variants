from django.db import models
import itertools
from django.db.models import ProtectedError

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True, max_length=1024)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name    
    
    def refresh_combinations(self):
        
        variant_types = self.variant_types.all()

        # edge Case 1  :  Simple Product (no variants)
        if not variant_types.exists():
            if not self.combinations.exists():
                Combination.objects.create(product=self, stock=0, additional_price=0.00)
            # clean up any residual combinations that might have options linked by mistake
            for combo in self.combinations.exclude(options__isnull=True):
                try:
                    combo.delete()
                except ProtectedError:
                    combo.stock = 0
                    combo.save()
            return

        options_by_type = [list(vt.options.all()) for vt in variant_types]
        
        # edge Case 2: incomplete variants (Waiting for options to be added)
        if any(not options for options in options_by_type):
            return 
        
        # 1 Calculate the mathematically correct combinations
        all_possible_combos = list(itertools.product(*options_by_type))
        valid_option_id_sets = [set(opt.id for opt in combo) for combo in all_possible_combos]

        existing_combos = list(self.combinations.all())
        
        # 2 Delete or Archive obsolete combinations (Options were removed)
        for combo in existing_combos:
            combo_option_ids = set(combo.options.values_list('id', flat=True))
            if combo_option_ids not in valid_option_id_sets:
                try:
                    combo.delete()
                except ProtectedError:
                    combo.stock = 0
                    combo.save()

        # 3 Create ONLY the missing combinations (Preserving stock/prices of existing ones)
        # Fetch current combinations again after deletion/archiving
        current_option_id_sets = [set(c.options.values_list('id', flat=True)) for c in self.combinations.all()]
        
        for combo_options in all_possible_combos:
            combo_ids = set(opt.id for opt in combo_options)
            if combo_ids not in current_option_id_sets:
                new_combo = Combination.objects.create(product=self, stock=0, additional_price=0.00)
                new_combo.options.set(combo_options)
    

class VariantType(models.Model):
    product = models.ForeignKey(Product, related_name='variant_types', on_delete=models.CASCADE)
    name = models.CharField(max_length=100) 

    def __str__(self):
        return f"{self.product.name} - {self.name}"
    
    

class VariantOption(models.Model):
    variant_type = models.ForeignKey(VariantType, related_name='options', on_delete=models.CASCADE)
    value = models.CharField(max_length=100) 
    
    def __str__(self):
        return f"{self.variant_type.name}: {self.value}"
    
    

class Combination(models.Model):
    product = models.ForeignKey(Product, related_name='combinations', on_delete=models.CASCADE)
    options = models.ManyToManyField(VariantOption)
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"SKU for {self.product.name} || Combo ID: {self.id}"  
    
    
    
class Order(models.Model):
    combination = models.ForeignKey(Combination, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} || Combo: {self.combination.id} || quantity: {self.quantity}"  
    
      
    
    
