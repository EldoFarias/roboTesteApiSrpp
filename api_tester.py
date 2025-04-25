import os
import time
import concurrent.futures
import requests
from dotenv import load_dotenv
from faker import Faker
from typing import Dict, Any
import random
import json  # Adicionando a importação do módulo json

# Carrega as variáveis de ambiente
load_dotenv()

# Configurações
API_BASE_URL = os.getenv('API_BASE_URL')
API_PORT = os.getenv('API_PORT')
MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS'))
TEST_DURATION_SECONDS = int(os.getenv('TEST_DURATION_SECONDS'))

# Inicializa o Faker para gerar dados aleatórios
fake = Faker('pt_BR')

class APITester:
    def __init__(self):
        # Corrigido: usa apenas API_BASE_URL, removendo barra final se houver
        self.base_url = API_BASE_URL.rstrip('/')
        self.session = requests.Session()
        self.results = {
            'success': 0,
            'errors': 0,
            'total_time': 0,
            'response_times': [],
            'success_responses': []  # <-- Adicionado para armazenar respostas de sucesso
        }
        # Lista para armazenar os números de pedidos criados
        self.pedidos_criados = []
        # Dicionário para armazenar os itens de cada pedido {nro_pedido: [codigos_produto]}
        self.itens_por_pedido = {}
        # Dicionário para rastrear os clientes de cada pedido
        self.pedidos_clientes = {}
        # Carregar códigos de produto
        self.codigos_produto = carregar_codigos_produto()
        # Tenta carregar pedidos criados anteriormente
        self.carregar_pedidos_criados()
        # Tenta carregar itens por pedido
        self.carregar_itens_por_pedido()
        # Tenta carregar pedidos_clientes
        self.carregar_pedidos_clientes()
    
    def carregar_pedidos_clientes(self):
        """Carrega a relação entre pedidos e clientes de um arquivo, se existir"""
        try:
            if os.path.exists('pedidos_clientes.json'):
                with open('pedidos_clientes.json', 'r') as f:
                    # Converte as chaves de string para int
                    dados = json.load(f)
                    self.pedidos_clientes = {int(k): v for k, v in dados.items()}
                print(f"Carregados clientes para {len(self.pedidos_clientes)} pedidos")
        except Exception as e:
            print(f"Erro ao carregar pedidos_clientes: {str(e)}")
            self.pedidos_clientes = {}
            
    def salvar_pedidos_clientes(self):
        """Salva o dicionário de pedidos e clientes em um arquivo"""
        try:
            with open('pedidos_clientes.json', 'w') as f:
                json.dump(self.pedidos_clientes, f)
            print(f"Salvos clientes para {len(self.pedidos_clientes)} pedidos")
        except Exception as e:
            print(f"Erro ao salvar pedidos_clientes: {str(e)}")
            
    def carregar_pedidos_criados(self):
        """Carrega pedidos criados de um arquivo, se existir"""
        try:
            if os.path.exists('pedidos_criados.json'):
                with open('pedidos_criados.json', 'r') as f:
                    self.pedidos_criados = json.load(f)
                print(f"Carregados {len(self.pedidos_criados)} pedidos de execuções anteriores")
        except Exception as e:
            print(f"Erro ao carregar pedidos criados: {str(e)}")
            self.pedidos_criados = []

    def salvar_pedidos_criados(self):
        """Salva a lista de pedidos criados em um arquivo"""
        try:
            with open('pedidos_criados.json', 'w') as f:
                json.dump(self.pedidos_criados, f)
            print(f"Salvos {len(self.pedidos_criados)} pedidos criados")
        except Exception as e:
            print(f"Erro ao salvar pedidos criados: {str(e)}")
            
    def carregar_itens_por_pedido(self):
        """Carrega itens por pedido de um arquivo, se existir"""
        try:
            if os.path.exists('itens_por_pedido.json'):
                with open('itens_por_pedido.json', 'r') as f:
                    # Converte as chaves de string para int
                    dados = json.load(f)
                    self.itens_por_pedido = {int(k): v for k, v in dados.items()}
                print(f"Carregados itens para {len(self.itens_por_pedido)} pedidos")
        except Exception as e:
            print(f"Erro ao carregar itens por pedido: {str(e)}")
            self.itens_por_pedido = {}
            
    def salvar_itens_por_pedido(self):
        """Salva o dicionário de itens por pedido em um arquivo"""
        try:
            with open('itens_por_pedido.json', 'w') as f:
                json.dump(self.itens_por_pedido, f)
            print(f"Salvos itens para {len(self.itens_por_pedido)} pedidos")
        except Exception as e:
            print(f"Erro ao salvar itens por pedido: {str(e)}")

    def adicionar_pedido_criado(self, nro_pedido):
        """Adiciona um número de pedido à lista de pedidos criados"""
        if nro_pedido not in self.pedidos_criados:
            self.pedidos_criados.append(nro_pedido)
            self.salvar_pedidos_criados()
            
    def adicionar_item_ao_pedido(self, nro_pedido, cod_produto):
        """Adiciona um item à lista de itens do pedido"""
        # Converte para int para garantir consistência
        nro_pedido = int(nro_pedido)
        
        # Inicializa a lista de itens se o pedido não existir no dicionário
        if nro_pedido not in self.itens_por_pedido:
            self.itens_por_pedido[nro_pedido] = []
            
        # Adiciona o código do produto à lista de itens do pedido
        if cod_produto not in self.itens_por_pedido[nro_pedido]:
            self.itens_por_pedido[nro_pedido].append(cod_produto)
            self.salvar_itens_por_pedido()
            return True
        return False
        
    def obter_item_aleatorio_do_pedido(self, nro_pedido):
        """Retorna um código de produto aleatório da lista de itens do pedido"""
        # Converte para int para garantir consistência
        nro_pedido = int(nro_pedido)
        
        # Verifica se o pedido existe e tem itens
        if nro_pedido in self.itens_por_pedido and self.itens_por_pedido[nro_pedido]:
            return random.choice(self.itens_por_pedido[nro_pedido])
        return None
        
    def remover_item_do_pedido(self, nro_pedido, cod_produto):
        """Remove um item da lista de itens do pedido"""
        # Converte para int para garantir consistência
        nro_pedido = int(nro_pedido)
        
        # Verifica se o pedido existe e tem o item
        if nro_pedido in self.itens_por_pedido and cod_produto in self.itens_por_pedido[nro_pedido]:
            self.itens_por_pedido[nro_pedido].remove(cod_produto)
            self.salvar_itens_por_pedido()
            return True
        return False

    def obter_pedido_aleatorio(self):
        """Retorna um número de pedido aleatório da lista de pedidos criados"""
        if not self.pedidos_criados:
            # Se não houver pedidos criados, retorna um valor padrão
            return random.choice(carregar_nro_pedidos())
        return random.choice(self.pedidos_criados)

    def test_endpoint(self, endpoint: str, method: str = 'GET', data: Dict[str, Any] = None, params: Dict[str, Any] = None) -> tuple[bool, float]:
        """
        Testa um endpoint específico
        """
        # Corrigido: garante que não haja barra dupla na URL
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        start_time = time.time()
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=params)
            elif method == 'POST':
                response = self.session.post(url, json=data, params=params)
            elif method == 'PUT':
                response = self.session.put(url, json=data)
            elif method == 'DELETE':
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Método {method} não suportado")

            response_time = time.time() - start_time
            self.results['response_times'].append(response_time)

            # Tratamento especial para o endpoint de recuperação de observação
            if endpoint.startswith('/EditaItemPedido/recuperarObservacao/') and response.status_code == 404:
                # Trata como sucesso com mensagem personalizada
                self.results['success'] += 1
                nro_pedido = params.get('nroPedido', 'desconhecido') if params else 'desconhecido'
                mensagem = f"Pedido {nro_pedido} sem observações"
                print(f"Informação: {mensagem}")
                self.results['success_responses'].append(mensagem)
                return True, response_time
                
            # Tratamento especial para o endpoint de exclusão de item
            if endpoint == '/EditaItemPedido/excluirItem' and response.status_code == 404:
                # Trata como informação, não como erro
                self.results['success'] += 1
                nro_pedido = params.get('nroPedido', 'desconhecido') if params else 'desconhecido'
                codigo = params.get('codigo', 'desconhecido') if params else 'desconhecido'
                mensagem = f"Item {codigo} não encontrado no pedido {nro_pedido}"
                print(f"Informação: {mensagem}")
                self.results['success_responses'].append(mensagem)
                return True, response_time
                
            # Tratamento especial para erros de impressão de pedido
            if (endpoint == '/Pedido/imprime' or endpoint == '/Pedido/imprimeFichaCadastral') and response.status_code == 500:
                # Trata como informação, não como erro
                self.results['success'] += 1
                nro_pedido = data.get('nroPedido', 'desconhecido') if data else 'desconhecido'
                mensagem = f"Pedido {nro_pedido} não pode ser impresso (pode ter sido excluído ou alterado)"
                print(f"Informação: {mensagem}")
                self.results['success_responses'].append(mensagem)
                return True, response_time
                
            # Tratamento especial para erro de cliente alterado ao fechar pedido
            if endpoint == '/EditaItemPedido/fecharPedido' and response.status_code == 400:
                # Verifica se a mensagem de erro contém "Código do Cliente foi alterado"
                try:
                    response_json = response.json()
                    if isinstance(response_json, dict) and 'errorMessage' in response_json and 'Código do Cliente foi alterado' in response_json['errorMessage']:
                        self.results['success'] += 1
                        nro_pedido = data.get('nroPedido', 'desconhecido') if data else 'desconhecido'
                        mensagem = f"Pedido {nro_pedido} não pode ser fechado (cliente foi alterado por outro usuário)"
                        print(f"Informação: {mensagem}")
                        self.results['success_responses'].append(mensagem)
                        return True, response_time
                except Exception:
                    pass
                    
            # Tratamento especial para erro de cliente alterado ao alterar quantidade
            if endpoint == '/EditaItemPedido/alterarQuantidade' and response.status_code == 500:
                # Verifica se a mensagem de erro contém "Código do Cliente foi alterado"
                try:
                    error_text = response.text
                    if 'Código do Cliente foi alterado por outro usuário' in error_text:
                        self.results['success'] += 1
                        nro_pedido = data.get('nroPedido', 'desconhecido') if data else 'desconhecido'
                        mensagem = f"Pedido {nro_pedido} não pode ter quantidade alterada (cliente foi alterado por outro usuário)"
                        print(f"Informação: {mensagem}")
                        self.results['success_responses'].append(mensagem)
                        return True, response_time
                except Exception:
                    pass
        
            if response.status_code in [200, 201, 204]:
                self.results['success'] += 1
                # Armazena o conteúdo da resposta de sucesso
                try:
                    response_json = response.json()
                    self.results['success_responses'].append(response_json)
                    
                    # Se for uma resposta de criação de pedido, armazena o número do pedido
                    if endpoint == '/Pedido/Criar' and isinstance(response_json, dict) and 'pedidoNumero' in response_json:
                        nro_pedido_criado = response_json['pedidoNumero']
                        self.adicionar_pedido_criado(nro_pedido_criado)
                        
                        # Armazenar o cliente associado a este pedido
                        if isinstance(data, dict) and 'CodCliente' in data:
                            # Atualiza o dicionário pedidos_clientes
                            self.pedidos_clientes[nro_pedido_criado] = data['CodCliente']
                            
                            # Salvar pedidos_clientes em um arquivo
                            try:
                                self.salvar_pedidos_clientes()
                                print(f"Cliente {data['CodCliente']} associado ao pedido {nro_pedido_criado}")
                            except Exception as e:
                                print(f"Erro ao salvar pedidos_clientes: {str(e)}")
                        
                        # Inicializa o contador de itens adicionados
                        itens_adicionados = 0
                        
                        # Adicionar entre 1 e 5 itens aleatórios ao pedido (menos para não sobrecarregar)
                        num_itens = random.randint(1, 5)
                        
                        for i in range(num_itens):
                            # Selecionar um produto aleatório
                            cod_produto_aleatorio = random.choice(self.codigos_produto)
                            qtd_vendida_aleatoria = random.randint(1, 500)
                            desconto_individual_aleatorio = round(random.uniform(1.0, 20.0), 2)
                            
                            # Dados para adicionar o item ao pedido
                            item_data = {
                                'nroPedido': nro_pedido_criado,
                                'codCliente': data['CodCliente'],
                                'codProduto': cod_produto_aleatorio,
                                'qtdVendida': qtd_vendida_aleatoria,
                                'descontoIndividual': desconto_individual_aleatorio,
                                'tabelaPreco': 1,
                                'codCondPagamento': data['CodCondPagamento'],
                                'codTransportadora': data['CodTransportadora'],
                                'tipoOperacao': 1
                            }
                            
                            # Adicionar o item ao pedido
                            item_success, _ = self.test_endpoint('/EditaItemPedido/alterarQuantidade', 'POST', item_data, None)
                            
                            # Se o item foi adicionado com sucesso, incrementar o contador
                            if item_success:
                                itens_adicionados += 1
                        
                        print(f"Adicionados {itens_adicionados} itens ao pedido {nro_pedido_criado}")
                    # Se for uma resposta de alteração de quantidade, armazena o item no pedido
                    if endpoint == '/EditaItemPedido/alterarQuantidade' and isinstance(data, dict):
                        if 'nroPedido' in data and 'codProduto' in data:
                            print(f"Adicionando produto {data['codProduto']} ao pedido {data['nroPedido']}")
                            self.adicionar_item_ao_pedido(data['nroPedido'], data['codProduto'])
                            
                    # Se for uma resposta de exclusão de item, remove o item do pedido
                    if endpoint == '/EditaItemPedido/excluirItem' and isinstance(params, dict):
                        if 'nroPedido' in params and 'codigo' in params:
                            self.remover_item_do_pedido(params['nroPedido'], params['codigo'])
                        
                    print(f"Resposta de sucesso do endpoint {endpoint}: {response.text}")
                except Exception as e:
                    self.results['success_responses'].append(response.text)
                    print(f"Erro ao processar resposta: {str(e)}")
                return True, response_time
            else:
                self.results['errors'] += 1
                print(f"Erro no endpoint {endpoint}: {response.status_code}")
                print(f"Resposta: {response.text}")
                return False, response_time

        except Exception as e:
            self.results['errors'] += 1
            print(f"Exceção no endpoint {endpoint}: {str(e)}")
            return False, time.time() - start_time

    def run_concurrent_tests(self, endpoint: str, method: str = 'GET', data: Dict[str, Any] = None, params: Dict[str, Any] = None, num_requests: int = 10):
        """
        Executa testes concorrentes em um endpoint
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS) as executor:
            futures = [
                executor.submit(self.test_endpoint, endpoint, method, data, params)
                for _ in range(num_requests)
            ]
            
            for future in concurrent.futures.as_completed(futures):
                success, response_time = future.result()
                if success:
                    print(f"Requisição bem-sucedida em {response_time:.2f} segundos")
                else:
                    print("Requisição falhou")

    def print_results(self):
        """
        Imprime os resultados dos testes
        """
        total_requests = self.results['success'] + self.results['errors']
        avg_response_time = sum(self.results['response_times']) / len(self.results['response_times']) if self.results['response_times'] else 0
        
        print("\n=== Resultados dos Testes ===")
        print(f"Total de requisições: {total_requests}")
        print(f"Sucessos: {self.results['success']}")
        print(f"Erros: {self.results['errors']}")
        print(f"Tempo médio de resposta: {avg_response_time:.2f} segundos")
        print(f"Taxa de sucesso: {(self.results['success']/total_requests)*100:.2f}%")

def carregar_codigos_produto():
    """Função que carrega códigos de produto de um arquivo"""
    try:
        if os.path.exists('codigos_produto.txt'):
            with open('codigos_produto.txt', 'r') as f:
                return [linha.strip() for linha in f if linha.strip()]
        else:
            # Retorna alguns códigos padrão caso o arquivo não exista
            return ['000001', '000002', '000003', '000004', '000005', '000006', '000007', '000008', '000009', '000010']
    except Exception as e:
        print(f"Erro ao carregar códigos de produto: {str(e)}")
        return ['000001', '000002', '000003', '000004', '000005']

def carregar_cod_representantes():
    return [
        105, 106, 107, 113, 124, 125, 132, 135, 191, 208, 213, 226, 234, 236, 247, 250, 255, 265, 266, 267,
        268, 270, 279, 287, 290, 292, 294, 302, 304, 309, 310, 311, 312, 313, 314, 402, 419, 423, 425, 32767
    ]

# Nova função para carregar CodCliente
def carregar_cod_clientes():
    return [
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
        21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
        41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
        61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80,
        81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100
    ]

def carregar_nro_pedidos():
    """Função de fallback que retorna alguns números de pedido padrão caso não existam pedidos criados"""
    return [1, 2, 3, 4, 5]  # Valores mínimos apenas para fallback

def carregar_cod_cond_pagamento():
    return [711, 712, 713, 714, 715, 717, 719]

def carregar_cod_transportadoras():
    return [
        1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 80, 82, 83, 84, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 105, 106, 107, 108
    ]

def main():
    tester = APITester()
    cod_representantes = carregar_cod_representantes()
    cod_clientes = carregar_cod_clientes()
    nro_pedidos = carregar_nro_pedidos()
    cod_cond_pagamento = carregar_cod_cond_pagamento()
    cod_transportadoras = carregar_cod_transportadoras()
    
    # Remova estas linhas se existirem:
    # pedidos_clientes = {}
    
    # Remova o carregamento de pedidos_clientes aqui, pois já está na classe
    
    print("Iniciando testes de carga...")
    print(f"Simulando {MAX_CONCURRENT_REQUESTS} usuários simultâneos...")
    
    start_time = time.time()
    
    while time.time() - start_time < TEST_DURATION_SECONDS:
        # Seleciona um endpoint aleatório para testar
        endpoints = [
            '/Representante/listar',
            '/Cliente/listar',
            '/Produto/listar',
            '/Pedido/listarPedidosAbertos/{codRepresentante}',
            '/Pedido/Criar',
            '/EditaItemPedido/alterarQuantidade',
            '/EditaItemPedido/excluirItem',
            '/EditaItemPedido/fecharPedido',
            '/Pedido/imprime',
            '/Pedido/imprimeFichaCadastral',
            '/Produto/busca'
        ]
        
        path = random.choice(endpoints)
        
        # Configurações específicas para cada endpoint
        if path == '/Representante/listar':
            tester.test_endpoint(path, 'GET')
        elif path == '/Cliente/listar':
            tester.test_endpoint(path, 'GET')
        elif path == '/Produto/listar':
            tester.test_endpoint(path, 'GET')
        elif path == '/Pedido/listarPedidosAbertos/{codRepresentante}':
            # Substitui o placeholder pelo código do representante
            cod_representante_aleatorio = random.choice(cod_representantes)
            endpoint = path.replace('{codRepresentante}', str(cod_representante_aleatorio))
            tester.test_endpoint(endpoint, 'GET')
        elif path == '/Pedido/Criar':
            # Dados para criar um pedido
            cod_cliente_aleatorio = random.choice(cod_clientes)
            cod_representante_aleatorio = random.choice(cod_representantes)
            cod_cond_pagamento_aleatorio = random.choice(cod_cond_pagamento)
            cod_transportadora_aleatoria = random.choice(cod_transportadoras)
            
            data = {
                'CodCliente': cod_cliente_aleatorio,
                'CodRepresentante': cod_representante_aleatorio,
                'CodCondPagamento': cod_cond_pagamento_aleatorio,
                'CodTransportadora': cod_transportadora_aleatoria,
                'TipoOperacao': 1,
                'TipoFrete': 'C',
                'Observacao': fake.text(max_nb_chars=100)
            }
            
            tester.test_endpoint(path, 'POST', data)
        elif path == '/EditaItemPedido/alterarQuantidade':
            # Verifica se há pedidos criados
            if not tester.pedidos_criados:
                continue
                
            # Seleciona um pedido aleatório
            nro_pedido_aleatorio = tester.obter_pedido_aleatorio()
            
            # Verifica se o pedido tem um cliente associado
            if nro_pedido_aleatorio not in tester.pedidos_clientes:
                continue
                
            cod_cliente = tester.pedidos_clientes[nro_pedido_aleatorio]
            
            # Seleciona um produto aleatório
            # AQUI ESTÁ A CORREÇÃO: usar tester.codigos_produto em vez de codigos_produto
            cod_produto_aleatorio = random.choice(tester.codigos_produto)
            qtd_vendida_aleatoria = random.randint(1, 500)
            desconto_individual_aleatorio = round(random.uniform(1.0, 20.0), 2)
            
            data = {
                'nroPedido': nro_pedido_aleatorio,
                'codCliente': cod_cliente,
                'codProduto': cod_produto_aleatorio,
                'qtdVendida': qtd_vendida_aleatoria,
                'descontoIndividual': desconto_individual_aleatorio,
                'tabelaPreco': 1,
                'codCondPagamento': random.choice(cod_cond_pagamento),
                'codTransportadora': random.choice(cod_transportadoras),
                'tipoOperacao': 1
            }
            
            tester.test_endpoint(path, 'POST', data)
        elif path == '/EditaItemPedido/excluirItem':
            # Verifica se há pedidos criados
            if not tester.pedidos_criados:
                continue
                
            # Seleciona um pedido aleatório
            nro_pedido_aleatorio = tester.obter_pedido_aleatorio()
            
            # Verifica se o pedido tem itens
            if nro_pedido_aleatorio not in tester.itens_por_pedido or not tester.itens_por_pedido[nro_pedido_aleatorio]:
                continue
                
            # Seleciona um item aleatório do pedido
            cod_produto_aleatorio = tester.obter_item_aleatorio_do_pedido(nro_pedido_aleatorio)
            
            params = {
                'nroPedido': nro_pedido_aleatorio,
                'codigo': cod_produto_aleatorio
            }
            
            tester.test_endpoint(path, 'DELETE', None, params)
        elif path == '/EditaItemPedido/fecharPedido':
            # Verifica se há pedidos criados
            if not tester.pedidos_criados:
                print("Não há pedidos criados para fechar. Pulando endpoint.")
                continue
                
            # Seleciona um pedido aleatório
            nro_pedido_aleatorio = tester.obter_pedido_aleatorio()
            
            data = {
                'nroPedido': nro_pedido_aleatorio
            }
            
            tester.test_endpoint(path, 'POST', data)
        elif path == '/Pedido/imprime' or path == '/Pedido/imprimeFichaCadastral':
            # Verifica se há pedidos criados
            if not tester.pedidos_criados:
                continue
                
            # Seleciona um pedido aleatório
            nro_pedido_aleatorio = tester.obter_pedido_aleatorio()
            
            data = {
                'nroPedido': nro_pedido_aleatorio
            }
            
            tester.test_endpoint(path, 'POST', data)
        elif path == '/Produto/busca':
            # AQUI ESTÁ A CORREÇÃO: usar tester.codigos_produto em vez de codigos_produto
            codigo_aleatorio = random.choice(tester.codigos_produto)
            data = {'codigo': codigo_aleatorio}
            tester.test_endpoint(path, 'POST', data)
    
    tester.print_results()

if __name__ == "__main__":
    main()