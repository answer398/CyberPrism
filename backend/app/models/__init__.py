from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)  # 姓名
    common_id = db.Column(db.String(100))  # 常用ID
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    submissions = db.relationship('Submission', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    skill_tags = db.relationship('UserSkillTag', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    containers = db.relationship('ContainerInstance', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def total_points(self):
        """计算用户总分"""
        correct_submissions = self.submissions.filter_by(is_correct=True).all()
        return sum(sub.challenge.points for sub in correct_submissions if sub.challenge)

    @property
    def solved_count(self):
        """计算已解题目数"""
        return self.submissions.filter_by(is_correct=True).distinct(Submission.challenge_id).count()

    def to_dict(self, include_skills=False):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'display_name': self.display_name,
            'common_id': self.common_id,
            'is_admin': self.is_admin,
            'total_points': self.total_points,
            'solved_count': self.solved_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_skills:
            data['skill_tags'] = [tag.to_dict() for tag in self.skill_tags]
        return data


class UserSkillTag(db.Model):
    """用户技能标签关联"""
    __tablename__ = 'user_skill_tags'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)  # 技能分类
    skill_name = db.Column(db.String(100), nullable=False)  # 技能名称
    skill_code = db.Column(db.String(50))  # 技能代码(如T1071)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'category': self.category,
            'skill_name': self.skill_name,
            'skill_code': self.skill_code,
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None
        }


class Challenge(db.Model):
    """题目模型(包括选择题和靶场题)"""
    __tablename__ = 'challenges'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)  # 题目分类
    type = db.Column(db.String(20), nullable=False)  # 'choice' 或 'docker'
    difficulty = db.Column(db.String(20))  # easy, medium, hard
    points = db.Column(db.Integer, default=100)

    # 选择题字段
    question = db.Column(db.Text)  # 题目内容
    options = db.Column(db.Text)  # JSON格式的选项 {"A": "...", "B": "..."}
    correct_answer = db.Column(db.String(10))  # 正确答案(如"A")

    # 靶场题字段
    flag = db.Column(db.String(255))  # 静态flag
    docker_compose_file = db.Column(db.String(255))  # docker-compose文件路径
    container_port = db.Column(db.Integer)  # 容器内部端口

    # 关联技能标签(JSON格式)
    skill_tags = db.Column(db.Text)  # JSON: {"category": "skill_name"}

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    submissions = db.relationship('Submission', backref='challenge', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, show_answer=False):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'type': self.type,
            'difficulty': self.difficulty,
            'points': self.points,
            'is_active': self.is_active
        }

        if self.type == 'choice':
            data['question'] = self.question
            data['options'] = json.loads(self.options) if self.options else {}
            if show_answer:
                data['correct_answer'] = self.correct_answer
        elif self.type == 'docker':
            data['container_port'] = self.container_port
            # 同时提供前端期望的字段名
            data['docker_port'] = self.container_port
            data['docker_image'] = self.docker_compose_file
            if show_answer:
                data['flag'] = self.flag
                data['docker_compose_file'] = self.docker_compose_file

        if self.skill_tags:
            data['skill_tags'] = json.loads(self.skill_tags)

        return data


class Submission(db.Model):
    """用户提交记录"""
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    submitted_answer = db.Column(db.Text)  # 提交的答案
    is_correct = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'challenge_id': self.challenge_id,
            'submitted_answer': self.submitted_answer,
            'is_correct': self.is_correct,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }


class ContainerInstance(db.Model):
    """Docker容器实例"""
    __tablename__ = 'container_instances'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    container_id = db.Column(db.String(255))  # Docker容器ID
    container_name = db.Column(db.String(255))  # 容器名称
    host_port = db.Column(db.Integer)  # 映射到宿主机的端口
    status = db.Column(db.String(20), default='running')  # running, stopped, expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # 过期时间(60分钟后)

    challenge = db.relationship('Challenge', backref='instances')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'challenge_id': self.challenge_id,
            'challenge_title': self.challenge.title if self.challenge else None,
            'container_id': self.container_id,
            'container_name': self.container_name,
            'host_port': self.host_port,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
