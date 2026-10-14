import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Supplier, SupplierProcess
from .services import consultar_fornecedor_real

# AUTENTICAÇÃO
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

# DASHBOARD & BUSCA
@login_required(login_url='login')
def dashboard(request):
    context = {}
    if request.method == 'POST':
        raw_cnpj = request.POST.get('cnpj', '')
        cnpj_limpo = re.sub(r'\D', '', str(raw_cnpj))
        
        if cnpj_limpo:
            dados = consultar_fornecedor_real(cnpj_limpo)
            if dados:
                supplier_obj = Supplier.objects.filter(cnpj=cnpj_limpo).first()
                is_monitored = False
                if supplier_obj and supplier_obj.monitored_by.filter(id=request.user.id).exists():
                    is_monitored = True

                context['searched_data'] = {
                    'cnpj': cnpj_limpo,
                    'razao_social': dados.get('razao_social'),
                    'nome_fantasia': dados.get('nome_fantasia'),
                    'cnae': dados.get('cnae'),
                    'situacao_cadastral': dados.get('situacao_cadastral'),
                    'uf': dados.get('uf'),
                    'municipio': dados.get('municipio'),
                    'active_processes': dados.get('active_processes', 0),
                    'processes_list': dados.get('processes_list', []),
                    'labor_risk': dados.get('labor_risk', 'Baixo'),
                    'environmental_situation': dados.get('environmental_situation', 'Regular'),
                    'score_nortedue': dados.get('score_nortedue', 100),
                    'is_monitored': is_monitored
                }
            else:
                context['error'] = "CNPJ não encontrado ou indisponível na Receita Federal."
        else:
            context['error'] = "Por favor, informe um CNPJ válido."

    monitored_suppliers = request.user.monitored_suppliers.all()
    context['low_risk_count'] = monitored_suppliers.filter(score_nortedue__gte=70).count()
    context['medium_risk_count'] = monitored_suppliers.filter(score_nortedue__gte=50, score_nortedue__lt=70).count()
    context['high_risk_count'] = monitored_suppliers.filter(score_nortedue__lt=50).count()
    context['total_monitored'] = monitored_suppliers.count()

    return render(request, 'dashboard.html', context)

# ADICIONAR / REMOVER DA CARTEIRA
@login_required(login_url='login')
def toggle_monitor(request):
    if request.method == 'POST':
        cnpj = request.POST.get('cnpj')
        razao_social = request.POST.get('razao_social')
        nome_fantasia = request.POST.get('nome_fantasia')
        cnae_principal = request.POST.get('cnae')
        situacao_cadastral = request.POST.get('situacao_cadastral', 'ATIVA')
        uf = request.POST.get('uf')
        municipio = request.POST.get('municipio')
        active_processes = int(request.POST.get('active_processes', 0))
        labor_risk = request.POST.get('labor_risk', 'Baixo')
        environmental_situation = request.POST.get('environmental_situation', 'Regular')
        score_nortedue = int(request.POST.get('score_nortedue', 100))

        supplier, created = Supplier.objects.update_or_create(
            cnpj=cnpj,
            defaults={
                'razao_social': razao_social,
                'nome_fantasia': nome_fantasia,
                'cnae_principal': cnae_principal,
                'situacao_cadastral': situacao_cadastral,
                'uf': uf,
                'municipio': municipio,
                'active_processes': active_processes,
                'labor_risk': labor_risk,
                'environmental_situation': environmental_situation,
                'score_nortedue': score_nortedue,
            }
        )

        if supplier.monitored_by.filter(id=request.user.id).exists():
            supplier.monitored_by.remove(request.user)
        else:
            supplier.monitored_by.add(request.user)

    return redirect('suppliers_list')

# LISTAGEM DE FORNECEDORES
@login_required(login_url='login')
def suppliers_list(request):
    search_query = request.GET.get('q', '').strip()
    suppliers = request.user.monitored_suppliers.all()
    
    if search_query:
        suppliers = suppliers.filter(
            models.Q(cnpj__icontains=search_query) | 
            models.Q(razao_social__icontains=search_query)
        )

    context = {
        'suppliers': suppliers,
        'search_query': search_query,
        'total_suppliers': suppliers.count(),
        'high_risk_count': suppliers.filter(score_nortedue__lt=50).count(),
        'regular_count': suppliers.filter(score_nortedue__gte=70).count(),
    }
    return render(request, 'suppliers.html', context)

# DOSSIÊ DETALHADO DO FORNECEDOR
@login_required(login_url='login')
def supplier_detail(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id, monitored_by=request.user)
    
    # Se necessário, realiza atualização de dados cadastrais
    dados_atualizados = consultar_fornecedor_real(supplier.cnpj)
    processes_list = []
    
    if dados_atualizados:
        supplier.razao_social = dados_atualizados.get('razao_social') or supplier.razao_social
        supplier.nome_fantasia = dados_atualizados.get('nome_fantasia') or supplier.nome_fantasia
        supplier.cnae_principal = dados_atualizados.get('cnae') or supplier.cnae_principal
        supplier.situacao_cadastral = dados_atualizados.get('situacao_cadastral') or supplier.situacao_cadastral
        supplier.uf = dados_atualizados.get('uf') or supplier.uf
        supplier.municipio = dados_atualizados.get('municipio') or supplier.municipio
        supplier.save()
        processes_list = dados_atualizados.get('processes_list', [])

    context = {
        'supplier': supplier,
        'processes_list': processes_list,
        'qsa': dados_atualizados.get('qsa', []) if dados_atualizados else []
    }
    return render(request, 'supplier_detail.html', context)