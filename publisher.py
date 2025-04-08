import json
import pika
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn

# Modelo Pydantic para validação dos pedidos
class PedidoInput(BaseModel):
    id: Optional[str] = None
    produto: str
    quantidade: int = Field(gt=0)  # Garantindo que quantidade seja maior que zero

# Modelo Pydantic para respostas
class PedidoResponse(BaseModel):
    mensagem: str
    pedido: dict

app = FastAPI(title="API de Pedidos", 
              description="Sistema de controle de pedidos com RabbitMQ",
              version="1.0.0")

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

@app.post("/pedido", response_model=PedidoResponse, status_code=201)
async def criar_pedido(pedido_input: PedidoInput):
    # Gerar ID único se não fornecido
    if not pedido_input.id:
        pedido_input.id = uuid.uuid4().hex
    
    # Preparar mensagem para a fila
    pedido = {
        "id": pedido_input.id,
        "produto": pedido_input.produto,
        "quantidade": pedido_input.quantidade,
        "status": "enviado_almoxarifado"
    }
    
    # Enviar para a fila do RabbitMQ
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Declarar a fila e vincular ao exchange direto
        channel.queue_declare(queue='pedidos')
        channel.queue_bind(
            exchange='amq.direct',
            queue='pedidos',
            routing_key='pedido'
        )
        
        # Publicar mensagem com exchange adequado
        channel.basic_publish(
            exchange='amq.direct',
            routing_key='pedido',
            body=json.dumps(pedido).encode('utf-8')
        )
        
        connection.close()
        return {"mensagem": "Pedido enviado com sucesso", "pedido": pedido}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao enviar pedido: {str(e)}")

@app.get("/")
async def root():
    return {"mensagem": "API de Pedidos - Use /docs para ver a documentação completa"}

if __name__ == '__main__':
    uvicorn.run("publisher:app", host="0.0.0.0", port=5000, reload=True)
