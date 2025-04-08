
# PyEcho

PyEcho is a flexible, lightweight HTTP echo and status code responder server. It's ideal for testing reverse proxies, simulating upstream services, or mocking behavior in your local environment.

## 🔧 Features

- Echo request method, headers, path, and body
- Serve constant HTTP status codes (e.g., always 200, always 503)
- Expose test endpoints for status and health checks
- Map multiple ports to different behaviors
- Supports Docker and Docker Compose
- Graceful shutdown and healthchecks built-in

---

## 🚀 Quick Start (Docker Compose)

```bash
docker compose up --build
```

This starts:

- Kong Gateway (on ports `8000`, `8001`)
- PyEcho with:
  - Port `9000`: always returns 200
  - Port `9001`: always returns 503
  - Port `9002`: full echo
  - Port `9003`: dynamic routes like `/status/418`

---

## ⚙️ Server Modes

| Mode   | Description |
|--------|-------------|
| `echo` | Echo request data |
| `static` | Return a fixed HTTP status |
| `dual` | Port 8080 returns 200, Port 8081 returns 503 |
| `map` | Define behavior per port using static map |

---

## 📦 CLI Usage Examples

### Echo mode
```bash
python unified_echo_server.py --mode echo --port 8080
```

### Static 418 response
```bash
python unified_echo_server.py --mode static --port 9999 --status 418
```

### Dual-mode (200 and 503)
```bash
python unified_echo_server.py --mode dual
```

### Map mode
```bash
python unified_echo_server.py --mode map --static-map "200:9000,503:9001,echo:9002,path:9003"
```

---

## 🌐 Available Endpoints (echo/path modes)

| Path            | Description                  |
|-----------------|------------------------------|
| `/healthz`      | Always returns 200 OK         |
| `/status/503`   | Returns 503 Service Unavailable |
| `/bad-request`  | Returns 400 Bad Request      |
| `/not-found`    | Returns 404 Not Found        |
| `/endpoints`    | Returns list of all endpoints|

---

## 🛠 Configuration via Environment

You can set any of the CLI options using env vars:

| Env Var             | CLI Equivalent        |
|---------------------|-----------------------|
| `PYECHO_MODE`       | `--mode`              |
| `PYECHO_PORT`       | `--port`              |
| `PYECHO_STATUS`     | `--status`            |
| `PYECHO_STATIC_MAP` | `--static-map`        |
| `PYECHO_LOG_LEVEL`  | `--log-level`         |

---

## 📁 Project Structure

```
.
├── Dockerfile
├── docker-compose.yml
├── README.md
└── unified_echo_server.py
```

---

## ✅ Healthcheck

Docker Compose automatically checks:
```http
GET http://localhost:9003/healthz
```

---

## 📜 License

MIT License — use freely in local or testing environments.
