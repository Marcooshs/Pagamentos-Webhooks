from decimal import Decimal
from rest_framework import serializers

class CriarPagamentoSerializer(serializers.Serializer):
    valor = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    email = serializers.EmailField()
