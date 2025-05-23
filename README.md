# Robô de Testes de API

Este é um robô de testes para simular acessos simultâneos a uma API local, desenvolvido para testar o comportamento da API sob carga.

## Requisitos

- Python 3.8 ou superior
- Bibliotecas listadas em `requirements.txt`

## Instalação

1. Clone este repositório
2. Crie um ambiente virtual:
   ```
   python -m venv venv
   ```
3. Ative o ambiente virtual:
   - Windows: `.\venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

## Configuração

Edite o arquivo `.env` com as configurações da sua API:

```
API_BASE_URL=http://localhost
API_PORT=80
MAX_CONCURRENT_REQUESTS=10
TEST_DURATION_SECONDS=60
```

## Uso

Execute o robô de testes:

```
python api_tester.py
```

O robô irá:
1. Fazer requisições simultâneas aos endpoints configurados
2. Gerar dados aleatórios para testes
3. Mostrar estatísticas de sucesso/erro
4. Exibir tempos médios de resposta

## Personalização

Para testar diferentes endpoints, edite a lista `endpoints` no arquivo `api_tester.py`. Cada endpoint pode ter:
- path: caminho do endpoint
- method: método HTTP (GET, POST, PUT)
- data: dados para enviar (opcional)

## Resultados

O robô mostrará:
- Total de requisições
- Número de sucessos e erros
- Tempo médio de resposta
- Taxa de sucesso #   r o b o T e s t e A p i S r p p  
 