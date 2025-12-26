from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import db, User, Challenge, ContainerInstance, Submission, UserSkillTag
from app.utils import admin_required, hash_password
from app.docker_challenges import DockerManager
import json

bp = Blueprint('admin', __name__, url_prefix='/api/admin')
docker_manager = DockerManager()


# ========== 用户管理 ==========

@bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """获取所有用户列表"""
    users = User.query.all()
    return jsonify([user.to_dict(include_skills=True) for user in users]), 200


@bp.route('/users', methods=['POST'])
@admin_required
def create_user():
    """创建新用户"""
    data = request.get_json()

    required_fields = ['username', 'email', 'password', 'display_name', 'common_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必填字段: {field}'}), 400

    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 400

    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已被使用'}), 400

    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hash_password(data['password']),
        display_name=data['display_name'],
        common_id=data['common_id'],
        is_admin=data.get('is_admin', False)
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': '用户创建成功',
        'user': user.to_dict()
    }), 201


@bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def reset_user_password(user_id):
    """重置用户密码"""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    data = request.get_json()
    if 'new_password' not in data:
        return jsonify({'error': '缺少新密码'}), 400

    user.password_hash = hash_password(data['new_password'])
    db.session.commit()

    return jsonify({'message': '密码重置成功'}), 200


@bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user_detail(user_id):
    """获取用户详情"""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    # 获取技能标签
    skill_tags = UserSkillTag.query.filter_by(user_id=user_id).all()
    skills_matrix = {}
    for tag in skill_tags:
        if tag.category not in skills_matrix:
            skills_matrix[tag.category] = []
        skills_matrix[tag.category].append(tag.to_dict())

    # 获取解题记录
    submissions = Submission.query.filter_by(user_id=user_id).all()

    return jsonify({
        'user': user.to_dict(),
        'skills_matrix': skills_matrix,
        'submissions': [sub.to_dict() for sub in submissions]
    }), 200


@bp.route('/users/<int:user_id>', methods=['PUT'])

@admin_required
def update_user(user_id):
    """更新用户信息"""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    data = request.get_json()

    if 'display_name' in data:
        user.display_name = data['display_name']
    if 'common_id' in data:
        user.common_id = data['common_id']
    if 'email' in data:
        user.email = data['email']
    if 'is_admin' in data:
        user.is_admin = data['is_admin']
    if 'password' in data:
        user.password_hash = hash_password(data['password'])

    db.session.commit()
    return jsonify({'message': '更新成功', 'user': user.to_dict()}), 200


@bp.route('/users/<int:user_id>', methods=['DELETE'])

@admin_required
def delete_user(user_id):
    """删除用户"""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    if user.is_admin:
        return jsonify({'error': '不能删除管理员账户'}), 400

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': '用户已删除'}), 200


# ========== 题目管理 ==========

@bp.route('/challenges', methods=['GET'])

@admin_required
def get_all_challenges():
    """获取所有题目(包括未激活的)"""
    challenges = Challenge.query.all()
    return jsonify([c.to_dict(show_answer=True) for c in challenges]), 200


@bp.route('/challenges', methods=['POST'])

@admin_required
def create_challenge():
    """创建新题目"""
    data = request.get_json()

    required_fields = ['title', 'description', 'category', 'type']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必填字段: {field}'}), 400

    challenge = Challenge(
        title=data['title'],
        description=data['description'],
        category=data['category'],
        type=data['type'],
        difficulty=data.get('difficulty', 'medium'),
        points=data.get('points', 100),
        is_active=data.get('is_active', True)
    )

    if data['type'] == 'choice':
        challenge.question = data.get('question')
        challenge.options = json.dumps(data.get('options', {}), ensure_ascii=False)
        challenge.correct_answer = data.get('correct_answer')
    elif data['type'] == 'docker':
        challenge.flag = data.get('flag')
        # 支持 docker_image 字段(前端使用),存储到 docker_compose_file
        challenge.docker_compose_file = data.get('docker_image') or data.get('docker_compose_file')
        # 支持 docker_port 字段(前端使用),存储到 container_port
        challenge.container_port = data.get('docker_port') or data.get('container_port', 80)

    if 'skill_tags' in data:
        challenge.skill_tags = json.dumps(data['skill_tags'], ensure_ascii=False)

    db.session.add(challenge)
    db.session.commit()

    return jsonify({
        'message': '题目创建成功',
        'challenge': challenge.to_dict(show_answer=True)
    }), 201


@bp.route('/challenges/<int:challenge_id>', methods=['PUT'])

@admin_required
def update_challenge(challenge_id):
    """更新题目"""
    challenge = db.session.get(Challenge, challenge_id)
    if not challenge:
        return jsonify({'error': '题目不存在'}), 404

    data = request.get_json()

    # 更新基本字段
    for field in ['title', 'description', 'category', 'difficulty', 'points', 'is_active']:
        if field in data:
            setattr(challenge, field, data[field])

    # 更新类型特定字段
    if challenge.type == 'choice':
        if 'question' in data:
            challenge.question = data['question']
        if 'options' in data:
            challenge.options = json.dumps(data['options'], ensure_ascii=False)
        if 'correct_answer' in data:
            challenge.correct_answer = data['correct_answer']
    elif challenge.type == 'docker':
        if 'flag' in data:
            challenge.flag = data['flag']
        # 支持 docker_image 字段(前端使用)
        if 'docker_image' in data or 'docker_compose_file' in data:
            challenge.docker_compose_file = data.get('docker_image') or data.get('docker_compose_file')
        # 支持 docker_port 字段(前端使用)
        if 'docker_port' in data or 'container_port' in data:
            challenge.container_port = data.get('docker_port') or data.get('container_port')

    if 'skill_tags' in data:
        challenge.skill_tags = json.dumps(data['skill_tags'], ensure_ascii=False)

    db.session.commit()
    return jsonify({
        'message': '题目更新成功',
        'challenge': challenge.to_dict(show_answer=True)
    }), 200


@bp.route('/challenges/<int:challenge_id>', methods=['DELETE'])

@admin_required
def delete_challenge(challenge_id):
    """删除题目"""
    challenge = db.session.get(Challenge, challenge_id)
    if not challenge:
        return jsonify({'error': '题目不存在'}), 404

    db.session.delete(challenge)
    db.session.commit()
    return jsonify({'message': '题目已删除'}), 200


# ========== 容器管理 ==========

@bp.route('/containers', methods=['GET'])

@admin_required
def get_all_containers():
    """获取所有运行中的容器"""
    containers = docker_manager.get_all_containers()
    return jsonify([c.to_dict() for c in containers]), 200


@bp.route('/containers/<int:instance_id>/stop', methods=['POST'])

@admin_required
def admin_stop_container(instance_id):
    """管理员停止容器"""
    try:
        instance = docker_manager.stop_container(instance_id, is_admin=True)
        return jsonify({
            'message': '容器已停止',
            'container': instance.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/containers/<int:instance_id>/extend', methods=['POST'])
@admin_required
def admin_extend_container(instance_id):
    """管理员延长容器时间"""
    try:
        data = request.get_json()
        minutes = data.get('minutes', 30)
        instance = docker_manager.extend_container(instance_id, minutes)
        return jsonify({
            'message': f'容器时间已延长 {minutes} 分钟',
            'container': instance.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/containers/<int:instance_id>', methods=['DELETE'])
@admin_required
def admin_delete_container(instance_id):
    """删除容器记录"""
    instance = db.session.get(ContainerInstance, instance_id)
    if not instance:
        return jsonify({'error': '容器不存在'}), 404

    # 如果容器还在运行,先停止
    if instance.status == 'running':
        try:
            docker_manager.stop_container(instance_id, is_admin=True)
        except:
            pass

    db.session.delete(instance)
    db.session.commit()
    return jsonify({'message': '容器记录已删除'}), 200


@bp.route('/containers/cleanup', methods=['POST'])

@admin_required
def cleanup_expired():
    """清理过期容器"""
    try:
        docker_manager.cleanup_expired_containers()
        return jsonify({'message': '过期容器清理完成'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ========== 统计信息 ==========

@bp.route('/stats', methods=['GET'])

@admin_required
def get_stats():
    """获取平台统计信息"""
    total_users = User.query.count()
    total_challenges = Challenge.query.filter_by(is_active=True).count()
    total_submissions = Submission.query.count()
    correct_submissions = Submission.query.filter_by(is_correct=True).count()
    running_containers = ContainerInstance.query.filter_by(status='running').count()

    return jsonify({
        'total_users': total_users,
        'total_challenges': total_challenges,
        'total_submissions': total_submissions,
        'correct_submissions': correct_submissions,
        'running_containers': running_containers,
        'success_rate': round(correct_submissions / total_submissions * 100, 2) if total_submissions > 0 else 0
    }), 200


@bp.route('/submissions/recent', methods=['GET'])
@admin_required
def get_recent_submissions():
    """获取最近提交记录"""
    limit = request.args.get('limit', 10, type=int)
    submissions = Submission.query.order_by(Submission.submitted_at.desc()).limit(limit).all()

    result = []
    for sub in submissions:
        user = db.session.get(User, sub.user_id)
        challenge = db.session.get(Challenge, sub.challenge_id)
        result.append({
            'id': sub.id,
            'username': user.username if user else 'Unknown',
            'challenge_title': challenge.title if challenge else 'Unknown',
            'is_correct': sub.is_correct,
            'submitted_at': sub.submitted_at.isoformat()
        })

    return jsonify(result), 200


@bp.route('/users/top', methods=['GET'])
@admin_required
def get_top_users():
    """获取TOP用户"""
    limit = request.args.get('limit', 10, type=int)
    users = User.query.all()
    # 按总分和解题数排序 (Python级别排序,因为是计算属性)
    users_sorted = sorted(users, key=lambda u: (u.total_points, u.solved_count), reverse=True)
    return jsonify([user.to_dict() for user in users_sorted[:limit]]), 200


@bp.route('/challenges/stats', methods=['GET'])
@admin_required
def get_challenge_stats():
    """获取题目分类统计"""
    from sqlalchemy import func

    stats = db.session.query(
        Challenge.category,
        func.count(Challenge.id).label('count'),
        func.avg(Challenge.points).label('avg_points')
    ).filter_by(is_active=True).group_by(Challenge.category).all()

    result = []
    for category, count, avg_points in stats:
        result.append({
            'category': category,
            'count': count,
            'avg_points': float(avg_points) if avg_points else 0
        })

    return jsonify(result), 200
