from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..models.pedido import Pedido
from ..schemas.pedido import PedidoCreate, PedidoResponse, PedidoUpdate
from ..services.rabbitmq_service import publicar_pedido

router = APIRouter(
    prefix="/pedidos",
    tags=["pedidos"],
    responses={404: {"description": "Não encontrado"}},
)

@router.post("/", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
def criar_pedido(pedido: PedidoCreate, db: Session = Depends(get_db)):
    """Cria um novo pedido e envia para a fila do RabbitMQ"""
    db_pedido = Pedido(
        id=pedido.id,
        produto=pedido.produto,
        quantidade=pedido.quantidade,
        status="enviado_almoxarifado"
    )
    
    db.add(db_pedido)
    db.commit()
    db.refresh(db_pedido)
    
    # Publica no RabbitMQ
    publicar_pedido(db_pedido)
    
    return db_pedido

@router.get("/", response_model=List[PedidoResponse])
def listar_pedidos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todos os pedidos"""
    return db.query(Pedido).offset(skip).limit(limit).all()

@router.get("/{pedido_id}", response_model=PedidoResponse)
def obter_pedido(pedido_id: str, db: Session = Depends(get_db)):
    """Obtém um pedido pelo ID"""
    db_pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if db_pedido is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return db_pedido

@router.patch("/{pedido_id}", response_model=PedidoResponse)
def atualizar_pedido(pedido_id: str, pedido: PedidoUpdate, db: Session = Depends(get_db)):
    """Atualiza um pedido pelo ID"""
    db_pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if db_pedido is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    # Atualiza os campos
    update_data = pedido.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_pedido, key, value)
    
    db.commit()
    db.refresh(db_pedido)
    return db_pedido

@router.delete("/{pedido_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_pedido(pedido_id: str, db: Session = Depends(get_db)):
    """Remove um pedido pelo ID"""
    db_pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if db_pedido is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    db.delete(db_pedido)
    db.commit()
    return None
