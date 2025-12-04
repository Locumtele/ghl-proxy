# GHL API Proxy

A simple CORS bypass proxy for GoHighLevel API calls. Only the base URL is hardcoded - everything else is dynamic.

## Why This Exists

When your website is iframed inside GHL, browser CORS restrictions block direct API calls. This proxy runs server-side and forwards your requests.

## Usage

Just append your GHL endpoint to the proxy URL:

```javascript
// Search contacts
fetch('https://ghl-proxy.locumtele.org/contacts/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-GHL-Token': '{{key}}',
    'X-GHL-Location-Id': '{{location_id}}'
  },
  body: JSON.stringify({ pageLimit: 20 })
});

// Get a specific contact
fetch('https://ghl-proxy.locumtele.org/contacts/{{contact_id}}', {
  headers: {
    'X-GHL-Token': '{{key}}',
    'X-GHL-Location-Id': '{{location_id}}'
  }
});

// Get a specific user
fetch('https://ghl-proxy.locumtele.org/users/{{user_id}}', {
  headers: {
    'X-GHL-Token': '{{key}}'
  }
});

// Get opportunities
fetch('https://ghl-proxy.locumtele.org/opportunities/{{opportunity_id}}', {
  headers: {
    'X-GHL-Token': '{{key}}'
  }
});
```

**Any GHL API endpoint works** - just replace the base URL.

## Headers Reference

| Header | Required | Description |
|--------|----------|-------------|
| `X-GHL-Token` | Yes | Your GHL API Bearer token |
| `X-GHL-Location-Id` | No | Location ID (added to request headers) |

## Endpoints

```
GET  /health      # Health check
ANY  /{endpoint}  # Forwards to https://services.leadconnectorhq.com/{endpoint}
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
