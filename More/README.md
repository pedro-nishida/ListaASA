# Sistema de Controle de Pedidos e Almoxarifado - Microserviços

Este projeto implementa um sistema de controle de pedidos e almoxarifado utilizando uma arquitetura de microserviços com Python, FastAPI e RabbitMQ.

## Visão Geral

O sistema é dividido em dois microserviços principais:

1. **Serviço de Pedidos**: Recebe pedidos via API REST e os envia para uma fila no RabbitMQ.
2. **Serviço de Almoxarifado**: Consome pedidos da fila quando o usuário do almoxarifado está disponível e retorna o status atualizado.

## Requisitos

- Python 3.6+
- RabbitMQ
- Docker e Docker Compose
- Bibliotecas Python (veja `requirements.txt`)

## Instalação

1. Clone este repositório:
   ```
   git clone <repositório>
   cd ListaASA
   ```

2. Configure um ambiente virtual:
   ```bash
   # Criar o ambiente virtual
   python3 -m venv venv
   
   # Ativar o ambiente virtual
   # No Windows:
   venv\Scripts\activate
   
   # No Linux/MacOS:
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

4. Certifique-se de que o RabbitMQ está em execução:
   ```
   # Instalar RabbitMQ (se necessário)
   # No Ubuntu:
   sudo apt-get install rabbitmq-server
   
   # No MacOS:
   brew install rabbitmq
   
   # Iniciar o serviço
   sudo service rabbitmq-server start
   ```

## Uso

### 1. Inicie os serviços

Em terminais separados, inicie os dois serviços (com ambiente virtual ativado):

Terminal 1 (Publisher - Sistema de Pedidos):
```
python publisher.py
```

Terminal 2 (Consumer - Sistema do Almoxarifado):
```
python consumer.py
```

### 2. Envie um pedido

Use uma ferramenta como cURL, Postman ou navegador para enviar um pedido:

```bash
curl -X POST http://localhost:5000/enviar-pedido \
     -H "Content-Type: application/json" \
     -d '{
           "id": "12345",
           "produto": "laptop",
           "quantidade": 2
         }'
```

Para enviar múltiplos pedidos de uma vez:

```bash
curl -X POST http://localhost:5000/enviar-pedido-lote \
     -H "Content-Type: application/json" \
     -d '[
           {
             "id": "12345",
             "produto": "laptop",
             "quantidade": 2
           },
           {
             "id": "67890",
             "produto": "mouse",
             "quantidade": 5
           }
         ]'
```

### 3. Processe pedidos no almoxarifado

#### Processamento individual (uma mensagem por vez):
```bash
curl http://localhost:5001/processar-pedidos
```

#### Processamento contínuo (consumo automático):
Para iniciar o processamento contínuo:
```bash
curl http://localhost:5001/iniciar-processamento
```

Para parar o processamento contínuo:
```bash
curl http://localhost:5001/parar-processamento
```

## Estrutura do Projeto

- `publisher.py`: Implementa o endpoint para receber pedidos e enviá-los à fila
- `consumer.py`: Implementa o endpoint para processar pedidos quando solicitado
- `requirements.txt`: Lista de dependências do projeto

## Formato das Mensagens

### Pedido Enviado ao Almoxarifado
```json
{
    "id": "12345",
    "produto": "laptop",
    "quantidade": 2,
    "status": "enviado_almoxarifado"
}
```

### Pedido Processado pelo Almoxarifado
```json
{
    "id": "12345",
    "produto": "laptop",
    "quantidade": 2,
    "status": "processado_almoxarifado"
}
```

## Endpoints da API

### Publisher (Sistema de Pedidos)
- `POST /enviar-pedido`: Recebe um pedido e o envia para o almoxarifado
- `POST /enviar-pedido-lote`: Recebe múltiplos pedidos e os envia para o almoxarifado

### Consumer (Sistema do Almoxarifado)
- `GET /processar-pedidos`: Busca um pedido da fila e o processa (processamento individual)
- `GET /iniciar-processamento`: Inicia o processamento contínuo de pedidos
- `GET /parar-processamento`: Para o processamento contínuo de pedidos

## Fluxo de Trabalho

1. O sistema de pedidos recebe um pedido via API
2. O pedido é enviado para a fila `pedidos_para_almoxarifado` com status "enviado_almoxarifado" usando o exchange "amq.direct"
3. O sistema do almoxarifado pode processar de duas formas:
   - Processamento individual: através do endpoint `/processar-pedidos`
   - Processamento contínuo: iniciando com `/iniciar-processamento` e parando com `/parar-processamento`
4. Cada pedido processado é enviado para a fila `pedidos_processados` com status "processado_almoxarifado"

## RabbitMQ - Configuração de Exchange e Routing Keys

O sistema utiliza o exchange padrão "amq.direct" com as seguintes routing keys:
- `pedidos`: Utilizada para enviar pedidos ao almoxarifado
- `processados`: Utilizada para pedidos já processados pelo almoxarifado

## Arquitetura de Microserviços

O projeto foi estruturado seguindo as melhores práticas para microserviços:

### Estrutura de Diretórios
```
/root/ListaASA/
├── pedido_service/             # Microserviço de Pedidos
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # Ponto de entrada da aplicação
│   │   ├── models/             # Modelos de dados (SQLAlchemy)
│   │   ├── schemas/            # Esquemas de validação (Pydantic)
│   │   ├── routers/            # Endpoints da API
│   │   ├── services/           # Lógica de negócios
│   │   ├── db/                 # Configuração do banco de dados
│   │   └── core/               # Configurações e segurança
│   ├── Dockerfile
│   └── requirements.txt
├── almoxarifado_service/       # Microserviço de Almoxarifado
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── db/
│   │   └── core/
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml          # Composição dos serviços
└── README.md
```

### Tecnologias Utilizadas
- **FastAPI**: Framework web de alta performance
- **SQLAlchemy**: ORM para comunicação com o banco de dados
- **Pydantic**: Validação de dados e serialização
- **RabbitMQ**: Comunicação assíncrona entre serviços
- **PostgreSQL**: Banco de dados relacional
- **Docker**: Containerização e isolamento
- **Docker Compose**: Orquestração de contêineres

## Executando com Docker

Para rodar toda a aplicação com Docker Compose:

```bash
# Construir e iniciar todos os serviços
docker-compose up --build

# Rodar em modo detached
docker-compose up -d

# Parar todos os serviços
docker-compose down
```

## Licença

[Incluir informações de licença aqui]
