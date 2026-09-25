import re
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Supplier
from .services import consultar_fornecedor_real

# ==========================================
# AUTENTICAÇÃO (LOGIN / REGISTRO / LOGOUT)
# ==========================================

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


# ==========================================
# PAINEL PRINCIPAL & CONSULTA
# ==========================================

@login_required(login_url='login')
def dashboard(request):
    context = {}

    # 1. Processa a busca por CNPJ, se enviada
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
                    'cnae': dados.get('cnae'),
                    'active_processes': dados.get('active_processes', 0),
                    'labor_risk': dados.get('labor_risk', 'Baixo'),
                    'environmental_situation': dados.get('environmental_situation', 'Regular'),
                    'score_nortedue': dados.get('score_nortedue', 100),
                    'is_monitored': is_monitored
                }
            else:
                context['error'] = "CNPJ não encontrado ou limite de requisições atingido."
        else:
            context['error'] = "Por favor, informe um CNPJ válido."

    # 2. Busca a carteira de fornecedores do usuário logado para o gráfico
    monitored_suppliers = request.user.monitored_suppliers.all()
    
    context['low_risk_count'] = monitored_suppliers.filter(score_nortedue__gte=70).count()
    context['medium_risk_count'] = monitored_suppliers.filter(score_nortedue__gte=50, score_nortedue__lt=70).count()
    context['high_risk_count'] = monitored_suppliers.filter(score_nortedue__lt=50).count()
    context['total_monitored'] = monitored_suppliers.count()

    return render(request, 'dashboard.html', context)

@login_required(login_url='login')
def toggle_monitor(request):
    """ Salva o CNPJ no banco e vincula/desvincula do usuário logado """
    if request.method == 'POST':
        cnpj = request.POST.get('cnpj')
        active_processes = request.POST.get('active_processes', 0)
        labor_risk = request.POST.get('labor_risk', 'Baixo')
        environmental_situation = request.POST.get('environmental_situation', 'Regular')
        score_nortedue = request.POST.get('score_nortedue', 100)

        # Atualiza ou cria o fornecedor no SQLite
        supplier, created = Supplier.objects.update_or_create(
            cnpj=cnpj,
            defaults={
                'active_processes': active_processes,
                'labor_risk': labor_risk,
                'environmental_situation': environmental_situation,
                'score_nortedue': score_nortedue,
            }
        )

        # Adiciona ou remove da lista monitored_by do usuário
        if supplier.monitored_by.filter(id=request.user.id).exists():
            supplier.monitored_by.remove(request.user)
        else:
            supplier.monitored_by.add(request.user)

    return redirect('suppliers_list')


# ==========================================
# CARTEIRA DE FORNECEDORES MONITORADOS
# ==========================================

@login_required(login_url='login')
def suppliers_list(request):
    search_query = request.GET.get('q', '').strip()
    
    # Filtra apenas os fornecedores monitorados pelo usuário logado
    suppliers = request.user.monitored_suppliers.all()
    
    # Permite busca/filtro por CNPJ na tabela
    if search_query:
        suppliers = suppliers.filter(cnpj__icontains=search_query)

    total_suppliers = suppliers.count()
    high_risk_count = suppliers.filter(score_nortedue__lt=50).count()
    regular_count = suppliers.filter(score_nortedue__gte=70).count()

    context = {
        'suppliers': suppliers,
        'search_query': search_query,
        'total_suppliers': total_suppliers,
        'high_risk_count': high_risk_count,
        'regular_count': regular_count,
    }
    return render(request, 'suppliers.html', context)