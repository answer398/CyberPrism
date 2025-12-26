<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>登录成功</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 100px auto;
            padding: 20px;
            background: #f0f0f0;
            text-align: center;
        }
        .success-box {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #28a745;
        }
        .flag {
            margin: 30px 0;
            padding: 20px;
            background: #d4edda;
            border: 2px dashed #28a745;
            border-radius: 5px;
            font-size: 20px;
            font-family: monospace;
            word-break: break-all;
        }
        .congrats {
            color: #666;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="success-box">
        <h1>✓ 登录成功!</h1>
        <p>欢迎,管理员!</p>

        <div class="flag">
            FLAG: <?php echo getenv('FLAG') ?: 'FLAG{sql_injection_is_easy}'; ?>
        </div>

        <p class="congrats">
            恭喜你成功利用SQL注入漏洞绕过了登录验证!<br>
            请将上述FLAG提交到平台。
        </p>
    </div>
</body>
</html>
