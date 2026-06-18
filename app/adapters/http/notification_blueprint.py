from flask import Blueprint, request, jsonify
from app.infrastructure.container import Container

bp = Blueprint("notifications", __name__, url_prefix="/notifications")


def _container() -> Container:
    """Obtiene el container de dependencias del contexto de la app."""
    from flask import current_app
    return current_app.extensions["container"]


@bp.post("/send")
def send_notification():
    """Enviar una nueva notificación."""
    data = request.get_json(silent=True) or {}
    required = ["recipient", "subject", "body", "channel"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Campos requeridos: {missing}"}), 400

    try:
        notification = _container().send_notification_use_case().execute(
            recipient=data["recipient"],
            subject=data["subject"],
            body=data["body"],
            channel=data["channel"],
        )
        return jsonify(notification.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 422


@bp.get("/<notification_id>/status")
def get_status(notification_id: str):
    """Obtener el estado de una notificación por ID."""
    try:
        notification = _container().get_status_use_case().execute(notification_id)
        return jsonify(notification.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@bp.get("/history")
def list_notifications():
    """Listar notificaciones con filtros opcionales."""
    status = request.args.get("status")
    channel = request.args.get("channel")
    limit = min(int(request.args.get("limit", 20)), 100)
    offset = int(request.args.get("offset", 0))

    try:
        result = _container().list_notifications_use_case().execute(
            status=status,
            channel=channel,
            limit=limit,
            offset=offset,
        )
        return jsonify({
            "items": [n.to_dict() for n in result["items"]],
            "total": result["total"],
            "limit": result["limit"],
            "offset": result["offset"],
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 422


@bp.post("/retry/<notification_id>")
def retry_notification(notification_id: str):
    """Reintentar el envío de una notificación fallida."""
    try:
        notification = _container().retry_notification_use_case().execute(notification_id)
        return jsonify(notification.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
