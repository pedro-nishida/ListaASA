# Sistema de Controle de Pedidos e Almoxarifado

Sistema para gerenciamento de pedidos e almoxarifado usando RabbitMQ para comunicação assíncrona entre os componentes.

## Visão Geral

O sistema consiste em dois componentes principais:

1. **Publisher (Pedidos)**: Envia pedidos para uma fila no RabbitMQ
2. **Consumer (Almoxarifado)**: Processa os pedidos da fila quando disponível

## Fluxo de Trabalho

```
[Usuário] -> python publisher.py "Produto" 10 -> [RabbitMQ: fila_pedidos]
                                                         |
                                                         v
[RabbitMQ: fila_processados] <- [Consumer: processa pedido]
```

## Requisitos

- Python 3.6+
- RabbitMQ Server
- Biblioteca pika

## Instalação

1. Clone o repositório ou baixe os arquivos
2. Instale as dependências:

```bash
pip install pika
```

3. Certifique-se de que o servidor RabbitMQ esteja em execução:

```bash
# Ubuntu/Debian
sudo service rabbitmq-server start

# Windows (via comando, após instalação)
rabbitmq-server start
```

## Como Usar

### Publicar um pedido

```bash
python publisher.py "Nome do Produto" <quantidade>

# Exemplo:
python publisher.py "Smartphone" 5
```

### Processar pedidos

#### Modo único (processa um pedido de cada vez)
```bash
python consumer.py
```

#### Modo contínuo (aguarda novos pedidos indefinidamente)
```bash
python consumer.py --continuo
```

## Estrutura das Mensagens

### Pedido enviado
```json
{
    "id": "uuid-gerado-automaticamente",
    "produto": "Nome do Produto",
    "quantidade": 5,
    "status": "enviado_almoxarifado"
}
```

### Pedido processado
```json
{
    "id": "mesmo-uuid-do-pedido-original",
    "produto": "Nome do Produto",
    "quantidade": 5,
    "status": "processado_almoxarifado"
}
```

## Acessando o RabbitMQ Management Console

Para monitorar filas e mensagens:

1. Habilite o plugin de gerenciamento (se ainda não estiver habilitado):
```bash
sudo rabbitmq-plugins enable rabbitmq_management
```

2. Acesse o console de gerenciamento:
   - URL: http://localhost:15672
   - Usuário padrão: guest
   - Senha padrão: guest

## Detalhes Técnicos

- O sistema utiliza o exchange `amq.direct` do RabbitMQ
- Filas utilizadas:
  - `fila_pedidos`: Armazena pedidos a serem processados
  - `fila_processados`: Armazena pedidos já processados pelo almoxarifado
- Routing keys:
  - `pedido`: Para mensagens de pedidos
  - `pedido_processado`: Para mensagens de pedidos processados
