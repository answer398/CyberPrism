from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import db, Challenge, Submission, UserSkillTag
from app.utils import get_current_user
import json

bp = Blueprint('challenges', __name__, url_prefix='/api/challenges')


@bp.route('/', methods=['GET'])
@jwt_required()
def get_challenges():
    """获取题目列表"""
    challenge_type = request.args.get('type')  # 'choice' 或 'docker'
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')

    query = Challenge.query.filter_by(is_active=True)

    if challenge_type:
        query = query.filter_by(type=challenge_type)
    if category:
        query = query.filter_by(category=category)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)

    challenges = query.all()

    # 获取当前用户的解题状态
    user = get_current_user()
    solved_challenge_ids = set()
    if user:
        solved_submissions = Submission.query.filter_by(
            user_id=user.id,
            is_correct=True
        ).all()
        solved_challenge_ids = {sub.challenge_id for sub in solved_submissions}

    result = []
    for challenge in challenges:
        challenge_data = challenge.to_dict(show_answer=False)
        challenge_data['solved'] = challenge.id in solved_challenge_ids
        result.append(challenge_data)

    return jsonify(result), 200


@bp.route('/<int:challenge_id>', methods=['GET'])
@jwt_required()
def get_challenge(challenge_id):
    """获取单个题目详情"""
    challenge = db.session.get(Challenge, challenge_id)

    if not challenge or not challenge.is_active:
        return jsonify({'error': '题目不存在'}), 404

    # 检查用户是否已解题
    user = get_current_user()
    solved = False
    if user:
        submission = Submission.query.filter_by(
            user_id=user.id,
            challenge_id=challenge_id,
            is_correct=True
        ).first()
        solved = submission is not None

    challenge_data = challenge.to_dict(show_answer=False)
    challenge_data['solved'] = solved

    return jsonify(challenge_data), 200


@bp.route('/<int:challenge_id>/submit', methods=['POST'])
@jwt_required()
def submit_answer(challenge_id):
    """提交答案"""
    user = get_current_user()
    challenge = db.session.get(Challenge, challenge_id)

    if not challenge or not challenge.is_active:
        return jsonify({'error': '题目不存在'}), 404

    data = request.get_json()
    submitted_answer = data.get('answer', '').strip()

    if not submitted_answer:
        return jsonify({'error': '答案不能为空'}), 400

    # 检查是否已经正确解答过
    existing_correct = Submission.query.filter_by(
        user_id=user.id,
        challenge_id=challenge_id,
        is_correct=True
    ).first()

    if existing_correct:
        return jsonify({'error': '您已经正确解答过此题'}), 400

    # 验证答案
    is_correct = False
    if challenge.type == 'choice':
        is_correct = submitted_answer.upper() == challenge.correct_answer.upper()
    elif challenge.type == 'docker':
        is_correct = submitted_answer == challenge.flag

    # 记录提交
    submission = Submission(
        user_id=user.id,
        challenge_id=challenge_id,
        submitted_answer=submitted_answer,
        is_correct=is_correct
    )
    db.session.add(submission)

    # 如果答案正确,解锁技能标签
    if is_correct and challenge.skill_tags:
        skill_tags_data = json.loads(challenge.skill_tags)
        for category, skill_name in skill_tags_data.items():
            # 检查是否已有该技能标签
            existing_tag = UserSkillTag.query.filter_by(
                user_id=user.id,
                category=category,
                skill_name=skill_name
            ).first()

            if not existing_tag:
                # 从预定义的技能标签JSON中获取技能代码
                SKILL_CODES = {
                    "信息收集与侦察": {
                        "信息收集": "T1071",
                        "网络扫描": "T1046",
                        "子域枚举": "T1071",
                        "网络拓扑分析": "T1027"
                    },
                    "漏洞利用与攻击": {
                        "利用公共漏洞": "T1203",
                        "提权与横向移动": "T1075",
                        "社会工程学攻击": "T1071",
                        "恶意软件": "T1053"
                    },
                    "后渗透": {
                        "横向移动": "T1021",
                        "后门植入": "T1012",
                        "权限提升": "T1088"
                    },
                    "防御规避与反侦察": {
                        "权限提升": "T1088",
                        "文件/日志清理": "T1070",
                        "命令与控制": "T1071"
                    }
                }

                skill_code = SKILL_CODES.get(category, {}).get(skill_name, '')

                new_tag = UserSkillTag(
                    user_id=user.id,
                    category=category,
                    skill_name=skill_name,
                    skill_code=skill_code
                )
                db.session.add(new_tag)

    db.session.commit()

    # 如果是靶场题且答案正确,自动销毁用户的容器
    if is_correct and challenge.type == 'docker':
        from app.docker_challenges import DockerManager
        from app.models import ContainerInstance

        docker_manager = DockerManager()

        # 查找用户在此题目上运行的容器
        running_container = ContainerInstance.query.filter_by(
            user_id=user.id,
            challenge_id=challenge_id,
            status='running'
        ).first()

        if running_container:
            try:
                docker_manager.stop_container(running_container.id, user_id=user.id, is_admin=False)
                print(f"自动销毁容器: {running_container.container_name} (用户: {user.username}, 题目: {challenge.title})")
            except Exception as e:
                print(f"自动销毁容器失败: {str(e)}")
                # 不影响提交结果,继续返回成功

    return jsonify({
        'is_correct': is_correct,
        'message': '恭喜!答案正确!' if is_correct else '答案错误,请重试',
        'points': challenge.points if is_correct else 0
    }), 200


@bp.route('/categories', methods=['GET'])
def get_categories():
    """获取所有题目分类"""
    categories = db.session.query(Challenge.category).filter_by(is_active=True).distinct().all()
    return jsonify([cat[0] for cat in categories]), 200
