from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, jwt_required
from app.models import User, db


def admin_required(fn):
    """装饰器: 要求管理员权限"""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = int(get_jwt_identity())  # 转换字符串为整数
        user = db.session.get(User, user_id)

        if not user or not user.is_admin:
            return jsonify({'error': '需要管理员权限'}), 403

        return fn(*args, **kwargs)
    return wrapper


def get_current_user():
    """获取当前登录用户"""
    user_id = int(get_jwt_identity())  # 转换字符串为整数
    return db.session.get(User, user_id)
