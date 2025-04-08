from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from ..db.database import Base

class Pedido(Base):
    """Modelo de dados para pedidos"""
    __tablename__ = "pedidos"
    
    id = Column(String, primary_key=True, index=True)
    produto = Column(String, index=True)
    quantidade = Column(Integer)
    status = Column(String, default="enviado_almoxarifado")
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    data_atualizacao = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Pedido id={self.id} produto={self.produto}>"
