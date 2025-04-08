# Sistema de Controle de Pedidos e Almoxarifado

Sistema para controle de pedidos com comunicação assíncrona entre sistemas de pedidos e almoxarifado utilizando RabbitMQ e FastAPI.

## Requisitos

- Python 3.7+
- FastAPI
- Uvicorn
- Pika (cliente RabbitMQ)
- RabbitMQ Server

## Instalação

```bash
# Instalar dependências
pip install fastapi uvicorn pika

# Instalar RabbitMQ (Ubuntu/Debian)
sudo apt-get install rabbitmq-server

# Iniciar RabbitMQ
sudo service rabbitmq-server start
```

## Executando o Sistema

1. **Inicie o serviço de Pedidos**:
   ```bash
   cd /root/ListaASA
   python publisher.py
   ```

2. **Inicie o serviço de Almoxarifado**:
   ```bash
   cd /root/ListaASA
   python consumer.py
   ```

## Usando a API

### API de Pedidos (Publicador)

- **URL**: http://localhost:5000/docs
- **Criar um novo pedido**:
  ```bash
  curl -X 'POST' \
    'http://localhost:5000/pedido' \
    -H 'Content-Type: application/json' \
    -d '{
      "produto": "Notebook",
      "quantidade": 2
    }'
  ```

### API de Almoxarifado (Consumidor)

- **URL**: http://localhost:5001/docs
- **Processar pedido**:
  ```bash
  curl -X 'GET' 'http://localhost:5001/processar-pedido'
  ```

## Acessando o RabbitMQ

1. **Ativar o plugin de gerenciamento** (se ainda não estiver ativado):
   ```bash
   sudo rabbitmq-plugins enable rabbitmq_management
   ```

2. **Acessar o painel de administração**:
   - URL: http://localhost:15672
   - Usuário padrão: `guest`
   - Senha padrão: `guest`

3. **Visualizar filas**:
   - No menu lateral, clique em "Queues"
   - Procure pelas filas `pedidos` e `pedidos_processados`

4. **Monitorar mensagens**:
   - Clique na fila desejada para ver detalhes
   - Use as guias "Get messages" para visualizar mensagens na fila

## Estrutura das Mensagens

### Pedido (enviado para a fila `pedidos`)
```json
{
    "id": "xxxxxx",
    "produto": "Nome do Produto",
    "quantidade": 1,
    "status": "enviado_almoxarifado"
}
```

### Pedido Processado (enviado para a fila `pedidos_processados`)
```json
{
    "id": "xxxxxx",
    "produto": "Nome do Produto",
    "quantidade": 1,
    "status": "processado_almoxarifado"
}
```

## Modo de Consumo Contínuo

Para habilitar o consumo contínuo de mensagens, edite o arquivo `consumer.py` e descomente as linhas:

```python
# consumer_thread = threading.Thread(target=start_consumer)
# consumer_thread.daemon = True
# consumer_thread.start()
```

Este modo permite processar pedidos automaticamente, sem necessidade de chamar o endpoint manualmente.
