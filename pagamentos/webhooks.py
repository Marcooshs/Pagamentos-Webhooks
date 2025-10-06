import os
import json
import logging
import stripe
from django.conf import settings
from django.http import HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from .models import Pagamento

logger = logging.getLogger(__name__)

VERIFY_SIGNATURE = os.getenv('STRIPE_VERIFY_SIGNATURE', 'True') == 'True'

@csrf_exempt
def webhook(request: HttpRequest):
    payload = request.body

    if VERIFY_SIGNATURE:
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        if not sig_header:
            logger.warning('Stripe webhook sem assinatura')
            return HttpResponse(status=400)
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except Exception as e:
            logger.exception('Falha ao validar webhook Stripe: %s', e)
            return HttpResponse(status=400)
    else:
        try:
            event = json.loads(payload or b'{}')
        except Exception:
            return HttpResponse(status= 400)

    if event.get('type') == 'checkout.session.completed':
        session = event['data']['object']
        Pagamento.objects.update_or_create(
            stripe_id=session.get('id', ''),
            defaults={
                'status': 'pago',
                'valor': (session.get('amount_total') or 0) / 100,
                'email': session.get('customer_email') or '',
            }
        )
        logger.info('Pagamento registrado via webhook: %s', session.get('id'))

    return HttpResponse(status=200)
