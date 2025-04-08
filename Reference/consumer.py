import pika
import json
import sys
import os
import threading
from flask import Flask, jsonify

app = Flask(__name__)

# Configurações do RabbitMQ
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
QUEUE_PEDIDOS = 'pedidos_para_almoxarifado'
QUEUE_PROCESSADOS = 'pedidos_processados'
EXCHANGE = 'amq.direct'
ROUTING_KEY_PEDIDOS = 'pedidos'
ROUTING_KEY_PROCESSADOS = 'processados'

# Flag para controlar o consumo de mensagens
processar_mensagens = False
consumer_thread = None

def callback(ch, method, properties, body):
    """Callback executado quando uma mensagem é recebida"""
    try:
        # Processa o pedido
        dados = json.loads(body)
        dados['status'] = 'processado_almoxarifado'
        pedido_processado = json.dumps(dados)
        
        # Publica o pedido processado
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            virtual_host='/',
            credentials=credentials
        )
        
        # Abre uma nova conexão para publicar
        pub_connection = pika.BlockingConnection(parameters)
        pub_channel = pub_connection.channel()
        
        # Declara a fila de processados e faz o binding
        pub_channel.queue_declare(queue=QUEUE_PROCESSADOS)
        pub_channel.queue_bind(
            exchange=EXCHANGE,
            queue=QUEUE_PROCESSADOS,
            routing_key=ROUTING_KEY_PROCESSADOS
        )
        
        # Publica a mensagem processada
        pub_channel.basic_publish(
            exchange=EXCHANGE,
            routing_key=ROUTING_KEY_PROCESSADOS,
            body=pedido_processado
        )
        
        print(f" [x] Processado: {dados['id']} - {dados['produto']}")
        pub_connection.close()
        
        # Confirma o recebimento da mensagem original
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        print(f"Erro ao processar mensagem: {str(e)}")
        # Rejeita a mensagem em caso de erro
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def iniciar_consumo():
    """Função que inicia o consumo de mensagens"""
    global processar_mensagens
    
    try:
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            virtual_host='/',
            credentials=credentials
        )
        
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        # Declara a fila e faz o binding
        channel.queue_declare(queue=QUEUE_PEDIDOS)
        channel.queue_bind(
            exchange=EXCHANGE,
            queue=QUEUE_PEDIDOS,
            routing_key=ROUTING_KEY_PEDIDOS
        )
        
        # Configura o consumo de mensagens
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue=QUEUE_PEDIDOS,
            on_message_callback=callback,
            auto_ack=False
        )
        
        print(' [*] Aguardando pedidos. CTRL+C para sair')
        
        # Loop de consumo que pode ser interrompido
        while processar_mensagens:
            connection.process_data_events(time_limit=1)  # Processa eventos por 1 segundo
            
        connection.close()
        print(' [*] Consumo de mensagens interrompido')
        
    except Exception as e:
        print(f"Erro na thread de consumo: {str(e)}")
    finally:
        processar_mensagens = False

@app.route('/iniciar-processamento', methods=['GET'])
def iniciar_processamento():
    """Endpoint para iniciar o processamento contínuo de pedidos"""
    global processar_mensagens, consumer_thread
    
    if processar_mensagens:
        return jsonify({'mensagem': 'Processamento já está em andamento'}), 200
    
    processar_mensagens = True
    consumer_thread = threading.Thread(target=iniciar_consumo)
    consumer_thread.daemon = True
    consumer_thread.start()
    
    return jsonify({'mensagem': 'Processamento de pedidos iniciado com sucesso'}), 200

@app.route('/parar-processamento', methods=['GET'])
def parar_processamento():
    """Endpoint para parar o processamento contínuo de pedidos"""
    global processar_mensagens
    
    if not processar_mensagens:
        return jsonify({'mensagem': 'Processamento não está em andamento'}), 200
    
    processar_mensagens = False
    
    # Aguarda a thread terminar (com timeout)
    if consumer_thread and consumer_thread.is_alive():
        consumer_thread.join(timeout=5.0)
    
    return jsonify({'mensagem': 'Processamento de pedidos interrompido com sucesso'}), 200

@app.route('/processar-pedidos', methods=['GET'])
def endpoint_processar_pedidos():
    """Endpoint que dispara o processamento individual de um pedido (manter compatibilidade)"""
    try:
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            virtual_host='/',
            credentials=credentials
        )
        
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        # Tenta obter uma mensagem da fila (sem auto_ack)
        method_frame, header_frame, body = channel.basic_get(
            queue=QUEUE_PEDIDOS,
            auto_ack=False
        )
        
        if method_frame:
            # Processa o pedido
            dados = json.loads(body)
            dados['status'] = 'processado_almoxarifado'
            pedido_processado = json.dumps(dados)
            
            # Publica o pedido processado
            channel.queue_declare(queue=QUEUE_PROCESSADOS)
            channel.queue_bind(
                exchange=EXCHANGE,
                queue=QUEUE_PROCESSADOS,
                routing_key=ROUTING_KEY_PROCESSADOS
            )
            
            channel.basic_publish(
                exchange=EXCHANGE,
                routing_key=ROUTING_KEY_PROCESSADOS,
                body=pedido_processado
            )
            
            # Confirma o processamento da mensagem original
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            
            # Fecha a conexão
            connection.close()
            
            # Retorna o pedido processado
            return jsonify({
                'mensagem': 'Pedido processado com sucesso',
                'pedido': dados
            }), 200
        else:
            connection.close()
            return jsonify({'mensagem': 'Nenhum pedido disponível para processamento'}), 200
            
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    try:
        app.run(debug=True, port=5001)
    except KeyboardInterrupt:
        print('Interrupted')
        processar_mensagens = False
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
