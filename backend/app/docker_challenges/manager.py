import docker
import random
import os
import platform
from datetime import datetime, timedelta
from app.models import db, Challenge, ContainerInstance


def get_docker_client():
    """获取Docker客户端，兼容Windows和Linux"""
    try:
        # 先尝试使用环境变量
        client = docker.from_env()
        # 测试连接
        client.ping()
        return client
    except Exception as e:
        print(f"使用from_env()失败: {e}")

        # Windows环境下尝试使用命名管道
        if platform.system() == 'Windows':
            try:
                client = docker.DockerClient(base_url='npipe:////./pipe/docker_engine')
                client.ping()
                print("使用Windows命名管道连接成功")
                return client
            except Exception as e2:
                print(f"使用命名管道失败: {e2}")

        # Linux环境下尝试Unix socket（注意是三个斜杠）
        try:
            client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
            client.ping()
            print("使用Unix socket连接成功")
            return client
        except Exception as e3:
            print(f"使用Unix socket失败: {e3}")

        print("所有Docker连接方式均失败")
        return None


class DockerManager:
    """Docker容器管理器"""

    def __init__(self):
        self.client = get_docker_client()
        if not self.client:
            print("警告: 无法连接到Docker daemon，请确保Docker Desktop正在运行")

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

        # 检查用户运行中的容器数量限制(最多3个)
        user_running_containers = ContainerInstance.query.filter_by(
            user_id=user_id,
            status='running'
        ).count()

        if user_running_containers >= 3:
            raise Exception("您已达到同时运行容器的上限(3个)，请先停止其他容器")

        # 生成随机端口(30000-40000)
        host_port = random.randint(30000, 40000)

        # 检查端口是否已被使用
        while ContainerInstance.query.filter_by(host_port=host_port, status='running').first():
            host_port = random.randint(30000, 40000)

        # 判断docker_compose_file是镜像名还是文件路径
        docker_config = challenge.docker_compose_file

        # 如果包含冒号且不是Windows路径(如C:)，可能是镜像名
        if ':' in docker_config and not (len(docker_config) > 1 and docker_config[1] == ':'):
            # 这是镜像名 (如 cyberprism/web-easy:latest)
            image_name = docker_config
            env_vars = {'FLAG': challenge.flag}

            print(f"使用镜像名称: {image_name}")

        elif os.path.exists(docker_config):
            # 这是docker-compose文件路径
            print(f"使用docker-compose文件: {docker_config}")

            # 读取docker-compose内容
            import yaml
            with open(docker_config, 'r', encoding='utf-8') as f:
                compose_config = yaml.safe_load(f)

            # 获取第一个服务
            service_name = list(compose_config['services'].keys())[0]
            service_config = compose_config['services'][service_name]

            # 确定要使用的镜像
            image_name = service_config.get('image')

            # 如果没有指定image，从build.tags中获取
            if not image_name and 'build' in service_config:
                build_config = service_config['build']
                if isinstance(build_config, dict) and 'tags' in build_config:
                    image_name = build_config['tags'][0]  # 使用第一个tag

            if not image_name:
                raise Exception("无法确定镜像名称，请检查docker-compose.yml配置中的image或build.tags字段")

            # 注入FLAG环境变量
            env_vars = service_config.get('environment', {})
            if isinstance(env_vars, list):
                env_vars.append(f"FLAG={challenge.flag}")
            else:
                if not env_vars:
                    env_vars = {}
                env_vars['FLAG'] = challenge.flag
        else:
            raise Exception(f"无效的Docker配置: {docker_config}")

        # 检查镜像是否存在
        try:
            self.client.images.get(image_name)
            print(f"找到镜像: {image_name}")
        except docker.errors.ImageNotFound:
            raise Exception(f"镜像 {image_name} 不存在，请先使用 docker-compose build 构建镜像")

        # 生成容器名称
        container_name = f"cyberprism_{challenge_id}_{user_id}_{random.randint(1000, 9999)}"

        # 启动容器
        try:
            container = self.client.containers.run(
                image=image_name,
                name=container_name,
                detach=True,
                environment=env_vars,
                ports={f"{challenge.container_port}/tcp": host_port}
            )

            print(f"容器启动成功: {container_name} -> localhost:{host_port}")

            # 等待容器启动并检查状态
            import time
            time.sleep(2)  # 等待2秒让容器完全启动

            container.reload()  # 刷新容器状态
            if container.status != 'running':
                # 容器已停止,获取日志
                logs = container.logs(tail=50).decode('utf-8', errors='ignore')
                container.remove()
                raise Exception(f"容器启动后立即停止。日志:\n{logs}")

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

        # 直接删除数据库记录,而不是标记为stopped
        db.session.delete(instance)
        db.session.commit()

        return True

    def extend_container(self, instance_id, user_id=None, minutes=30, is_admin=False):
        """延长容器时间"""
        instance = db.session.get(ContainerInstance, instance_id)
        if not instance:
            raise Exception("容器实例不存在")

        # 权限检查
        if not is_admin and instance.user_id != user_id:
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

            # 直接删除记录
            db.session.delete(instance)

        db.session.commit()

    def get_user_containers(self, user_id):
        """获取用户的运行中容器(按创建时间降序)"""
        return ContainerInstance.query.filter_by(
            user_id=user_id,
            status='running'
        ).order_by(ContainerInstance.created_at.desc()).all()

    def get_all_containers(self):
        """获取所有容器(管理员)"""
        return ContainerInstance.query.filter_by(status='running').all()
