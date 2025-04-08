from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Pedido Service API"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/pedidos")
    
    # RabbitMQ
    RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST", "rabbitmq")
    RABBITMQ_PORT: int = int(os.getenv("RABBITMQ_PORT", "5672"))
    RABBITMQ_USER: str = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD: str = os.getenv("RABBITMQ_PASSWORD", "guest")
    RABBITMQ_EXCHANGE: str = os.getenv("RABBITMQ_EXCHANGE", "amq.direct")
    
    # Filas e Routing Keys
    QUEUE_PEDIDOS: str = os.getenv("QUEUE_PEDIDOS", "pedidos_para_almoxarifado")
    ROUTING_KEY_PEDIDOS: str = os.getenv("ROUTING_KEY_PEDIDOS", "pedidos")
    
    class Config:
        env_file = ".env"

settings = Settings()
