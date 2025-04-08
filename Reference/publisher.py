import pika
import json
import sys
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configurações do RabbitMQ
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
QUEUE_PEDIDOS = 'pedidos_para_almoxarifado'
EXCHANGE = 'amq.direct'
ROUTING_KEY = 'pedidos'

def conectar_rabbitmq():
    """Estabelece conexão com o RabbitMQ usando credenciais"""
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host='/',
        credentials=credentials
    )
    
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    # Declara a fila e faz o binding com o exchange
    channel.queue_declare(queue=QUEUE_PEDIDOS)
    channel.queue_bind(
        exchange=EXCHANGE,
        queue=QUEUE_PEDIDOS,
        routing_key=ROUTING_KEY
    )
    
    return connection, channel

@app.route('/enviar-pedido', methods=['POST'])
def enviar_pedido():
    """Endpoint para enviar pedidos para o almoxarifado"""
    try:
        dados = request.json
        
        # Valida os dados recebidos
        if not dados or not all(key in dados for key in ['id', 'produto', 'quantidade']):
            return jsonify({'erro': 'Dados incompletos'}), 400
        
        # Adiciona o status
        dados['status'] = 'enviado_almoxarifado'
        
        # Converte para JSON
        mensagem = json.dumps(dados)
        
        # Conecta ao RabbitMQ
        connection, channel = conectar_rabbitmq()
        
        # Publica a mensagem
        channel.basic_publish(
            exchange=EXCHANGE,
            routing_key=ROUTING_KEY,
            body=mensagem
        )
        
        print(f" [x] Pedido enviado: {dados['id']} - {dados['produto']}")
        
        # Fecha a conexão
        connection.close()
        
        return jsonify({
            'mensagem': 'Pedido enviado com sucesso',
            'pedido': dados
        }), 201
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/enviar-pedido-lote', methods=['POST'])
def enviar_pedido_lote():
    """Endpoint para enviar múltiplos pedidos de uma vez"""
    try:
        pedidos = request.json
        
        if not isinstance(pedidos, list):
            return jsonify({'erro': 'Formato inválido. Envie uma lista de pedidos.'}), 400
        
        # Conecta ao RabbitMQ
        connection, channel = conectar_rabbitmq()
        
        pedidos_enviados = []
        for pedido in pedidos:
            # Valida os dados recebidos
            if not all(key in pedido for key in ['id', 'produto', 'quantidade']):
                continue
                
            # Adiciona o status
            pedido['status'] = 'enviado_almoxarifado'
            
            # Converte para JSON
            mensagem = json.dumps(pedido)
            
            # Publica a mensagem
            channel.basic_publish(
                exchange=EXCHANGE,
                routing_key=ROUTING_KEY,
                body=mensagem
            )
            
            pedidos_enviados.append(pedido)
            print(f" [x] Pedido enviado: {pedido['id']} - {pedido['produto']}")
        
        # Fecha a conexão
        connection.close()
        
        return jsonify({
            'mensagem': f'{len(pedidos_enviados)} pedidos enviados com sucesso',
            'pedidos': pedidos_enviados
        }), 201
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    try:
        app.run(debug=True, port=5000)
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
