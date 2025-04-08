from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PedidoBase(BaseModel):
    """Schema base para pedidos"""
    produto: str
    quantidade: int = Field(..., gt=0)

class PedidoCreate(PedidoBase):
    """Schema para criação de pedidos"""
    id: str

class PedidoUpdate(BaseModel):
    """Schema para atualização de pedidos"""
    produto: Optional[str] = None
    quantidade: Optional[int] = Field(None, gt=0)
    status: Optional[str] = None

class PedidoResponse(PedidoBase):
    """Schema para resposta de pedidos"""
    id: str
    status: str
    data_criacao: datetime
    data_atualizacao: Optional[datetime] = None
    
    class Config:
        orm_mode = True
