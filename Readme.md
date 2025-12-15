
# FuelSense

> Você atua como Desenvolvedor Fullstack no Ministério dos Transportes e recebeu a missão
de criar uma solução para monitorar o mercado de combustíveis. Postos de gasolina de
diversas regiões irão enviar dados sobre vendas e preços, e você precisa coletar, armazenar e
exibir essas informações de forma gerencial.
Os dados chegam de forma bruta e precisam ser consolidados para que os gestores
possam ver o comportamento dos preços e do consumo ao longo do tempo.

## Funcionalidades do Projeto

- **Dashboard Analítico**: Visualização de KPIs e dados de coleta com gráficos interativos
- **Autenticação**: Sistema seguro de login com JWT
- **Histórico de Coletas**: Registro completo de dados de combustível
- **Cache Inteligente**: Redis para otimização de performance

## Estrutura de Execução

### Pré-requisitos

- Docker e Docker Compose
- Node.js 20+ (desenvolvimento local)
- Python 3.10+ (desenvolvimento local)

### Rodando com Docker

```bash
docker-compose up --build -d
```


##  Estrutura

- `backend/`: API FastAPI com autenticação semelhante a Oauth2, integração com banco de dados e cache Redis
- `frontend/`: Aplicação Angular 20 com componentes de gráficos e dashboard para consumir os dados filtrados de suas Fontes

## 🔗 Acesso

- Frontend: http://localhost:4200
- API: http://localhost:8000/docs

## Credenciais de acesso ao sistema

```
username = "admin@teste.com"
password = "123456"
```

> Essas credenciais são necessarias para poder acessar a aplicação e observar o dashboard (O usuário pode acessar o sistema por até 7 dias)
