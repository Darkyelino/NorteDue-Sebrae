from django.db import models
from django.contrib.auth.models import User

class Supplier(models.Model):
    # Relacionamento: Vários usuários podem monitorar o mesmo fornecedor
    monitored_by = models.ManyToManyField(User, related_name='monitored_suppliers', blank=True)
    
    cnpj = models.CharField(max_length=18, unique=True)
    active_processes = models.IntegerField(default=0)
    labor_risk = models.CharField(max_length=50, default='Baixo')
    environmental_situation = models.CharField(max_length=100, default='Regular')
    score_nortedue = models.IntegerField(default=100)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.cnpj} - Score: {self.score_nortedue}"