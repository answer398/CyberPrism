from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///cyberprism.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 24小时
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

# 初始化扩展
CORS(app)

# 导入models并初始化db
from app.models import db
db.init_app(app)

migrate = Migrate(app, db)
jwt = JWTManager(app)

# 注册蓝图
from app.routes import auth, challenges, containers, admin, users
app.register_blueprint(auth.bp)
app.register_blueprint(challenges.bp)
app.register_blueprint(containers.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(users.bp)


@app.route('/')
def index():
    return {'message': 'CyberPrism API', 'version': '1.0'}


@app.route('/health')
def health():
    return {'status': 'healthy'}


def init_db():
    """初始化数据库"""
    with app.app_context():
        db.create_all()

        # 创建默认管理员账户
        from app.models import User
        from app.utils import hash_password

        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@cyberprism.com',
                password_hash=hash_password('admin123'),
                display_name='Administrator',
                common_id='admin',
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print('✓ 默认管理员账户已创建 (admin/admin123)')