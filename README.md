# GHL API Proxy

A generic CORS bypass proxy for GoHighLevel API calls. Fully dynamic - all credentials and endpoints passed per-request.

## Why This Exists

When your website is iframed inside GHL, browser CORS restrictions block direct API calls. This proxy runs server-side and forwards your requests.

## Usage

### Option 1: Endpoint in URL Path
```javascript
fetch('https://ghl-proxy.locumtele.org/proxy/contacts/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-GHL-Token': '{{key}}',
    'X-GHL-Location-Id': '{{location_id}}'
  },
  body: JSON.stringify({ pageLimit: 20 })
});

// Get a specific contact
fetch('https://ghl-proxy.locumtele.org/proxy/contacts/{{contact_id}}', {
  headers: {
    'X-GHL-Token': '{{key}}',
    'X-GHL-Location-Id': '{{location_id}}'
  }
});

// Get a specific user
fetch('https://ghl-proxy.locumtele.org/proxy/users/{{user_id}}', {
  headers: {
    'X-GHL-Token': '{{key}}',
    'X-GHL-Location-Id': '{{location_id}}'
  }
});
```

### Option 2: Endpoint in Header
```javascript
fetch('https://ghl-proxy.locumtele.org/proxy', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-GHL-Token': '{{key}}',
    'X-GHL-Location-Id': '{{location_id}}',
    'X-GHL-Endpoint': '/contacts/search'
  },
  body: JSON.stringify({ pageLimit: 20 })
});
```

### Option 3: Full URL Override
```javascript
fetch('https://ghl-proxy.locumtele.org/proxy', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-GHL-Token': '{{key}}',
    'X-GHL-URL': 'https://services.leadconnectorhq.com/contacts/search'
  },
  body: JSON.stringify({ locationId: '{{location_id}}', pageLimit: 20 })
});
```

## Headers Reference

| Header | Required | Description |
|--------|----------|-------------|
| `X-GHL-Token` | Yes | Your GHL API Bearer token |
| `X-GHL-Location-Id` | No | Location ID (added to request headers) |
| `X-GHL-Endpoint` | No* | GHL endpoint path (e.g., `/contacts/search`) |
| `X-GHL-URL` | No* | Full URL override |

*Either pass endpoint in URL path (`/proxy/contacts/search`) OR use `X-GHL-Endpoint` header OR use `X-GHL-URL` header.

## Endpoints

```
GET /health                    # Health check
ANY /proxy                     # Dynamic proxy (endpoint via header)
ANY /proxy/{ghl-endpoint}      # Dynamic proxy (endpoint in path)
```

## Deployment to Coolify

1. Go to Coolify: `http://44.254.48.227:8000`
2. Add Resource → Public Repository
3. Repo: `https://github.com/Locumtele/ghl-proxy`
4. Port: `5000`
5. Deploy

No environment variables needed - everything is passed per-request.

## DNS

Add A record: `ghl-proxy.locumtele.org` → `44.254.48.227`

## Local Development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Docker

```bash
docker build -t ghl-proxy .
docker run -p 5000:5000 ghl-proxy
```
