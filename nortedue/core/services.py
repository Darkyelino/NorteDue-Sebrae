import requests
import re

def consultar_fornecedor_real(cnpj):
    cnpj_limpo = re.sub(r'\D', '', str(cnpj))
    
    # 1. Consulta Dados Cadastrais Oficiais (BrasilAPI - Gratuita)
    url_brasilapi = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
    
    try:
        resp_cad = requests.get(url_brasilapi, timeout=10)
        
        if resp_cad.status_code != 200:
            return None
            
        data = resp_cad.json()
        situacao = data.get('descricao_situacao_cadastral', 'ATIVA')
        
        occurrences = [] # Lista unificada de ocorrências / autuações / processos

        # ---------------------------------------------------------
        # 2. CONSULTA REAL DE EMBARGOS E AUTUAÇÕES AMBIENTAIS (IBAMA)
        # ---------------------------------------------------------
        environmental_situation = "Regular (Sem Embargos Ativos)"
        try:
            # Endpoint público de Dados Abertos do IBAMA para Embargos por CNPJ
            url_ibama = f"https://dadosabertos.ibama.gov.br/api/3/action/datastore_search?resource_id=e703ed82-12f5-4f40-8fdd-b28e51a66699&q={cnpj_limpo}"
            resp_ibama = requests.get(url_ibama, timeout=6)
            
            if resp_ibama.status_code == 200:
                ibama_data = resp_ibama.json()
                records = ibama_data.get('result', {}).get('records', [])
                
                if records:
                    environmental_situation = f"Alerta: {len(records)} Embargo(s) IBAMA"
                    for rec in records[:10]: # Limita aos 10 registros mais recentes
                        occurrences.append({
                            'numero_processo': rec.get('num_term_embargo_autuacao', 'Embargo IBAMA'),
                            'tribunal': 'IBAMA / Órgão Ambiental',
                            'tipo': 'Ambiental',
                            'assunto': rec.get('des_infra_infraestrutura') or rec.get('nom_municipio', 'Autuação/Embargo Ambiental'),
                            'status': 'Embargado / Autuado'
                        })
        except Exception as e_ibama:
            print(f"Erro na consulta IBAMA: {e_ibama}")

        # ---------------------------------------------------------
        # 3. CONSULTA REAL DE RISCO TRABALHISTA E SANÇÕES (CGU / MTE)
        # ---------------------------------------------------------
        labor_risk = "Baixo"
        try:
            # Consulta sanções no Portal de Dados da CGU (CEIS / CNEP)
            url_cgu = f"https://api.portaldatransparencia.gov.br/api-de-dados/ceis?cnpjSancionado={cnpj_limpo}&pagina=1"
            headers_cgu = {"accept": "*/*"}
            resp_cgu = requests.get(url_cgu, headers=headers_cgu, timeout=6)
            
            if resp_cgu.status_code == 200:
                cgu_data = resp_cgu.json()
                if isinstance(cgu_data, list) and len(cgu_data) > 0:
                    labor_risk = "Alto (Empresa Sancionada / Inidônea)"
                    for sancao in cgu_data[:5]:
                        occurrences.append({
                            'numero_processo': sancao.get('numeroProcesso', 'Sanção CGU'),
                            'tribunal': sancao.get('orgaoSancionador', {}).get('nome', 'CGU / MTE'),
                            'tipo': 'Trabalhista / Administrativo',
                            'assunto': sancao.get('tipoSancao', {}).get('descricao', 'Inidoneidade / Sanção Federal'),
                            'status': 'Sancionado'
                        })
        except Exception as e_cgu:
            print(f"Erro na consulta CGU/MTE: {e_cgu}")

        # ---------------------------------------------------------
        # 4. CÁLCULO DINÂMICO DE SCORE NORTEDUE REAL
        # ---------------------------------------------------------
        score = 100
        if situacao != 'ATIVA':
            score -= 40
        if "Alerta" in environmental_situation:
            score -= 35
        if labor_risk != "Baixo":
            score -= 35
        if len(occurrences) > 0 and score == 100:
            score -= 20

        return {
            'cnpj': cnpj_limpo,
            'razao_social': data.get('razao_social', 'Razão Social não informada'),
            'nome_fantasia': data.get('nome_fantasia') or data.get('razao_social'),
            'cnae': data.get('cnae_fiscal_descricao', 'Não Informado'),
            'situacao_cadastral': situacao,
            'uf': data.get('uf', 'AC'),
            'municipio': data.get('municipio', ''),
            'qsa': data.get('qsa', []),
            'active_processes': len(occurrences),
            'processes_list': occurrences,
            'labor_risk': labor_risk,
            'environmental_situation': environmental_situation,
            'score_nortedue': max(score, 10)
        }

    except Exception as e:
        print(f"Erro na consulta geral: {e}")
        return None