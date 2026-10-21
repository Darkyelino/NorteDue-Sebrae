import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Supplier, SupplierProcess
from .services import consultar_fornecedor_real

# ==========================================
# AUTENTICAÇÃO
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
# DASHBOARD & BUSCA
# ==========================================
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


# ==========================================
# ADICIONAR / REMOVER DA CARTEIRA
# ==========================================
@login_required(login_url='login')
def toggle_monitor(request):
    if request.method == 'POST':
        cnpj = request.POST.get('cnpj')
        
        # Para salvar corretamente os processos reais, consultamos a API novamente
        dados = consultar_fornecedor_real(cnpj)

        if dados:
            supplier, created = Supplier.objects.update_or_create(
                cnpj=dados['cnpj'],
                defaults={
                    'razao_social': dados.get('razao_social'),
                    'nome_fantasia': dados.get('nome_fantasia'),
                    'cnae_principal': dados.get('cnae'),
                    'situacao_cadastral': dados.get('situacao_cadastral', 'ATIVA'),
                    'uf': dados.get('uf'),
                    'municipio': dados.get('municipio'),
                    'active_processes': dados.get('active_processes', 0),
                    'labor_risk': dados.get('labor_risk', 'Baixo'),
                    'environmental_situation': dados.get('environmental_situation', 'Regular'),
                    'score_nortedue': dados.get('score_nortedue', 100),
                }
            )

            # Limpa processos antigos do banco para evitar duplicidade e salva os novos
            SupplierProcess.objects.filter(supplier=supplier).delete()
            for proc in dados.get('processes_list', []):
                SupplierProcess.objects.create(
                    supplier=supplier,
                    numero_processo=proc.get('numero_processo', 'S/N'),
                    tribunal=proc.get('tribunal', 'Diversos'),
                    tipo=proc.get('tipo', '1º Grau'),
                    assunto=proc.get('assunto', 'Não especificado'),
                    status=proc.get('status', 'Mapeado')
                )

            # Vincula ou desvincula do usuário logado
            if supplier.monitored_by.filter(id=request.user.id).exists():
                supplier.monitored_by.remove(request.user)
            else:
                supplier.monitored_by.add(request.user)

    return redirect('suppliers_list')


# ==========================================
# LISTAGEM DE FORNECEDORES
# ==========================================
@login_required(login_url='login')
def suppliers_list(request):
    search_query = request.GET.get('q', '').strip()
    suppliers = request.user.monitored_suppliers.all()
    
    if search_query:
        suppliers = suppliers.filter(
            Q(cnpj__icontains=search_query) | 
            Q(razao_social__icontains=search_query)
        )

    context = {
        'suppliers': suppliers,
        'search_query': search_query,
        'total_suppliers': suppliers.count(),
        'high_risk_count': suppliers.filter(score_nortedue__lt=50).count(),
        'regular_count': suppliers.filter(score_nortedue__gte=70).count(),
    }
    return render(request, 'suppliers.html', context)


# ==========================================
# DOSSIÊ DETALHADO DO FORNECEDOR
# ==========================================
@login_required(login_url='login')
def supplier_detail(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id, monitored_by=request.user)
    
    # Atualiza sempre os dados cadastrais (e captura o QSA) em tempo real
    dados_atualizados = consultar_fornecedor_real(supplier.cnpj)
    
    if dados_atualizados:
        # Atualiza informações principais no banco
        supplier.razao_social = dados_atualizados.get('razao_social') or supplier.razao_social
        supplier.nome_fantasia = dados_atualizados.get('nome_fantasia') or supplier.nome_fantasia
        supplier.cnae_principal = dados_atualizados.get('cnae') or supplier.cnae_principal
        supplier.situacao_cadastral = dados_atualizados.get('situacao_cadastral') or supplier.situacao_cadastral
        supplier.uf = dados_atualizados.get('uf') or supplier.uf
        supplier.municipio = dados_atualizados.get('municipio') or supplier.municipio
        supplier.active_processes = dados_atualizados.get('active_processes', supplier.active_processes)
        supplier.labor_risk = dados_atualizados.get('labor_risk', supplier.labor_risk)
        supplier.environmental_situation = dados_atualizados.get('environmental_situation', supplier.environmental_situation)
        supplier.score_nortedue = dados_atualizados.get('score_nortedue', supplier.score_nortedue)
        supplier.save()

        # Atualiza a lista de processos no banco (limpa os velhos e adiciona os atuais)
        SupplierProcess.objects.filter(supplier=supplier).delete()
        for proc in dados_atualizados.get('processes_list', []):
            SupplierProcess.objects.create(
                supplier=supplier,
                numero_processo=proc.get('numero_processo', 'S/N'),
                tribunal=proc.get('tribunal', 'Diversos'),
                tipo=proc.get('tipo', '1º Grau'),
                assunto=proc.get('assunto', 'Não especificado'),
                status=proc.get('status', 'Mapeado')
            )

    # Busca a lista de processos já estruturada do banco de dados (relacionamento reverse)
    processes_list = supplier.processes.all()

    context = {
        'supplier': supplier,
        'processes_list': processes_list,
        'qsa': dados_atualizados.get('qsa', []) if dados_atualizados else []
    }
    return render(request, 'supplier_detail.html', context)