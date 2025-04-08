import pika
import json
from ..core.config import settings
from ..models.pedido import Pedido

def conectar_rabbitmq():
    """Estabelece conexão com o RabbitMQ usando credenciais"""
    credentials = pika.PlainCredentials(
        settings.RABBITMQ_USER, 
        settings.RABBITMQ_PASSWORD
    )
    parameters = pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        virtual_host='/',
        credentials=credentials
    )
    
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    # Declara a fila e faz o binding com o exchange
    channel.queue_declare(queue=settings.QUEUE_PEDIDOS)
    channel.queue_bind(
        exchange=settings.RABBITMQ_EXCHANGE,
        queue=settings.QUEUE_PEDIDOS,
        routing_key=settings.ROUTING_KEY_PEDIDOS
    )
    
    return connection, channel

def publicar_pedido(pedido: Pedido):
    """Publica um pedido na fila do RabbitMQ"""
    # Converte o modelo para dicionário
    pedido_dict = {
        "id": pedido.id,
        "produto": pedido.produto,
        "quantidade": pedido.quantidade,
        "status": pedido.status
    }
    
    # Converte para JSON
    mensagem = json.dumps(pedido_dict)
    
    # Conecta ao RabbitMQ
    connection, channel = conectar_rabbitmq()
    
    # Publica a mensagem
    channel.basic_publish(
        exchange=settings.RABBITMQ_EXCHANGE,
        routing_key=settings.ROUTING_KEY_PEDIDOS,
        body=mensagem,
        properties=pika.BasicProperties(
            delivery_mode=2,  # persistente
            content_type='application/json'
        )
    )
    
    # Fecha a conexão
    connection.close()
