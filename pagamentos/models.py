from django.db import models

class Pagamento(models.Model):
    stripe_id = models.CharField(max_length=200, unique=True)
    status = models.CharField(max_length=50)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    email = models.EmailField()
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.email} - R$ {self.valor} - {self.status}'
