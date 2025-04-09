import json
import pika
import sys
import os
import time

# Configuração do RabbitMQ com autenticação explícita
def get_rabbitmq_connection():
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters(
        host='localhost',
        port=5672,
        virtual_host='/',
        credentials=credentials
    )
    return pika.BlockingConnection(parameters=parameters)

def processar_pedido():
    """
    Processa um único pedido da fila
    """
    try:
        # Conectar ao RabbitMQ
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Declarar filas e bind com exchange
        channel.queue_declare(queue='fila_pedidos')
        channel.queue_bind(
            exchange='amq.direct',
            queue='fila_pedidos',
            routing_key='pedido'
        )
        
        channel.queue_declare(queue='fila_processados')
        channel.queue_bind(
            exchange='amq.direct',
            queue='fila_processados',
            routing_key='pedido_processado'
        )
        
        # Verificar se há mensagens na fila
        method_frame, header_frame, body = channel.basic_get(queue='fila_pedidos', auto_ack=True)
        
        if method_frame:
            # Processar o pedido
            pedido = json.loads(body)
            print(f"[✓] Pedido recebido: {pedido['id']}")
            print(f"    Produto: {pedido['produto']}")
            print(f"    Quantidade: {pedido['quantidade']}")
            
            # Simular processamento
            print(f"[*] Processando pedido...")
            time.sleep(1)  # Simula o tempo de processamento
            
            # Criar pedido processado
            pedido_processado = {
                "id": pedido['id'],
                "produto": pedido['produto'],
                "quantidade": pedido['quantidade'],
                "status": "processado_almoxarifado"
            }
            
            # Publicar na fila de pedidos processados usando o exchange
            channel.basic_publish(
                exchange='amq.direct',
                routing_key='pedido_processado',
                body=json.dumps(pedido_processado).encode('utf-8')
            )
            
            connection.close()
            print(f"[✓] Pedido processado com sucesso!")
            return True
        else:
            connection.close()
            print("[!] Não há pedidos para processar")
            return False
    
    except Exception as e:
        print(f"[✗] Falha ao processar pedido: {str(e)}")
        return False

def start_consumer():
    """
    Inicia o consumo contínuo da fila
    """
    def callback(ch, method, properties, body):
        pedido = json.loads(body)
        print(f"[✓] Pedido recebido: {pedido['id']}")
        print(f"    Produto: {pedido['produto']}")
        print(f"    Quantidade: {pedido['quantidade']}")
        
        # Simular processamento
        print(f"[*] Processando pedido...")
        time.sleep(1)  # Simula o tempo de processamento
        
        # Criar pedido processado
        pedido_processado = {
            "id": pedido['id'],
            "produto": pedido['produto'],
            "quantidade": pedido['quantidade'],
            "status": "processado_almoxarifado"
        }
        
        # Publicar resultado
        ch.basic_publish(
            exchange='amq.direct',
            routing_key='pedido_processado',
            body=json.dumps(pedido_processado).encode('utf-8')
        )
        print(f"[✓] Pedido processado e enviado para a fila de processados")
    
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        channel.queue_declare(queue='fila_pedidos')
        channel.queue_bind(
            exchange='amq.direct',
            queue='fila_pedidos',
            routing_key='pedido'
        )
        
        channel.queue_declare(queue='fila_processados')
        channel.queue_bind(
            exchange='amq.direct',
            queue='fila_processados',
            routing_key='pedido_processado'
        )
        
        channel.basic_consume(
            queue='fila_pedidos',
            on_message_callback=callback,
            auto_ack=True
        )
        
        print('[*] Aguardando pedidos. CTRL+C para sair')
        channel.start_consuming()
    
    except KeyboardInterrupt:
        print('Consumidor interrompido')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

if __name__ == '__main__':
    # Verificar modo de execução
    if len(sys.argv) > 1 and sys.argv[1] == "--continuo":
        print("Iniciando modo de consumo contínuo...")
        start_consumer()
    else:
        print("Processando um único pedido...")
        processar_pedido()
        print("Para iniciar o modo de consumo contínuo, use: python consumer.py --continuo")
