# Booking API

Servico Python em FastAPI responsavel por locais, salas e reservas. Ele valida localmente o JWT emitido pelo AuthService usando o mesmo `JWT_SECRET`, sem fazer chamada HTTP ao microsservico C#.

O banco de dados e independente do banco de autenticacao e usa SQLAlchemy 2 com PostgreSQL em producao/desenvolvimento via Docker.

## Arquitetura

```mermaid
flowchart LR
    FE["Frontend"] --> API["Booking API FastAPI"]
    API --> DB[("booking-db PostgreSQL")]
    FE -. "Bearer JWT" .-> API
    API -. "valida HS256 localmente" .-> API
```

## Endpoints

| Metodo | Rota | Auth | Descricao |
| --- | --- | --- | --- |
| GET | `/api/v1/reservations` | Sim | Lista reservas com filtros `room_id`, `date`, `user_id` |
| POST | `/api/v1/reservations` | Sim | Cria reserva |
| GET | `/api/v1/reservations/{id}` | Sim | Detalha reserva |
| PUT | `/api/v1/reservations/{id}` | Sim | Edita reserva completa |
| PATCH | `/api/v1/reservations/{id}` | Sim | Edita reserva parcial |
| DELETE | `/api/v1/reservations/{id}` | Sim | Exclui reserva individual |
| DELETE | `/api/v1/reservations` | Sim | Exclui reservas em lote |
| GET | `/api/v1/locations` | Sim | Lista unidades/filiais |
| POST | `/api/v1/locations` | Sim | Cria unidade/filial |
| PUT | `/api/v1/locations/{id}` | Sim | Edita unidade/filial |
| DELETE | `/api/v1/locations/{id}` | Sim | Exclui unidade sem salas vinculadas |
| GET | `/api/v1/locations/{id}/rooms` | Sim | Lista salas por unidade |
| GET | `/api/v1/rooms` | Sim | Lista salas com filtro `location_id` |
| POST | `/api/v1/rooms` | Sim | Cria sala |
| PUT | `/api/v1/rooms/{id}` | Sim | Edita sala |
| GET | `/health` | Nao | Healthcheck |

## Variaveis

| Variavel | Obrigatoria | Descricao | Exemplo |
| --- | --- | --- | --- |
| `DATABASE_URL` | Sim | Conexao PostgreSQL | `postgresql+psycopg://booking_user:booking_pass@localhost:5434/booking_db` |
| `JWT_SECRET` | Sim | Mesmo secret do AuthService | `mude-para-uma-string-secreta-com-32-chars-minimo` |
| `ALLOWED_ORIGINS` | Sim | Origins permitidas no CORS | `http://localhost:5173,http://127.0.0.1:5173` |

## Regra De Conflito

Uma reserva conflita quando:

```python
novo_inicio < fim_existente and novo_fim > inicio_existente
```

A validacao considera a mesma sala, exclui a propria reserva em edicao e usa `SELECT FOR UPDATE` via SQLAlchemy.

## Como Rodar

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Via Docker, na raiz do monorepo:

```powershell
docker compose up -d booking-db booking-api
```

## Testes

```powershell
pytest -q
```

Ambiente validado com Python 3.12 via Docker:

```powershell
docker compose run --rm --build booking-api pytest -q
```

## Seed

Na inicializacao, a API cria tabelas e insere pelo menos 2 unidades e 5 salas para facilitar testes manuais do frontend.

## Decisoes

- JWT validado localmente: evita acoplamento HTTP entre microsservicos e atende ao fluxo pedido no PDF.
- Banco separado: isolamento de dados entre autenticacao e reservas.
- Pydantic v2: validacao forte de entrada, incluindo data futura, timezone e `end_time > start_time`.
- Repositorios com Protocol: facilita testes e separa regra de negocio da camada HTTP.
