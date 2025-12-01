# Mikel's Coupons Microservice

Microservicio independiente para generación y validación de cupones únicos de descuento.

## Endpoints

### POST /api/coupon/generate
Genera un cupón único para un email.

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "coupon_code": "MIKELS10-ABC123XY",
  "message": "Coupon generated successfully"
}
```

### POST /api/coupon/validate
Valida si un cupón es válido.

**Request:**
```json
{
  "code": "MIKELS10-ABC123XY",
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "valid": true,
  "discount_percent": 10,
  "code": "MIKELS10-ABC123XY"
}
```

### POST /api/coupon/use
Marca un cupón como usado.

**Request:**
```json
{
  "code": "MIKELS10-ABC123XY",
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Coupon marked as used"
}
```

## Deploy en Railway

1. Crear nuevo servicio desde este repositorio
2. Conectar a la misma base de datos PostgreSQL
3. Railway agregará automáticamente `DATABASE_URL`
4. El servicio estará disponible en la URL asignada por Railway

## Variables de Entorno Requeridas

- `DATABASE_URL`: URL de conexión a PostgreSQL (automática en Railway)
- `PORT`: Puerto del servicio (automático en Railway)
