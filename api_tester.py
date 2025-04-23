import os
import time
import concurrent.futures
import requests
from dotenv import load_dotenv
from faker import Faker
from typing import Dict, Any
import random

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
            'response_times': []
        }

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
            else:
                raise ValueError(f"Método {method} não suportado")

            response_time = time.time() - start_time
            self.results['response_times'].append(response_time)

            if response.status_code in [200, 201, 204]:
                self.results['success'] += 1
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
    with open('codigos_produto.txt', 'r', encoding='utf-8') as f:
        return [linha.strip() for linha in f if linha.strip()]

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
    return [
        15, 21, 24, 25, 29, 30, 31, 33, 35, 37, 39, 42, 44, 47, 50, 51, 53, 54, 55, 59,
        66, 67, 68, 69, 75, 79, 81, 83, 86, 87, 88, 90, 91, 93, 94, 97, 101, 102, 103, 106,
        107, 108, 109, 110, 113, 116, 119, 123, 124, 126
    ]

def carregar_cod_cond_pagamento():
    return [711, 712, 713, 714, 715, 717, 719]

def carregar_cod_transportadoras():
    return [
        1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 80, 82, 83, 84, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 105, 106, 107, 108
    ]

def main():
    tester = APITester()
    codigos_produto = carregar_codigos_produto()
    cod_representantes = carregar_cod_representantes()
    cod_clientes = carregar_cod_clientes()
    nro_pedidos = carregar_nro_pedidos()
    cod_cond_pagamento = carregar_cod_cond_pagamento()
    cod_transportadoras = carregar_cod_transportadoras()
    
    # Endpoints para testar
    endpoints = [
        # Criar Pedido
        {
            'path': '/Pedido/Criar',
            'method': 'POST',
            # O CodRepresentante e CodCliente serão definidos dinamicamente abaixo
        },
        # Listar Pedidos Abertos
        {
            'path': '/Pedido/listarPedidosAbertos/{codRepresentante}',
            'method': 'GET',
            'params': {'codRepresentante': 190}
        },
        
        # Total do Pedido
        {
            'path': '/Pedido/totalPedido/{nroPedido}',
            'method': 'GET',
            'params': {'nroPedido': 42}
        },
        
        # Imprimir Pedido
        {
            'path': '/Pedido/imprime',
            'method': 'POST',
            # O nropedido será definido dinamicamente abaixo
        },
        {
            'path': '/Pedido/imprimeFichaCadastral',
            'method': 'POST',
            # O nropedido será definido dinamicamente abaixo
        },
        
        # Buscar Produto por Código
        {
            'path': '/Produto/busca',
            'method': 'POST',
            # O código será definido dinamicamente abaixo
        },
    ]
    
    print("Iniciando testes de carga...")
    start_time = time.time()
    
    while time.time() - start_time < TEST_DURATION_SECONDS:
        for endpoint in endpoints:
            path = endpoint['path']
            data = endpoint.get('data')
            params = endpoint.get('params')
            
            # Randomiza CodRepresentante, CodCliente, CodCondPagamento e CodTransportadora para o endpoint de criar pedido
            if path == '/Pedido/Criar':
                cod_representante_aleatorio = random.choice(cod_representantes)
                cod_cliente_aleatorio = random.choice(cod_clientes)
                cod_cond_pagamento_aleatorio = random.choice(cod_cond_pagamento)
                cod_transportadora_aleatoria = random.choice(cod_transportadoras)
                data = {
                    'CodRepresentante': cod_representante_aleatorio,
                    'CodCliente': cod_cliente_aleatorio,
                    'CodCondPagamento': cod_cond_pagamento_aleatorio,
                    'CodTransportadora': cod_transportadora_aleatoria,
                    'DtPrevEntrega': '2025-02-09T13:56:40.203'
                }

            # Randomiza codRepresentante para listar pedidos abertos
            if path == '/Pedido/listarPedidosAbertos/{codRepresentante}':
                cod_representante_aleatorio = random.choice(cod_representantes)
                params = {'codRepresentante': cod_representante_aleatorio}
                path = path.replace('{codRepresentante}', str(cod_representante_aleatorio))

            # Randomiza nroPedido para total do pedido
            if path == '/Pedido/totalPedido/{nroPedido}':
                nro_pedido_aleatorio = random.choice(nro_pedidos)
                params = {'nroPedido': nro_pedido_aleatorio}
                path = path.replace('{nroPedido}', str(nro_pedido_aleatorio))

            # Se for o endpoint de busca de produto, seleciona um código aleatório e um nroPedido aleatório
            if path == '/Produto/busca':
                codigo_aleatorio = random.choice(codigos_produto)
                nro_pedido_aleatorio = random.choice(nro_pedidos)
                data = {
                    'codigo': codigo_aleatorio,
                    'tabelaPreco': 1,
                    'nroPedido': nro_pedido_aleatorio
                }

            # Randomiza nropedido para os endpoints de impressão
            if path == '/Pedido/imprime' or path == '/Pedido/imprimeFichaCadastral':
                nropedido_aleatorio = random.choice(nro_pedidos)
                params = {'nropedido': nropedido_aleatorio}

            tester.run_concurrent_tests(
                path,
                endpoint['method'],
                data,
                params,
                num_requests=20
            )
            time.sleep(1)  # Pequena pausa entre os testes
    
    tester.print_results()

if __name__ == "__main__":
    main()