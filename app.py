"""
Microservicio independiente para generación y validación de cupones únicos
"""
import os
import secrets
import string
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)  # Permitir CORS para que el frontend pueda llamarlo

# Obtener DATABASE_URL de las variables de entorno
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    """Crear conexión a PostgreSQL"""
    return psycopg2.connect(DATABASE_URL)

def generate_coupon_code():
    """Generar código de cupón único: MIKELS10-XXXXXXXX"""
    random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    return f"MIKELS10-{random_part}"

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'mikels-coupons'}), 200

@app.route('/api/coupon/generate', methods=['POST'])
def generate_coupon():
    """
    Generar cupón único para un email
    Request: {"email": "user@example.com"}
    Response: {"coupon_code": "MIKELS10-ABC123XY", "success": true}
    """
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Verificar si el email ya tiene un cupón
        cursor.execute(
            "SELECT code FROM coupons WHERE email = %s AND used = FALSE LIMIT 1",
            (email,)
        )
        existing_coupon = cursor.fetchone()
        
        if existing_coupon:
            # Ya tiene un cupón, devolver el existente
            cursor.close()
            conn.close()
            return jsonify({
                'success': True,
                'coupon_code': existing_coupon['code'],
                'message': 'Existing coupon returned'
            }), 200
        
        # Generar nuevo cupón
        coupon_code = generate_coupon_code()
        
        # Guardar en base de datos
        cursor.execute(
            """
            INSERT INTO coupons (code, email, discount_percent, used, created_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING code
            """,
            (coupon_code, email, 10, False, datetime.now())
        )
        
        conn.commit()
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'coupon_code': result['code'],
            'message': 'Coupon generated successfully'
        }), 200
        
    except Exception as e:
        print(f"Error generating coupon: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/coupon/validate', methods=['POST'])
def validate_coupon():
    """
    Validar si un cupón es válido
    Request: {"code": "MIKELS10-ABC123XY", "email": "user@example.com"}
    Response: {"valid": true, "discount_percent": 10}
    """
    try:
        data = request.get_json()
        code = data.get('code')
        email = data.get('email')
        
        if not code or not email:
            return jsonify({'error': 'Code and email are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(
            """
            SELECT code, email, discount_percent, used 
            FROM coupons 
            WHERE code = %s AND email = %s
            """,
            (code, email)
        )
        
        coupon = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not coupon:
            return jsonify({
                'valid': False,
                'error': 'Coupon not found or does not belong to this email'
            }), 404
        
        if coupon['used']:
            return jsonify({
                'valid': False,
                'error': 'Coupon already used'
            }), 400
        
        return jsonify({
            'valid': True,
            'discount_percent': coupon['discount_percent'],
            'code': coupon['code']
        }), 200
        
    except Exception as e:
        print(f"Error validating coupon: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/coupon/use', methods=['POST'])
def use_coupon():
    """
    Marcar cupón como usado
    Request: {"code": "MIKELS10-ABC123XY", "email": "user@example.com"}
    Response: {"success": true}
    """
    try:
        data = request.get_json()
        code = data.get('code')
        email = data.get('email')
        
        if not code or not email:
            return jsonify({'error': 'Code and email are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            UPDATE coupons 
            SET used = TRUE, used_at = %s 
            WHERE code = %s AND email = %s AND used = FALSE
            RETURNING code
            """,
            (datetime.now(), code, email)
        )
        
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        if not result:
            return jsonify({
                'success': False,
                'error': 'Coupon not found, already used, or does not belong to this email'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Coupon marked as used'
        }), 200
        
    except Exception as e:
        print(f"Error using coupon: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
