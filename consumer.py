import json
import pika
import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Optional
import uvicorn
import threading

app = FastAPI(title="API de Almoxarifado", 
              description="Sistema de processamento de pedidos com RabbitMQ",
              version="1.0.0")

# Modelo Pydantic para respostas de processamento
class ProcessamentoResponse(BaseModel):
    mensagem: str
    pedido_original: Optional[Dict] = None
    pedido_processado: Optional[Dict] = None

# Configuração melhorada do RabbitMQ com autenticação explícita
def get_rabbitmq_connection():
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters(
        host='localhost',
        port=5672,
        virtual_host='/',
        credentials=credentials
    )
    return pika.BlockingConnection(parameters=parameters)

@app.get("/processar-pedido", response_model=ProcessamentoResponse)
async def processar_pedido():
    try:
        # Conectar ao RabbitMQ
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Declarar filas e bind com exchange
        channel.queue_declare(queue='pedidos')
        channel.queue_bind(
            exchange='amq.direct',
            queue='pedidos',
            routing_key='pedido'
        )
        
        channel.queue_declare(queue='pedidos_processados')
        channel.queue_bind(
            exchange='amq.direct',
            queue='pedidos_processados',
            routing_key='pedido_processado'
        )
        
        # Verificar se há mensagens na fila
        method_frame, header_frame, body = channel.basic_get(queue='pedidos', auto_ack=True)
        
        if method_frame:
            # Processar o pedido
            pedido = json.loads(body)
            
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
            return {
                "mensagem": "Pedido processado com sucesso",
                "pedido_original": pedido,
                "pedido_processado": pedido_processado
            }
        else:
            connection.close()
            return {"mensagem": "Não há pedidos para processar"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao processar pedido: {str(e)}")

@app.get("/")
async def root():
    return {"mensagem": "API de Almoxarifado - Use /docs para ver a documentação completa"}

# Adicionar função para consumo contínuo (modo daemon)
def start_consumer():
    def callback(ch, method, properties, body):
        pedido = json.loads(body)
        print(f"[x] Pedido recebido: {pedido['id']}")
        
        # Processar o pedido
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
        print(f"[x] Pedido processado: {pedido['id']}")
    
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        channel.queue_declare(queue='pedidos')
        channel.queue_bind(
            exchange='amq.direct',
            queue='pedidos',
            routing_key='pedido'
        )
        
        channel.queue_declare(queue='pedidos_processados')
        channel.queue_bind(
            exchange='amq.direct',
            queue='pedidos_processados',
            routing_key='pedido_processado'
        )
        
        channel.basic_consume(
            queue='pedidos',
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
    # Escolha entre iniciar a API FastAPI ou o consumidor
    
    # Iniciar o consumidor em uma thread separada se necessário
    # consumer_thread = threading.Thread(target=start_consumer)
    # consumer_thread.daemon = True
    # consumer_thread.start()
    
    # Iniciar o servidor FastAPI
    uvicorn.run("consumer:app", host="0.0.0.0", port=5001, reload=True)
    
    # Ou para iniciar apenas o consumidor (descomente a linha abaixo):
    # start_consumer()
