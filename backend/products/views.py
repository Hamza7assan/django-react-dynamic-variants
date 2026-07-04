from django.shortcuts import render
from rest_framework import generics
from .models import Product, Combination, VariantType, VariantOption, Order
from .serializers import ProductSerializer, ProductDetailSerializer, CombinationSerializer, CombinationListSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404

class ProductListCreate(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        product = serializer.save()
        product.refresh_combinations()


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if Order.objects.filter(combination__product=instance).exists():
            return Response(
                {"error": "Cannot delete the product because there are invoices and purchase orders associated with it."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)
    
    
class CombinationUpdate(generics.UpdateAPIView):
    queryset = Combination.objects.all()
    serializer_class = CombinationSerializer
    
    
class ProductCombinationList(generics.ListAPIView):
    serializer_class = CombinationListSerializer
    def get_queryset(self):
        return Combination.objects.filter(product_id=self.kwargs['pk'])


class VariantTypeCreate(APIView):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        name = request.data.get('name')
        options = request.data.get('options', []) 

        if not name:
            return Response({"error": "Variant type name is required"}, status=status.HTTP_400_BAD_REQUEST)

        vt = VariantType.objects.create(product=product, name=name)
        
        for opt_value in options:
            VariantOption.objects.create(variant_type=vt, value=opt_value)
        product.refresh_combinations()
        return Response({"message": "Variant type and options created successfully", "variant_id": vt.id}, status=status.HTTP_201_CREATED)


class VariantOptionCreate(APIView):
    def post(self, request, pk, vid):
        vt = get_object_or_404(VariantType, pk=vid, product_id=pk)
        value = request.data.get('option')

        if not value:
            return Response({"error": "Option value is required"}, status=status.HTTP_400_BAD_REQUEST)

        opt = VariantOption.objects.create(variant_type=vt, value=value)
        vt.product.refresh_combinations()
        return Response({"message": "Option added successfully", "option_id": opt.id}, status=status.HTTP_201_CREATED)


class VariantTypeDelete(generics.DestroyAPIView):
    queryset = VariantType.objects.all()
    lookup_url_kwarg = 'vid'
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        product = instance.product

        if Order.objects.filter(combination__product=product).exists():
            return Response(
                {"error": "Cannot delete the product because there are invoices and purchase orders associated with it."},
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.delete()
        product.refresh_combinations()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VariantOptionDelete(generics.DestroyAPIView):
    queryset = VariantOption.objects.all()
    lookup_url_kwarg = 'oid'     
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        product = instance.variant_type.product

        if Order.objects.filter(combination__options=instance).exists():
            return Response(
                {"error": "Cannot delete the product because there are invoices and purchase orders associated with it."},
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.delete()
        product.refresh_combinations()
        return Response(status=status.HTTP_204_NO_CONTENT)       
    
    
#################################################################################################  
       
       
class CombinationLookup(APIView):
      def post(self, request, pk):
        
        option_ids = request.data.get('option_ids', [])

        if not isinstance(option_ids, list):
            return Response({"error": "Please provide a valid list of option_ids"}, status=status.HTTP_400_BAD_REQUEST)

        combinations = Combination.objects.filter(product_id=pk).prefetch_related('options')

        for combo in combinations:
            combo_option_ids = [opt.id for opt in combo.options.all()]
            
            if sorted(combo_option_ids) == sorted(option_ids):
                final_price = combo.product.base_price + combo.additional_price
                
                return Response({
                    "combination_id": combo.id,
                    "additional_price": str(combo.additional_price),
                    "final_price": str(final_price),
                    "stock": combo.stock,
                    "in_stock": combo.stock > 0
                }, status=status.HTTP_200_OK)

        return Response(
            {"error": "Combination not found for the selected options"}, 
            status=status.HTTP_404_NOT_FOUND
        )


#placing an order safely (atomic deduction)
class PlaceOrder(APIView):
    def post(self, request):
        combo_id = request.data.get('combination_id')
        quantity = request.data.get('quantity')

        if not combo_id or not isinstance(quantity, int) or quantity <= 0:
            return Response({"error": "Invalid combination_id or quantity"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            #start a database transaction
            with transaction.atomic():
                # select_for_update() locks the row so no other request can modify this combo until this transaction end
                combo = Combination.objects.select_for_update().get(id=combo_id)

                if combo.stock >= quantity:
                    combo.stock -= quantity
                    combo.save()

                    final_price = combo.product.base_price + combo.additional_price
                    total = final_price * quantity
                    
                    order = Order.objects.create(
                        combination=combo,
                        quantity=quantity,
                        total_price=total
                    )

                    return Response({
                        "order_id": order.id,
                        "total": str(total),
                        "status": "confirmed"
                    }, status=status.HTTP_201_CREATED)
                
                else:
                    # if stock is insufficient ----->  return 422 Unprocessable Entity 
                    return Response({
                        "error": f"Insufficient stock. Requested: {quantity}, Available: {combo.stock}"
                    }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        except Combination.DoesNotExist:
            return Response({"error": "Combination not found"}, status=status.HTTP_404_NOT_FOUND) 
        
        
        
        
