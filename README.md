# Python — Notifications Service

## Flask · Arquitectura Hexagonal (Ports & Adapters)

---

## La idea central

En la arquitectura hexagonal el **dominio no depende de nada externo**.
Flask, SQLAlchemy, y los senders de email/SMS son adaptadores intercambiables.
El dominio solo conoce sus propias entidades y puertos (interfaces abstractas).

```
┌─────────────────────────────────────────────────┐
│                   DOMINIO                        │
│  Notification (entidad)                          │
│  NotificationRepositoryPort (interfaz)           │
│  NotificationSenderPort (interfaz)               │
│                                                  │
│  No importa Flask, SQLAlchemy, ni nada externo  │
└──────────────────┬──────────────────────────────┘
                   │ usa (solo interfaces)
┌──────────────────▼──────────────────────────────┐
│              CASOS DE USO                        │
│  SendNotification   GetNotificationStatus        │
│  ListNotifications  RetryNotification            │
└──────────────────┬──────────────────────────────┘
                   │ implementan las interfaces
┌──────────────────▼──────────────────────────────┐
│               ADAPTADORES                        │
│  SQLiteNotificationRepository (repositorio)      │
│  EmailSender / SmsSender / InAppSender           │
│  NotificationBlueprint (HTTP via Flask)          │
└─────────────────────────────────────────────────┘
```

---

## Estructura del proyecto

```
python-flask-hexagonal/
├── main.py                                      # Punto de entrada Flask
├── requirements.txt
├── notifications.db                             # Se genera automáticamente
└── app/
    ├── domain/                                  # ← núcleo puro, sin deps externas
    │   ├── entities/
    │   │   └── notification.py                  # Entidad + enums de dominio
    │   └── ports/
    │       ├── notification_repository_port.py  # Interfaz: persistencia
    │       └── notification_sender_port.py      # Interfaz: envío
    ├── application/
    │   └── use_cases/
    │       ├── send_notification.py             # Orquesta envío
    │       ├── get_notification_status.py       # Consulta por ID
    │       ├── list_notifications.py            # Lista con filtros
    │       └── retry_notification.py            # Reintenta fallidas
    ├── adapters/
    │   ├── http/
    │   │   └── notification_blueprint.py        # Rutas Flask
    │   ├── repositories/
    │   │   └── sqlite_notification_repository.py # Implementa el puerto con SQLAlchemy
    │   └── notifications/
    │       └── senders.py                       # Email/SMS/InApp simulados
    └── infrastructure/
        └── container.py                         # DI manual: conecta todo
```

---

## Requisitos previos

- **Python 3.10+**
  Verifica con: `python --version` o `python3 --version`

---

## Cómo correr el proyecto

### 1. Crea y activa un entorno virtual

```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 2. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 3. Corre el servidor

```bash
flask --app main run --debug --port 5000
```

O también:

```bash
python main.py
```

El servidor arranca en: **http://localhost:5000**

> La base de datos `notifications.db` se crea automáticamente al primer arranque.

### 4. Verifica que funciona

```
GET http://localhost:5000/
```

Respuesta esperada:

```json
{
  "status": "ok",
  "project": "Python - Flask Hexagonal Architecture",
  "channels": ["email", "sms", "in_app"]
}
```

---

## Cómo probarlo en Postman

### URL base

```
http://localhost:5000
```

---

### 1. Enviar una notificación por email

**POST** `/notifications/send`

Body (JSON):

```json
{
  "recipient": "usuario@example.com",
  "subject": "Bienvenido al sistema",
  "body": "Hola, tu cuenta ha sido activada exitosamente.",
  "channel": "email"
}
```

Valores válidos para `channel`: `"email"` · `"sms"` · `"in_app"`

Respuesta exitosa (201):

```json
{
  "id": "a1b2c3d4-...",
  "recipient": "usuario@example.com",
  "subject": "Bienvenido al sistema",
  "status": "sent",
  "channel": "email",
  "retry_count": 0,
  "created_at": "2025-01-01T12:00:00",
  "sent_at": "2025-01-01T12:00:01"
}
```

---

### 2. Enviar por SMS

**POST** `/notifications/send`

```json
{
  "recipient": "+52 33 1234 5678",
  "subject": "Alerta de seguridad",
  "body": "Se detectó un nuevo inicio de sesión en tu cuenta.",
  "channel": "sms"
}
```

---

### 3. Enviar notificación in-app

**POST** `/notifications/send`

```json
{
  "recipient": "user_id_123",
  "subject": "Tienes un nuevo mensaje",
  "body": "Juan te envió un mensaje directo.",
  "channel": "in_app"
}
```

---

### 4. Consultar estado de una notificación

**GET** `/notifications/{id}/status`

Reemplaza `{id}` con el `id` que devolvió el POST anterior.

Ejemplo: `GET /notifications/a1b2c3d4-e5f6.../status`

---

### 5. Ver historial de notificaciones

**GET** `/notifications/history`

Query params opcionales:

- `status` → `pending` · `sent` · `failed`
- `channel` → `email` · `sms` · `in_app`
- `limit` → máx registros (default 20, máx 100)
- `offset` → para paginación (default 0)

Ejemplos:

```
GET /notifications/history
GET /notifications/history?status=sent
GET /notifications/history?channel=email&limit=5
GET /notifications/history?status=failed&offset=10
```

---

### 6. Reintentar una notificación fallida

**POST** `/notifications/retry/{id}`

Funciona solo si la notificación está en status `failed` y tiene menos de 3 intentos.

---

## Colección Postman (importar)

Guarda como `p2-notifications.postman_collection.json` e impórtalo en Postman:

```json
{
  "info": {
    "name": "Python - Flask Notifications (Hexagonal)",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    { "key": "base_url", "value": "http://localhost:5000" },
    { "key": "notification_id", "value": "" }
  ],
  "item": [
    {
      "name": "Health Check",
      "request": { "method": "GET", "url": "{{base_url}}/" }
    },
    {
      "name": "Send Email Notification",
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "const r = pm.response.json(); if(r.id) pm.collectionVariables.set('notification_id', r.id);"
            ]
          }
        }
      ],
      "request": {
        "method": "POST",
        "url": "{{base_url}}/notifications/send",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "body": {
          "mode": "raw",
          "raw": "{\"recipient\": \"user@example.com\", \"subject\": \"Bienvenido\", \"body\": \"Tu cuenta fue activada.\", \"channel\": \"email\"}"
        }
      }
    },
    {
      "name": "Send SMS Notification",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/notifications/send",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "body": {
          "mode": "raw",
          "raw": "{\"recipient\": \"+52 33 1234 5678\", \"subject\": \"Alerta\", \"body\": \"Nuevo inicio de sesión detectado.\", \"channel\": \"sms\"}"
        }
      }
    },
    {
      "name": "Send In-App Notification",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/notifications/send",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "body": {
          "mode": "raw",
          "raw": "{\"recipient\": \"user_id_123\", \"subject\": \"Nuevo mensaje\", \"body\": \"Tienes un mensaje de Juan.\", \"channel\": \"in_app\"}"
        }
      }
    },
    {
      "name": "Get Notification Status",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/notifications/{{notification_id}}/status"
      }
    },
    {
      "name": "List All Notifications",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/notifications/history"
      }
    },
    {
      "name": "List Sent Notifications",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/notifications/history?status=sent"
      }
    },
    {
      "name": "List by Channel (email)",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/notifications/history?channel=email"
      }
    },
    {
      "name": "Retry Notification",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/notifications/retry/{{notification_id}}"
      }
    }
  ]
}
```

> El request "Send Email Notification" guarda el `id` automáticamente en `{{notification_id}}` para usarlo en los siguientes requests.

---

## Despliegue en Render

Este proyecto está desplegado como un **Web Service** en [Render](https://render.com).

### Pasos para desplegar

1. En el dashboard de Render, crea un nuevo **Web Service** y conecta el repositorio.

2. Configura el servicio:

   | Campo | Valor |
   |-------|-------|
   | **Environment** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `gunicorn main:app --bind 0.0.0.0:$PORT` |

   > Si no tienes `gunicorn` en `requirements.txt`, también puedes usar: `flask --app main run --host 0.0.0.0 --port $PORT` (solo para desarrollo/demo).

3. No se requieren variables de entorno. La base de datos `notifications.db` se crea automáticamente al arrancar.

4. Una vez desplegado, copia la URL pública (ej. `https://python-flask-hexagonal.onrender.com`) y pégala en el panel de ajustes de **API Explorer** para apuntar al entorno de producción.

---

## Diferencia clave vs python-fastapi-tasks (Layered)

|                            | python-fastapi-tasks     | python-flask-hexagonal    |
| -------------------------- | ------------------------ | ------------------------- |
| Dominio importa Flask      | Sí (indirectamente)      | **No, nunca**             |
| Dominio importa SQLAlchemy | Sí                       | **No, nunca**             |
| Cambiar DB                 | Requiere editar services | Solo cambiar el adaptador |
| Cambiar canal de envío     | Toca lógica de negocio   | Solo agregar un sender    |
| Testeable sin DB           | Difícil                  | **Sí, con mocks simples** |
