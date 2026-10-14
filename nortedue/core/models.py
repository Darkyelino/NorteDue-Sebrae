from django.db import models
from django.contrib.auth.models import User

class Supplier(models.Model):
    monitored_by = models.ManyToManyField(User, related_name='monitored_suppliers', blank=True)
    
    cnpj = models.CharField(max_length=18, unique=True)
    razao_social = models.CharField(max_length=255, blank=True, null=True)
    nome_fantasia = models.CharField(max_length=255, blank=True, null=True)
    cnae_principal = models.CharField(max_length=255, blank=True, null=True)
    situacao_cadastral = models.CharField(max_length=50, default='ATIVA')
    uf = models.CharField(max_length=2, blank=True, null=True)
    municipio = models.CharField(max_length=100, blank=True, null=True)
    
    active_processes = models.IntegerField(default=0)
    labor_risk = models.CharField(max_length=50, default='Baixo')
    environmental_situation = models.CharField(max_length=100, default='Regular')
    score_nortedue = models.IntegerField(default=100)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.razao_social or self.cnpj} ({self.cnpj})"

class SupplierProcess(models.Model):
    supplier = models.ForeignKey(Supplier, related_name='processes', on_delete=models.CASCADE)
    numero_processo = models.CharField(max_length=100)
    tribunal = models.CharField(max_length=100)  # Ex: TRT14 (AC/RO), TJAC, TRF1
    tipo = models.CharField(max_length=50)       # Ex: Trabalhista, Ambiental, Cível
    assunto = models.TextField(blank=True, null=True)
    data_distribuicao = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=50, default='Em Andamento')

    def __str__(self):
        return f"{self.numero_processo} - {self.tribunal}"