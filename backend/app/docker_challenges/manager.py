import docker
import random
import os
from datetime import datetime, timedelta
from app.models import db, Challenge, ContainerInstance


class DockerManager:
    """Docker容器管理器"""

    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as e:
            print(f"警告: 无法连接到Docker daemon: {e}")
            self.client = None

    def start_container(self, user_id, challenge_id):
        """启动容器"""
        if not self.client:
            raise Exception("Docker服务未启动")

        challenge = db.session.get(Challenge, challenge_id)
        if not challenge or challenge.type != 'docker':
            raise Exception("无效的靶场题目")

        # 检查用户是否已有该题目的运行中容器
        existing = ContainerInstance.query.filter_by(
            user_id=user_id,
            challenge_id=challenge_id,
            status='running'
        ).first()

        if existing:
            return existing

        # 生成随机端口(30000-40000)
        host_port = random.randint(30000, 40000)

        # 检查端口是否已被使用
        while ContainerInstance.query.filter_by(host_port=host_port, status='running').first():
            host_port = random.randint(30000, 40000)

        # 获取docker-compose文件路径
        compose_file = challenge.docker_compose_file
        if not compose_file or not os.path.exists(compose_file):
            raise Exception("Docker配置文件不存在")

        # 读取docker-compose内容
        import yaml
        with open(compose_file, 'r', encoding='utf-8') as f:
            compose_config = yaml.safe_load(f)

        # 获取第一个服务
        service_name = list(compose_config['services'].keys())[0]
        service_config = compose_config['services'][service_name]

        # 生成容器名称
        container_name = f"cyberprism_{challenge_id}_{user_id}_{random.randint(1000, 9999)}"

        # 注入FLAG环境变量
        env_vars = service_config.get('environment', {})
        if isinstance(env_vars, list):
            env_vars.append(f"FLAG={challenge.flag}")
        else:
            env_vars['FLAG'] = challenge.flag

        # 启动容器
        try:
            container = self.client.containers.run(
                image=service_config['image'],
                name=container_name,
                detach=True,
                environment=env_vars,
                ports={f"{challenge.container_port}/tcp": host_port},
                **{k: v for k, v in service_config.items() if k not in ['image', 'environment', 'ports']}
            )

            # 记录到数据库
            expires_at = datetime.utcnow() + timedelta(minutes=60)
            instance = ContainerInstance(
                user_id=user_id,
                challenge_id=challenge_id,
                container_id=container.id,
                container_name=container_name,
                host_port=host_port,
                status='running',
                expires_at=expires_at
            )

            db.session.add(instance)
            db.session.commit()

            return instance

        except Exception as e:
            raise Exception(f"启动容器失败: {str(e)}")

    def stop_container(self, instance_id, user_id=None, is_admin=False):
        """停止容器"""
        if not self.client:
            raise Exception("Docker服务未启动")

        instance = db.session.get(ContainerInstance, instance_id)
        if not instance:
            raise Exception("容器实例不存在")

        # 权限检查
        if not is_admin and instance.user_id != user_id:
            raise Exception("无权限操作此容器")

        try:
            container = self.client.containers.get(instance.container_id)
            container.stop()
            container.remove()
        except docker.errors.NotFound:
            pass  # 容器已不存在
        except Exception as e:
            print(f"停止容器时出错: {e}")

        instance.status = 'stopped'
        db.session.commit()

        return instance

    def extend_container(self, instance_id, user_id, minutes=30):
        """延长容器时间"""
        instance = db.session.get(ContainerInstance, instance_id)
        if not instance:
            raise Exception("容器实例不存在")

        if instance.user_id != user_id:
            raise Exception("无权限操作此容器")

        if instance.status != 'running':
            raise Exception("容器未运行")

        # 延长时间
        instance.expires_at = instance.expires_at + timedelta(minutes=minutes)
        db.session.commit()

        return instance

    def cleanup_expired_containers(self):
        """清理过期容器"""
        if not self.client:
            return

        expired = ContainerInstance.query.filter(
            ContainerInstance.status == 'running',
            ContainerInstance.expires_at < datetime.utcnow()
        ).all()

        for instance in expired:
            try:
                container = self.client.containers.get(instance.container_id)
                container.stop()
                container.remove()
            except:
                pass

            instance.status = 'expired'

        db.session.commit()

    def get_user_containers(self, user_id):
        """获取用户的所有容器"""
        return ContainerInstance.query.filter_by(user_id=user_id).all()

    def get_all_containers(self):
        """获取所有容器(管理员)"""
        return ContainerInstance.query.filter_by(status='running').all()
