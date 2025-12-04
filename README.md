# GHL API Proxy

A simple Flask proxy server to bypass CORS restrictions when making GoHighLevel API calls from iframed websites.

## Why This Exists

When your website is iframed inside GHL, browser CORS restrictions block direct API calls to `services.leadconnectorhq.com`. This proxy runs server-side (no CORS) and forwards your requests.

## Endpoints

### Health Check
```
GET /health
```

### Generic Proxy
```
GET/POST/PUT/DELETE /proxy/{ghl-endpoint}
```
Forwards any request to `https://services.leadconnectorhq.com/{ghl-endpoint}`

### Convenience Endpoints
```
POST /contacts/search          # Search contacts (auto-adds locationId)
GET  /contacts/{contact_id}    # Get single contact
PUT  /contacts/{contact_id}    # Update contact
```

## Usage from Your Website

### Option 1: Use Default Credentials (from environment variables)
```javascript
// Proxy uses GHL_TOKEN and GHL_LOCATION_ID from server env vars
const response = await fetch('https://ghl-proxy.locumtele.org/contacts/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    pageLimit: 20
    // locationId auto-added by proxy
  })
});
```

### Option 2: Pass Custom Credentials (per-request)
```javascript
// Override with your own token and location ID via headers
const response = await fetch('https://ghl-proxy.locumtele.org/contacts/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-GHL-Token': 'pit-your-token-here',
    'X-GHL-Location-Id': 'YourLocationId123'
  },
  body: JSON.stringify({
    pageLimit: 20
  })
});
```

**Header priority:** Request headers (`X-GHL-Token`, `X-GHL-Location-Id`) override environment variables.

## Deployment to Coolify

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial GHL proxy"
git remote add origin https://github.com/YOUR_USERNAME/ghl-proxy.git
git push -u origin main
```

### 2. Add to Coolify
1. Go to Coolify Dashboard: `http://44.254.48.227:8000`
2. Click **Add Resource** → **Public Repository**
3. Enter your GitHub repo URL
4. Set **Branch**: `main`
5. Set **Domain**: `ghl-proxy.locumtele.org`
6. Click **Deploy**

### 3. Add Environment Variables in Coolify
In the service settings, add:
```
GHL_TOKEN=pit-f768897c-2360-44cb-8eeb-af2323df011e
GHL_LOCATION_ID=RNRx3ZaPG9Zw6DjL5cRb
```

### 4. Add DNS Record
Create A record: `ghl-proxy.locumtele.org` → `44.254.48.227`

## Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GHL_TOKEN="your-token"
export GHL_LOCATION_ID="your-location-id"

# Run
python app.py
```

## Docker

```bash
# Build
docker build -t ghl-proxy .

# Run
docker run -p 5000:5000 \
  -e GHL_TOKEN="your-token" \
  -e GHL_LOCATION_ID="your-location-id" \
  ghl-proxy
```

## Security Notes

- Never expose your GHL_TOKEN in client-side code
- The proxy keeps your token server-side
- Consider adding rate limiting for production
- Consider adding authentication if the proxy is public

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GHL_TOKEN` | No* | Default GHL API Bearer token |
| `GHL_LOCATION_ID` | No* | Default GHL Sub-account/Location ID |
| `PORT` | No | Server port (default: 5000) |

*Can be passed per-request via `X-GHL-Token` and `X-GHL-Location-Id` headers instead.
