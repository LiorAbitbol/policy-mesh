# Metrics

Policy Mesh exposes Prometheus-format metrics at **GET /v1/metrics**. Use them for dashboards, alerting, and capacity planning.

---

## Endpoint

| Endpoint | Content-Type | Description |
|----------|--------------|-------------|
| `GET /v1/metrics` | `text/plain` (Prometheus exposition) | Counters and histograms for chat requests. |

**Example:**

```bash
curl -s http://localhost:8000/v1/metrics
```

---

## Metrics

### chat_requests_total

**Type:** Counter
**Description:** Total number of chat requests handled.

**Labels:**

| Label | Values | Description |
|-------|--------|-------------|
| `provider` | `local`, `openai` | Which provider handled the request. |
| `status` | `success`, `failure` | Outcome of the provider call. |

**Example:**

```
# HELP chat_requests_total Total chat requests
# TYPE chat_requests_total counter
chat_requests_total{provider="openai",status="success"} 42.0
chat_requests_total{provider="local",status="failure"} 1.0
```

---

### chat_request_latency_seconds

**Type:** Histogram
**Description:** End-to-end latency of chat requests (time to receive full response from the provider).

**Labels:**

| Label | Values | Description |
|-------|--------|-------------|
| `provider` | `local`, `openai` | Which provider handled the request. |

**Buckets (seconds):** `0.01`, `0.05`, `0.1`, `0.5`, `1.0`, `5.0` (plus `+Inf`).

**Example:**

```
# HELP chat_request_latency_seconds Chat request latency in seconds
# TYPE chat_request_latency_seconds histogram
chat_request_latency_seconds_bucket{provider="openai",le="0.01"} 0.0
chat_request_latency_seconds_bucket{provider="openai",le="0.05"} 0.0
...
chat_request_latency_seconds_bucket{provider="openai",le="+Inf"} 42.0
chat_request_latency_seconds_sum{provider="openai"} 125.3
chat_request_latency_seconds_count{provider="openai"} 42.0
```

---

## Scraping with Prometheus

Add a scrape config for the app. When the app runs in Docker Compose as service `app` on port 8000:

```yaml
scrape_configs:
  - job_name: policy-mesh
    static_configs:
      - targets: ['app:8000']
    metrics_path: /v1/metrics
```

If Prometheus runs on the host and the app is on localhost:

```yaml
scrape_configs:
  - job_name: policy-mesh
    static_configs:
      - targets: ['host.docker.internal:8000']
    metrics_path: /v1/metrics
```

Adjust `targets` to match your deployment (e.g. `localhost:8000` when running the app on the host).

---

## Example queries (PromQL)

- **Request rate by provider:** `rate(chat_requests_total[5m])`
- **Failure rate:** `rate(chat_requests_total{status="failure"}[5m]) / rate(chat_requests_total[5m])`
- **P95 latency by provider:** `histogram_quantile(0.95, rate(chat_request_latency_seconds_bucket[5m]))`
