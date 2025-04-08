# PyEcho

A flexible HTTP echo and static response mock service for testing or simulation.

## Modes

- **echo**: Echo method, headers, body
- **static**: Return constant HTTP status
- **dual**: 200 on port 8080, 503 on 8081
- **map**: Use PYECHO_STATIC_MAP to define multiple ports/behaviors

## Usage

```bash
docker compose up --build
```

## Endpoints

On echo/path ports:
- `/healthz`
- `/status/<code>`
- `/bad-request`
- `/not-found`
- `/endpoints`
