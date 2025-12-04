"""
Generic GHL API Proxy Server
Bypasses CORS restrictions - fully dynamic endpoints and credentials.

All values passed via request headers or body - nothing hardcoded.
"""

import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

GHL_BASE_URL = 'https://services.leadconnectorhq.com'
GHL_API_VERSION = '2021-07-28'


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'ghl-proxy',
        'mode': 'dynamic'
    })


@app.route('/proxy', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def proxy():
    """
    Generic proxy - all parameters passed dynamically.

    Required headers:
        X-GHL-Token: Your GHL API token
        X-GHL-Endpoint: The GHL endpoint path (e.g., /contacts/search, /contacts/{{contact_id}})

    Optional headers:
        X-GHL-Location-Id: Location ID (added to request headers)
        X-GHL-URL: Full URL override (ignores X-GHL-Endpoint, uses this instead)

    Body: JSON payload to forward to GHL API

    Examples:
        X-GHL-Endpoint: /contacts/search
        X-GHL-Endpoint: /contacts/abc123
        X-GHL-Endpoint: /users/xyz789
        X-GHL-URL: https://services.leadconnectorhq.com/contacts/search
    """
    # Get credentials and endpoint from headers
    token = request.headers.get('X-GHL-Token')
    endpoint = request.headers.get('X-GHL-Endpoint')
    location_id = request.headers.get('X-GHL-Location-Id')
    full_url = request.headers.get('X-GHL-URL')

    if not token:
        return jsonify({'error': 'Missing X-GHL-Token header'}), 400

    if not endpoint and not full_url:
        return jsonify({'error': 'Missing X-GHL-Endpoint or X-GHL-URL header'}), 400

    # Build target URL
    if full_url:
        url = full_url
    else:
        # Ensure endpoint starts with /
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        url = f"{GHL_BASE_URL}{endpoint}"

    # Build headers for GHL API
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Version': GHL_API_VERSION
    }

    if location_id:
        headers['locationId'] = location_id

    try:
        # Forward the request
        if request.method == 'GET':
            response = requests.get(url, headers=headers, params=request.args)
        elif request.method == 'POST':
            response = requests.post(url, headers=headers, json=request.json)
        elif request.method == 'PUT':
            response = requests.put(url, headers=headers, json=request.json)
        elif request.method == 'PATCH':
            response = requests.patch(url, headers=headers, json=request.json)
        elif request.method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            return jsonify({'error': 'Method not allowed'}), 405

        return Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get('Content-Type', 'application/json')
        )

    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Failed to reach GHL API',
            'details': str(e)
        }), 502


@app.route('/proxy/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def proxy_path(endpoint):
    """
    Alternative: Pass endpoint as URL path instead of header.

    Required headers:
        X-GHL-Token: Your GHL API token

    Optional headers:
        X-GHL-Location-Id: Location ID

    Examples:
        POST /proxy/contacts/search
        GET  /proxy/contacts/abc123
        GET  /proxy/users/xyz789
    """
    token = request.headers.get('X-GHL-Token')
    location_id = request.headers.get('X-GHL-Location-Id')

    if not token:
        return jsonify({'error': 'Missing X-GHL-Token header'}), 400

    url = f"{GHL_BASE_URL}/{endpoint}"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Version': GHL_API_VERSION
    }

    if location_id:
        headers['locationId'] = location_id

    try:
        if request.method == 'GET':
            response = requests.get(url, headers=headers, params=request.args)
        elif request.method == 'POST':
            response = requests.post(url, headers=headers, json=request.json)
        elif request.method == 'PUT':
            response = requests.put(url, headers=headers, json=request.json)
        elif request.method == 'PATCH':
            response = requests.patch(url, headers=headers, json=request.json)
        elif request.method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            return jsonify({'error': 'Method not allowed'}), 405

        return Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get('Content-Type', 'application/json')
        )

    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Failed to reach GHL API',
            'details': str(e)
        }), 502


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
