# Postman — GnTech Weather API

## Importar

1. Abra o Postman
2. **Import** → selecione `GnTech-Weather-API.postman_collection.json`
3. **Import** → selecione `GnTech-Weather-API.postman_environment.json`
4. Selecione o environment **GnTech Weather API — Local** no canto superior direito

## Pré-requisito

O ambiente Docker deve estar rodando antes de executar a coleção:

```bash
docker-compose up --build
```

## Executar todos os testes

No Postman: clique na coleção → **Run collection**.

Via Newman (linha de comando):

```bash
npm install -g newman
newman run GnTech-Weather-API.postman_collection.json \
  -e GnTech-Weather-API.postman_environment.json
```

## Fluxos cobertos

### Readings — fluxos principais
| Request | O que valida |
|---|---|
| GET /health | Serviço respondendo |
| GET /readings | Lista retorna array com campos obrigatórios |
| GET /readings?city=Florianopolis | Filtro por cidade funciona |
| GET /readings?from_dt=...&to_dt=... | Filtro por período funciona |
| GET /readings/latest | Última leitura por cidade |
| GET /readings/stats | Estatísticas com max_temp >= min_temp |

### Segurança — OWASP API Top 10
| Request | Vetor | Resultado esperado |
|---|---|---|
| `?city=Florianopolis' OR '1'='1` | API3: SQL Injection | 200 com array vazio — query parametrizada, sem crash |
| `?from_dt=2026-01-01' OR '1'='1` | API3: SQL Injection via data | 422 — Pydantic rejeita o tipo inválido |
| `?city=AAA...` (10k chars) | API4: Input oversized | 422 — max_length=100 |
| `?limit=99999` | API4: Consumo excessivo | 422 — limite máximo é 500 |
| `GET /docs` (prod) | API8: Swagger em produção | 404 — indisponível com docker-compose.prod.yml |
| `GET /readings/latest` | API8: Chave exposta | Resposta não contém `appid` nem `openweather` |
| `?from_dt=2026-12-31&to_dt=2026-01-01` | Intervalo inválido | 422 com mensagem clara |
