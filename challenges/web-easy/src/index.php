<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>简单登录系统 - SQL注入挑战</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 500px;
            margin: 100px auto;
            padding: 20px;
            background: #f0f0f0;
        }
        .login-box {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #333;
        }
        input {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 10px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background: #0056b3;
        }
        .hint {
            margin-top: 20px;
            padding: 10px;
            background: #fff3cd;
            border-radius: 5px;
            font-size: 14px;
        }
        .error {
            color: red;
            margin-top: 10px;
        }
        .success {
            color: green;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>登录系统</h1>
        <form method="POST" action="login.php">
            <input type="text" name="username" placeholder="用户名" required>
            <input type="password" name="password" placeholder="密码" required>
            <button type="submit">登录</button>
        </form>

        <div class="hint">
            <strong>提示:</strong> 这是一个存在SQL注入漏洞的登录系统。<br>
            目标: 绕过登录验证,获取管理员权限,找到FLAG。<br>
            <small>技能标签: 信息收集 / 利用公共漏洞</small>
        </div>
    </div>
</body>
</html>
