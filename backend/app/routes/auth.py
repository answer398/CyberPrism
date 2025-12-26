from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import db, User
from app.utils import hash_password, verify_password

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()

    # 验证必填字段
    required_fields = ['username', 'email', 'password', 'display_name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'缺少必填字段: {field}'}), 400

    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 400

    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已存在'}), 400

    # 创建新用户
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hash_password(data['password']),
        display_name=data['display_name'],
        common_id=data.get('common_id', ''),
        is_admin=False
    )

    db.session.add(user)
    db.session.commit()

    # 生成JWT令牌 (identity必须是字符串)
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        'message': '注册成功',
        'access_token': access_token,
        'user': user.to_dict()
    }), 201


@bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400

    # 查找用户
    user = User.query.filter_by(username=username).first()

    if not user or not verify_password(password, user.password_hash):
        return jsonify({'error': '用户名或密码错误'}), 401

    # 生成JWT令牌 (identity必须是字符串)
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        'message': '登录成功',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user_info():
    """获取当前用户信息"""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({'error': '用户不存在'}), 404

    return jsonify(user.to_dict(include_skills=True)), 200


@bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """更新当前用户信息"""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({'error': '用户不存在'}), 404

    data = request.get_json()

    # 可更新的字段
    if 'display_name' in data:
        user.display_name = data['display_name']
    if 'common_id' in data:
        user.common_id = data['common_id']
    if 'email' in data:
        # 检查邮箱是否已被其他用户使用
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user.id:
            return jsonify({'error': '邮箱已被使用'}), 400
        user.email = data['email']

    # 修改密码
    if 'new_password' in data:
        if not data.get('old_password'):
            return jsonify({'error': '需要提供旧密码'}), 400
        if not verify_password(data['old_password'], user.password_hash):
            return jsonify({'error': '旧密码错误'}), 400
        user.password_hash = hash_password(data['new_password'])

    db.session.commit()

    return jsonify({
        'message': '更新成功',
        'user': user.to_dict()
    }), 200
