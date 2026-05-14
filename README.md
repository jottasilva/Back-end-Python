# Booking API

Servico responsavel por locais, salas e reservas. Ele valida o JWT emitido pelo Auth Service localmente e nunca faz chamada HTTP ao backend C# durante as operacoes.

A API foi implementada com FastAPI, SQLAlchemy 2, Pydantic v2 e Postgres. A regra central do sistema e impedir conflito de horario na mesma sala usando a condicao `start_novo < end_existente AND end_novo > start_existente`.

## Arquitetura

```mermaid
flowchart LR
    F["Frontend"] --> API["FastAPI routers"]
    API --> APP["Use cases"]
    APP --> REP["Repositories"]
    REP --> DB["Postgres booking-db"]
    API -. "JWT HS256 local" .-> JWT["JWT_SECRET"]
```

## Pre-requisitos

| Ferramenta | Versao |
| --- | --- |
| Python | 3.12 |
| Docker | 24+ |
| Postgres | 16 |

## Variaveis de ambiente

| Variavel | Obrigatoria | Descricao | Exemplo |
| --- | --- | --- | --- |
| `DATABASE_URL` | Sim | URL SQLAlchemy do banco de reservas. | `postgresql+psycopg://booking_user:booking_pass@localhost:5434/booking_db` |
| `JWT_SECRET` | Sim | Mesmo secret usado pelo Auth Service. | `mude-para-uma-string-secreta-com-32-chars-minimo` |
| `ALLOWED_ORIGINS` | Sim | Origins permitidas no CORS. | `http://localhost:5173` |

## Como rodar localmente

Via Docker Compose na raiz:

```bash
docker compose up --build booking-db booking-api
```

Via Python local:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

O schema e criado no startup e o seed inicial cadastra 2 locais e 5 salas.

## Endpoints

| Metodo | Rota | Auth | Body | Response |
| --- | --- | --- | --- | --- |
| GET | `/health` | Nao | - | `{ status: "ok" }` |
| GET | `/api/v1/reservations` | Sim | filtros `room_id`, `date`, `user_id` | lista de reservas |
| POST | `/api/v1/reservations` | Sim | dados da reserva | reserva criada |
| GET | `/api/v1/reservations/{id}` | Sim | - | detalhe da reserva |
| PUT | `/api/v1/reservations/{id}` | Sim | reserva completa | reserva atualizada |
| PATCH | `/api/v1/reservations/{id}` | Sim | campos parciais | reserva atualizada |
| DELETE | `/api/v1/reservations/{id}` | Sim | - | `204` |
| DELETE | `/api/v1/reservations` | Sim | `{ ids: [] }` | `204` |
| GET | `/api/v1/locations` | Sim | - | lista de locais |
| POST | `/api/v1/locations` | Sim | `{ name, address }` | local criado |
| PUT | `/api/v1/locations/{id}` | Sim | `{ name, address }` | local atualizado |
| DELETE | `/api/v1/locations/{id}` | Sim | - | `204` se nao houver salas vinculadas |
| GET | `/api/v1/locations/{id}/rooms` | Sim | - | salas do local |
| GET | `/api/v1/rooms` | Sim | filtro `location_id` | lista de salas |
| POST | `/api/v1/rooms` | Sim | dados da sala | sala criada |
| PUT | `/api/v1/rooms/{id}` | Sim | dados da sala | sala atualizada |
| DELETE | `/api/v1/rooms/{id}` | Sim | - | `204` se nao houver reservas vinculadas |

## Testes

```bash
pytest -q
```

Via Docker Compose:

```bash
docker compose run --rm booking-api pytest -q
```

## Decisoes tecnicas

| Decisao | Justificativa |
| --- | --- |
| FastAPI | Rapido para APIs RESTful com OpenAPI e validacao integrada. |
| SQLAlchemy 2 | ORM relacional robusto e explicito. |
| Pydantic v2 | Contratos de entrada e saida tipados. |
| Validacao local de JWT | Mantem a API de reservas independente do Auth Service. |
| `SELECT FOR UPDATE` no conflito | Reduz corrida de escrita para reservas simultaneas. |
| Seed inicial | Facilita testes manuais do frontend. |

