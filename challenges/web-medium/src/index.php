<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>简易博客系统 - LFI挑战</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
        }
        nav {
            background: white;
            padding: 15px 30px;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        nav a {
            color: #667eea;
            text-decoration: none;
            margin-right: 20px;
            font-weight: 500;
        }
        nav a:hover {
            text-decoration: underline;
        }
        .content {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            min-height: 400px;
        }
        .hint-box {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin-top: 20px;
            border-radius: 5px;
        }
        .hint-box strong {
            color: #856404;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📝 简易博客系统</h1>
            <p style="color: #666;">欢迎来到我的博客,探索并找到隐藏的秘密!</p>
        </header>

        <nav>
            <a href="?page=home">首页</a>
            <a href="?page=about">关于</a>
            <a href="?page=contact">联系我</a>
        </nav>

        <div class="content">
            <?php
            $page = isset($_GET['page']) ? $_GET['page'] : 'home';

            // 存在文件包含漏洞 - 没有足够的过滤
            $file = 'pages/' . $page . '.php';

            if (file_exists($file)) {
                include($file);
            } else {
                echo '<h2>页面不存在</h2>';
                echo '<p>请求的页面: ' . htmlspecialchars($page) . '</p>';
            }
            ?>

            <div class="hint-box">
                <strong>挑战提示:</strong> 这个应用存在本地文件包含(LFI)漏洞。<br>
                目标: 读取系统中的敏感文件,找到FLAG。<br>
                <small>提示: FLAG位于系统的某个特殊位置...</small><br>
                <small>技能标签: 网络扫描 / 利用公共漏洞</small>
            </div>
        </div>
    </div>
</body>
</html>
