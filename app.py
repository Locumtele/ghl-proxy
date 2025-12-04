"""
GHL API Proxy - CORS bypass
Base URL hardcoded, everything else dynamic.
"""

import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Only this is hardcoded
GHL_BASE_URL = 'https://services.leadconnectorhq.com'
GHL_API_VERSION = '2021-07-28'


@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'base_url': GHL_BASE_URL})


@app.route('/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def proxy(endpoint):
    """
    Forwards to: https://services.leadconnectorhq.com/{endpoint}

    Headers:
        X-GHL-Token: required
        X-GHL-Location-Id: optional
    """
    token = request.headers.get('X-GHL-Token')
    if not token:
        return jsonify({'error': 'Missing X-GHL-Token header'}), 400

    url = f"{GHL_BASE_URL}/{endpoint}"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Version': GHL_API_VERSION
    }

    location_id = request.headers.get('X-GHL-Location-Id')
    if location_id:
        headers['locationId'] = location_id

    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            params=request.args,
            json=request.json if request.is_json else None
        )
        return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type', 'application/json'))
    except Exception as e:
        return jsonify({'error': str(e)}), 502


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
