# pagamentos/urls.py
from django.urls import path
from django.conf import settings
from .views import CriarPagamentoAPIView, HealthAPIView
from .views import AuthPingAPIView


urlpatterns = [
    path('criar/', CriarPagamentoAPIView.as_view(), name='criar-pagamento'),
    path('health/', HealthAPIView.as_view(), name='health'),
    path('auth-ping/', AuthPingAPIView.as_view(), name='auth-ping'),
]

# rota demo só se DEMO_MODE=True
if getattr(settings, "DEMO_MODE", False):
    from .views import DemoPayView
    urlpatterns += [
        path('demo/pay/<str:sid>/', DemoPayView.as_view(), name='demo-pay'),
    ]

# webhook (opcional p/ modo real)
from .webhooks import webhook
urlpatterns += [path('webhook/', webhook, name='stripe-webhook')]
