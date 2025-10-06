import stripe
from uuid import uuid4
from decimal import Decimal
from django.conf import settings

def _to_cents(valor) -> int:
    if isinstance(valor, float):
        valor = Decimal(str(valor))
    elif not isinstance(valor, Decimal):
        valor = Decimal(valor)
    return int((valor * 100).quantize(Decimal('1')))

def criar_checkout(valor, email):
    """
    Se DEMO_MODE=True, retorna uma URL local que simula o checkout.
    Caso contrário, cria sessão real no Stripe.
    """
    if settings.DEMO_MODE or not settings.STRIPE_SECRET_KEY:
        sid = f"sess_demo_{uuid4().hex[:10]}"
        # vamos passar valor e email na query string p/ a view de simulação
        url = f"{settings.SITE_URL}/api/demo/pay/{sid}?valor={float(valor)}&email={email}"
        return {"url": url, "id": sid}

    # --- Modo real Stripe ---
    stripe.api_key = settings.STRIPE_SECRET_KEY.strip()
    amount = _to_cents(valor)
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'brl',
                'unit_amount': amount,
                'product_data': {'name': 'Pagamento Teste'},
            },
            'quantity': 1,
        }],
        mode='payment',
        customer_email=email,
        success_url=f'{settings.SITE_URL}/docs',   # ajuste se quiser
        cancel_url=f'{settings.SITE_URL}/docs',
    )
    return {'url': session.url, 'id': session.id}
