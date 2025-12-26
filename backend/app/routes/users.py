from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models import db, User, UserSkillTag
from app.utils import get_current_user

bp = Blueprint('users', __name__, url_prefix='/api/users')


@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户个人资料和技能标签"""
    user = get_current_user()

    if not user:
        return jsonify({'error': '用户不存在'}), 404

    # 计算能力矩阵完成度
    from app.models import Submission, Challenge
    import json

    # 获取所有已激活的题目,按类别分组
    all_challenges = Challenge.query.filter_by(is_active=True).all()

    # 统计每个类别的总题目数和用户已完成题目数
    category_stats = {}
    for challenge in all_challenges:
        category = challenge.category
        if category not in category_stats:
            category_stats[category] = {
                'total': 0,
                'completed': 0,
                'skills': {}  # 技能标签及其关联的题目
            }
        category_stats[category]['total'] += 1

        # 解析题目的skill_tags
        if challenge.skill_tags:
            skill_tags = json.loads(challenge.skill_tags)
            for skill_category, skill_name in skill_tags.items():
                if skill_category not in category_stats[category]['skills']:
                    category_stats[category]['skills'][skill_category] = {
                        'name': skill_name,
                        'total': 0,
                        'completed': 0
                    }
                category_stats[category]['skills'][skill_category]['total'] += 1

    # 统计用户已完成的题目
    correct_submissions = Submission.query.filter_by(
        user_id=user.id,
        is_correct=True
    ).all()

    completed_challenge_ids = set()
    for sub in correct_submissions:
        if sub.challenge_id not in completed_challenge_ids:
            completed_challenge_ids.add(sub.challenge_id)
            challenge = sub.challenge
            if challenge and challenge.is_active:
                category = challenge.category
                if category in category_stats:
                    category_stats[category]['completed'] += 1

                    # 统计技能标签完成度
                    if challenge.skill_tags:
                        skill_tags = json.loads(challenge.skill_tags)
                        for skill_category, skill_name in skill_tags.items():
                            if skill_category in category_stats[category]['skills']:
                                category_stats[category]['skills'][skill_category]['completed'] += 1

    # 计算完成度百分比并构建能力矩阵
    skills_matrix = {}
    for category, stats in category_stats.items():
        completion_rate = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0

        # 计算该类别下所有技能的完成度
        skills_list = []
        for skill_code, skill_data in stats['skills'].items():
            skill_completion = (skill_data['completed'] / skill_data['total'] * 100) if skill_data['total'] > 0 else 0
            skills_list.append({
                'skill_name': skill_data['name'],
                'skill_code': skill_code,
                'completion_rate': round(skill_completion, 1),
                'completed': skill_data['completed'],
                'total': skill_data['total'],
                'mastered': skill_completion >= 60  # 60%视为掌握
            })

        if skills_list:  # 只添加有技能标签的类别
            skills_matrix[category] = {
                'completion_rate': round(completion_rate, 1),
                'completed': stats['completed'],
                'total': stats['total'],
                'skills': skills_list
            }

    # 统计解题数量
    total_submissions = Submission.query.filter_by(user_id=user.id).count()
    correct_submissions_count = Submission.query.filter_by(user_id=user.id, is_correct=True).count()

    # 统计已掌握的技能数(完成度>=60%)
    mastered_skills = sum(
        1 for cat_data in skills_matrix.values()
        for skill in cat_data['skills']
        if skill['mastered']
    )

    return jsonify({
        'user': user.to_dict(),
        'skills_matrix': skills_matrix,
        'stats': {
            'total_submissions': total_submissions,
            'correct_submissions': correct_submissions_count,
            'skills_unlocked': mastered_skills
        }
    }), 200


@bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """获取排行榜"""
    from app.models import Submission
    from sqlalchemy import func

    # 统计每个用户的正确提交数和得分
    leaderboard = db.session.query(
        User.id,
        User.username,
        User.display_name,
        func.count(Submission.id).label('solved_count'),
        func.sum(db.case((Submission.is_correct == True, 100), else_=0)).label('total_points')
    ).join(
        Submission, User.id == Submission.user_id
    ).filter(
        Submission.is_correct == True
    ).group_by(
        User.id
    ).order_by(
        func.sum(db.case((Submission.is_correct == True, 100), else_=0)).desc()
    ).limit(50).all()

    return jsonify([{
        'user_id': item.id,
        'username': item.username,
        'display_name': item.display_name,
        'solved_count': item.solved_count,
        'total_points': item.total_points or 0
    } for item in leaderboard]), 200
