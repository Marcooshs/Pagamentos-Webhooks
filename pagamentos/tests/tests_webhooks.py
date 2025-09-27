from django.test import TestCase
from pagamentos.models import Pagamento

class PagamentoModelTests(TestCase):
    def test_criacao_pagamento(self):
        pagamento = Pagamento.objects.create(
            stripe_id='sess_test_001',
            valor=99.00,
            status='pago',
            email='cliente@tests.com'
        )
        self.assertEqual(Pagamento.objects.count(), 1)
        self.assertEqual(pagamento.status, 'pago')
        self.assertEqual(float(pagamento.valor), 99.00)
        self.assertEqual(pagamento.email, 'cliente@tests.com')
