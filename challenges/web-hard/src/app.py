from flask import Flask, render_template, request
import os
import subprocess

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ping', methods=['POST'])
def ping():
    """网络诊断工具 - 存在命令注入漏洞"""
    host = request.form.get('host', '')

    if not host:
        return render_template('index.html', error='请输入主机地址')

    # 基本过滤(但不完善)
    blacklist = [';', '&&', '||', '|', '`', '$', '(', ')']
    for char in blacklist:
        if char in host:
            return render_template('index.html', error=f'检测到非法字符: {char}')

    try:
        # 存在命令注入漏洞 - 使用shell=True且过滤不完善
        command = f'ping -c 4 {host}'
        result = subprocess.check_output(
            command,
            shell=True,
            stderr=subprocess.STDOUT,
            timeout=10,
            text=True
        )

        return render_template('index.html', result=result, host=host)

    except subprocess.TimeoutExpired:
        return render_template('index.html', error='命令执行超时')
    except subprocess.CalledProcessError as e:
        return render_template('index.html', error=f'命令执行失败', result=e.output)
    except Exception as e:
        return render_template('index.html', error=f'发生错误: {str(e)}')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
