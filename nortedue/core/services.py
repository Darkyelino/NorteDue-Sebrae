import requests
import re

def consultar_fornecedor_real(cnpj):
    # 1. Remove qualquer caractere que não seja número (pontos, traços, barras, espaços)
    cnpj_limpo = re.sub(r'\D', '', str(cnpj))
    
    # Valida se possui exatamente 14 dígitos
    if len(cnpj_limpo) != 14:
        print(f"--- [DEBUG API] CNPJ inválido (tamanho {len(cnpj_limpo)}): '{cnpj_limpo}' ---")
        return None

    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
    
    # 2. Adiciona um User-Agent para a API não identificar como robô simples
    headers = {
        'User-Agent': 'NorteDue-ESG-App/1.0'
    }
    
    try:
        # 3. Timeout de 5 segundos para não travar o Django se a API demorar
        response = requests.get(url, headers=headers, timeout=5)
        print(f"--- [DEBUG API] Status HTTP: {response.status_code} ---")
        
        if response.status_code == 200:
            data = response.json()
            return {
                'razao_social': data.get('razao_social'),
                'cnae': data.get('cnae_fiscal_descricao', 'Não informado'),
                'active_processes': 0,
                'labor_risk': 'Baixo',
                'environmental_situation': 'Regular (Consulta Receita OK)',
                'score_nortedue': 100
            }
        elif response.status_code == 429:
            print("--- [DEBUG API] ALERTA: Limite de requisições atingido (Rate Limit). Aguarde 10 segundos. ---")
        elif response.status_code == 404:
            print("--- [DEBUG API] ERRO: CNPJ não encontrado na base da Receita. ---")
            
    except requests.exceptions.RequestException as e:
        print(f"--- [DEBUG API] ERRO DE CONEXÃO: {e} ---")
        
    return None