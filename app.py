"""
GHL API Proxy Server
Bypasses CORS restrictions for GHL API calls from iframed websites.

Credentials can be passed via:
1. Request headers: X-GHL-Token, X-GHL-Location-Id (takes priority)
2. Environment variables: GHL_TOKEN, GHL_LOCATION_ID (fallback)
"""

import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Default configuration from environment variables (fallback)
DEFAULT_GHL_TOKEN = os.environ.get('GHL_TOKEN', '')
DEFAULT_GHL_LOCATION_ID = os.environ.get('GHL_LOCATION_ID', '')
GHL_BASE_URL = 'https://services.leadconnectorhq.com'
GHL_API_VERSION = '2021-07-28'


def get_credentials():
    """
    Get GHL credentials from request headers or fall back to environment variables.
    Headers take priority: X-GHL-Token, X-GHL-Location-Id
    """
    token = request.headers.get('X-GHL-Token') or DEFAULT_GHL_TOKEN
    location_id = request.headers.get('X-GHL-Location-Id') or DEFAULT_GHL_LOCATION_ID
    return token, location_id


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for container orchestration."""
    return jsonify({
        'status': 'healthy',
        'service': 'ghl-proxy',
        'default_location': DEFAULT_GHL_LOCATION_ID[:8] + '...' if DEFAULT_GHL_LOCATION_ID else 'not configured',
        'accepts_custom_credentials': True
    })


@app.route('/proxy/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def proxy(endpoint):
    """
    Proxy requests to GHL API.

    Usage:
        GET  /proxy/contacts/search
        POST /proxy/contacts/search with JSON body

    Optional headers:
        X-GHL-Token: Your GHL API token (overrides default)
        X-GHL-Location-Id: Your GHL location ID (overrides default)
    """
    token, location_id = get_credentials()

    if not token:
        return jsonify({'error': 'GHL_TOKEN not configured. Pass X-GHL-Token header or set env var.'}), 500

    url = f"{GHL_BASE_URL}/{endpoint}"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Version': GHL_API_VERSION
    }

    # Add locationId header if available
    if location_id:
        headers['locationId'] = location_id

    try:
        # Forward the request to GHL API
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

        # Return the response from GHL API
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


@app.route('/contacts/search', methods=['POST'])
def search_contacts():
    """
    Convenience endpoint for searching contacts.
    Automatically includes locationId in request body.

    Optional headers:
        X-GHL-Token: Your GHL API token (overrides default)
        X-GHL-Location-Id: Your GHL location ID (overrides default)
    """
    token, location_id = get_credentials()

    if not token:
        return jsonify({'error': 'GHL_TOKEN not configured. Pass X-GHL-Token header or set env var.'}), 500

    url = f"{GHL_BASE_URL}/contacts/search"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Version': GHL_API_VERSION
    }

    # Get request body and ensure locationId is included
    body = request.json or {}
    if 'locationId' not in body and location_id:
        body['locationId'] = location_id

    try:
        response = requests.post(url, headers=headers, json=body)
        return Response(
            response.content,
            status=response.status_code,
            content_type='application/json'
        )
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Failed to reach GHL API',
            'details': str(e)
        }), 502


@app.route('/contacts/<contact_id>', methods=['GET', 'PUT', 'DELETE'])
def contact_operations(contact_id):
    """
    Convenience endpoint for single contact operations.

    Optional headers:
        X-GHL-Token: Your GHL API token (overrides default)
        X-GHL-Location-Id: Your GHL location ID (overrides default)
    """
    token, location_id = get_credentials()

    if not token:
        return jsonify({'error': 'GHL_TOKEN not configured. Pass X-GHL-Token header or set env var.'}), 500

    url = f"{GHL_BASE_URL}/contacts/{contact_id}"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Version': GHL_API_VERSION
    }

    if location_id:
        headers['locationId'] = location_id

    try:
        if request.method == 'GET':
            response = requests.get(url, headers=headers)
        elif request.method == 'PUT':
            response = requests.put(url, headers=headers, json=request.json)
        elif request.method == 'DELETE':
            response = requests.delete(url, headers=headers)

        return Response(
            response.content,
            status=response.status_code,
            content_type='application/json'
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
