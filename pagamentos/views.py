# pagamentos/views.py
from decimal import Decimal
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import CriarPagamentoSerializer
from .stripe_service import criar_checkout
from .models import Pagamento
import stripe


class CriarPagamentoAPIView(APIView):
    """
    POST { valor, email } -> { url, session_id }
    - DEMO_MODE=True: público (sem JWT) e simula checkout/local
    - DEMO_MODE=False: exige JWT e usa Stripe real
    """
    permission_classes = [AllowAny] if getattr(settings, "DEMO_MODE", False) else [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CriarPagamentoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        valor = serializer.validated_data["valor"]
        email = serializer.validated_data["email"]

        try:
            result = criar_checkout(valor, email)
        except stripe.error.StripeError as e:
            return Response(
                {"detail": "Erro ao criar sessão de checkout no Stripe.", "error": str(e)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if getattr(settings, "DEMO_MODE", False):
            Pagamento.objects.update_or_create(
                stripe_id=result["id"],
                defaults={"status": "pendente", "valor": valor, "email": email},
            )

        return Response({"url": result["url"], "session_id": result["id"]}, status=status.HTTP_201_CREATED)


class DemoPayView(APIView):
    """
    GET /api/demo/pay/<sid>?valor=99.9&email=foo@bar  (DEMO only)
    Confirma o "pagamento" simulando o webhook e marca como 'pago'.
    """
    permission_classes = [AllowAny]

    def get(self, request, sid, *args, **kwargs):
        if not getattr(settings, "DEMO_MODE", False):
            return Response({"detail": "Demo desativado."}, status=status.HTTP_404_NOT_FOUND)

        try:
            valor = Decimal(request.GET.get("valor", "0"))
        except Exception:
            return Response({"detail": "Valor inválido."}, status=status.HTTP_400_BAD_REQUEST)

        email = request.GET.get("email") or ""
        if not email:
            return Response({"detail": "Email é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        pagamento, _ = Pagamento.objects.update_or_create(
            stripe_id=sid,
            defaults={"status": "pago", "valor": valor, "email": email},
        )
        return Response(
            {
                "status": pagamento.status,
                "stripe_id": pagamento.stripe_id,
                "valor": float(pagamento.valor),
                "email": pagamento.email,
            },
            status=status.HTTP_200_OK,
        )


class HealthAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class AuthPingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({"ok": True, "user": request.user.username}, status=status.HTTP_200_OK)
