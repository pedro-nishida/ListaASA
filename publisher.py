import pika
import uuid
import json
import sys

def get_rabbitmq_connection():
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters(
        host='localhost',
        port=5672,
        virtual_host='/',
        credentials=credentials
    )
    return pika.BlockingConnection(parameters=parameters)

def publicar_pedido(produto, quantidade):
    # Gerar ID único para o pedido
    id_pedido = uuid.uuid4().hex
    
    # Criar o objeto de pedido
    pedido = {
        "id": id_pedido,
        "produto": produto,
        "quantidade": quantidade,
        "status": "enviado_almoxarifado"
    }
    
    try:
        # Conectar ao RabbitMQ
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Declarar a fila e vincular ao exchange
        channel.queue_declare(queue='fila_pedidos')
        channel.queue_bind(
            exchange='amq.direct',
            queue='fila_pedidos',
            routing_key='pedido'
        )
        
        # Publicar a mensagem
        channel.basic_publish(
            exchange='amq.direct',
            routing_key='pedido',
            body=json.dumps(pedido).encode('utf-8')
        )
        
        print(f"[✓] Pedido enviado com sucesso!")
        print(f"    ID: {id_pedido}")
        print(f"    Produto: {produto}")
        print(f"    Quantidade: {quantidade}")
        
        # Fechar a conexão
        connection.close()
        return True
        
    except Exception as e:
        print(f"[✗] Erro ao enviar pedido: {str(e)}")
        return False

if __name__ == "__main__":
    # Verificar se argumentos foram fornecidos
    if len(sys.argv) < 3:
        print("Uso: python publisher.py <produto> <quantidade>")
        print("Exemplo: python publisher.py 'Notebook' 2")
        sys.exit(1)
    
    # Obter argumentos da linha de comando
    produto = sys.argv[1]
    quantidade = int(sys.argv[2])
    
    # Publicar o pedido
    publicar_pedido(produto, quantidade)
