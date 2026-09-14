import re
from .models import Supplier
from .services import consultar_fornecedor_real
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required

def dashboard(request):
    context = {}
    
    if request.method == 'POST':
        raw_cnpj = request.POST.get('cnpj', '')
        cnpj_limpo = re.sub(r'\D', '', str(raw_cnpj))  # Sanitiza deixando apenas dígitos
        
        if cnpj_limpo:
            dados = consultar_fornecedor_real(cnpj_limpo)
            
            if dados:
                supplier, created = Supplier.objects.update_or_create(
                    cnpj=cnpj_limpo,  # Busca e salva sempre sanitizado
                    defaults={
                        'active_processes': dados.get('active_processes', 0),
                        'labor_risk': dados.get('labor_risk', 'Baixo'),
                        'environmental_situation': dados.get('environmental_situation', 'Regular'),
                        'score_nortedue': dados.get('score_nortedue', 100),
                    }
                )
                context['supplier'] = supplier
                context['razao_social'] = dados.get('razao_social')
                context['cnae'] = dados.get('cnae')
            else:
                context['error'] = "CNPJ não encontrado ou limite de requisições atingido."
        else:
            context['error'] = "Por favor, informe um CNPJ válido."

    return render(request, 'dashboard.html', context)

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

@login_required(login_url='login')
def dashboard(request):
    context = {}
    if request.method == 'POST':
        raw_cnpj = request.POST.get('cnpj', '')
        cnpj_limpo = re.sub(r'\D', '', str(raw_cnpj))
        
        if cnpj_limpo:
            dados = consultar_fornecedor_real(cnpj_limpo)
            if dados:
                supplier, created = Supplier.objects.update_or_create(
                    cnpj=cnpj_limpo,
                    defaults={
                        'active_processes': dados.get('active_processes', 0),
                        'labor_risk': dados.get('labor_risk', 'Baixo'),
                        'environmental_situation': dados.get('environmental_situation', 'Regular'),
                        'score_nortedue': dados.get('score_nortedue', 100),
                    }
                )
                context['supplier'] = supplier
                context['razao_social'] = dados.get('razao_social')
                context['cnae'] = dados.get('cnae')
            else:
                context['error'] = "CNPJ não encontrado ou limite de requisições atingido."
        else:
            context['error'] = "Por favor, informe um CNPJ válido."

    return render(request, 'dashboard.html', context)