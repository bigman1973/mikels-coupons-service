"""Retired public coupon microservice.

Welcome coupons are now issued only by the main backend after it records the
subscriber's consent and atomically reserves their canonical email identity.
"""
import os

from flask import Flask, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

RETIREMENT_MESSAGE = (
    'This legacy coupon endpoint has been retired. '
    'Welcome coupons are issued only by the newsletter backend.'
)


@app.route('/health', methods=['GET'])
def health():
    """Health check retained for Railway monitoring."""
    return jsonify({'status': 'healthy', 'service': 'mikels-coupons', 'retired': True}), 200


def retired_response():
    return jsonify({'success': False, 'error': RETIREMENT_MESSAGE}), 410


@app.route('/api/coupon/generate', methods=['POST'])
def generate_coupon():
    return retired_response()


@app.route('/api/coupon/validate', methods=['POST'])
def validate_coupon():
    return retired_response()


@app.route('/api/coupon/use', methods=['POST'])
def use_coupon():
    return retired_response()


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
