from django.contrib import admin
from .models import Pagamento

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('email', 'valor', 'status', 'stripe_id', 'criado_em')
    search_fields = ('email', 'stripe_id', 'status')
    list_filter = ('status', 'criado_em')
