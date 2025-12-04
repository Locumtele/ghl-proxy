"""
GHL API Proxy Server
Bypasses CORS restrictions for GHL API calls from iframed websites.
"""

import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration from environment variables
GHL_TOKEN = os.environ.get('GHL_TOKEN', '')
GHL_LOCATION_ID = os.environ.get('GHL_LOCATION_ID', '')
GHL_BASE_URL = 'https://services.leadconnectorhq.com'
GHL_API_VERSION = '2021-07-28'


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for container orchestration."""
    return jsonify({
        'status': 'healthy',
        'service': 'ghl-proxy',
        'location_id': GHL_LOCATION_ID[:8] + '...' if GHL_LOCATION_ID else 'not configured'
    })


@app.route('/proxy/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def proxy(endpoint):
    """
    Proxy requests to GHL API.

    Usage:
        GET  /proxy/contacts/search
        POST /proxy/contacts/search with JSON body
    """
    if not GHL_TOKEN:
        return jsonify({'error': 'GHL_TOKEN not configured'}), 500

    url = f"{GHL_BASE_URL}/{endpoint}"

    headers = {
        'Authorization': f'Bearer {GHL_TOKEN}',
        'Content-Type': 'application/json',
        'Version': GHL_API_VERSION
    }

    # Add locationId header if configured
    if GHL_LOCATION_ID:
        headers['locationId'] = GHL_LOCATION_ID

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
    """
    if not GHL_TOKEN:
        return jsonify({'error': 'GHL_TOKEN not configured'}), 500

    url = f"{GHL_BASE_URL}/contacts/search"

    headers = {
        'Authorization': f'Bearer {GHL_TOKEN}',
        'Content-Type': 'application/json',
        'Version': GHL_API_VERSION
    }

    # Get request body and ensure locationId is included
    body = request.json or {}
    if 'locationId' not in body and GHL_LOCATION_ID:
        body['locationId'] = GHL_LOCATION_ID

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
    """
    if not GHL_TOKEN:
        return jsonify({'error': 'GHL_TOKEN not configured'}), 500

    url = f"{GHL_BASE_URL}/contacts/{contact_id}"

    headers = {
        'Authorization': f'Bearer {GHL_TOKEN}',
        'Content-Type': 'application/json',
        'Version': GHL_API_VERSION
    }

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
