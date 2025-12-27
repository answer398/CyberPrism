from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import db, ContainerInstance
from app.utils import get_current_user
from app.docker_challenges import DockerManager

bp = Blueprint('containers', __name__, url_prefix='/api/containers')
docker_manager = DockerManager()


@bp.route('/start/<int:challenge_id>', methods=['POST'])
@jwt_required()
def start_container(challenge_id):
    """启动容器"""
    user = get_current_user()

    try:
        instance = docker_manager.start_container(user.id, challenge_id)
        return jsonify({
            'message': '容器启动成功',
            'container': instance.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<int:instance_id>/stop', methods=['POST'])
@jwt_required()
def stop_container(instance_id):
    """停止容器"""
    user = get_current_user()

    try:
        docker_manager.stop_container(instance_id, user_id=user.id, is_admin=user.is_admin)
        return jsonify({'message': '容器已停止'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<int:instance_id>/extend', methods=['POST'])
@jwt_required()
def extend_container(instance_id):
    """延长容器时间"""
    user = get_current_user()
    data = request.get_json() or {}
    minutes = data.get('minutes', 30)

    if minutes < 10 or minutes > 60:
        return jsonify({'error': '延长时间必须在10-60分钟之间'}), 400

    try:
        instance = docker_manager.extend_container(instance_id, user_id=user.id, minutes=minutes, is_admin=False)
        return jsonify({
            'message': f'容器时间已延长{minutes}分钟',
            'container': instance.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/my', methods=['GET'])
@jwt_required()
def get_my_containers():
    """获取当前用户的容器列表"""
    user = get_current_user()
    containers = docker_manager.get_user_containers(user.id)

    return jsonify([c.to_dict() for c in containers]), 200


@bp.route('/<int:instance_id>', methods=['GET'])
@jwt_required()
def get_container_info(instance_id):
    """获取容器信息"""
    user = get_current_user()
    instance = db.session.get(ContainerInstance, instance_id)

    if not instance:
        return jsonify({'error': '容器不存在'}), 404

    # 权限检查
    if not user.is_admin and instance.user_id != user.id:
        return jsonify({'error': '无权限查看此容器'}), 403

    return jsonify(instance.to_dict()), 200
