<?php
// 简单的SQLite数据库连接(存在SQL注入漏洞)

// 创建SQLite数据库
$db = new SQLite3('/tmp/users.db');

// 初始化数据库
$db->exec('CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0
)');

// 插入默认用户
$db->exec("INSERT OR IGNORE INTO users (id, username, password, is_admin) VALUES
    (1, 'admin', 'super_secret_password_12345', 1),
    (2, 'guest', 'guest123', 0)
");

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'];
    $password = $_POST['password'];

    // 存在SQL注入漏洞的查询
    $query = "SELECT * FROM users WHERE username='$username' AND password='$password'";

    try {
        $result = $db->query($query);
        $user = $result->fetchArray(SQLITE3_ASSOC);

        if ($user) {
            if ($user['is_admin'] == 1) {
                // 登录成功,跳转到管理员页面
                header('Location: admin.php');
                exit();
            } else {
                echo '<div class="login-box" style="max-width: 500px; margin: 100px auto; padding: 30px; background: white; border-radius: 10px;">';
                echo '<p class="error" style="color: red;">登录成功,但您不是管理员。</p>';
                echo '<a href="index.php">返回</a>';
                echo '</div>';
            }
        } else {
            echo '<div class="login-box" style="max-width: 500px; margin: 100px auto; padding: 30px; background: white; border-radius: 10px;">';
            echo '<p class="error" style="color: red;">用户名或密码错误!</p>';
            echo '<p style="font-size: 12px; color: #666;">执行的SQL: ' . htmlspecialchars($query) . '</p>';
            echo '<a href="index.php">返回</a>';
            echo '</div>';
        }
    } catch (Exception $e) {
        echo '<div class="login-box" style="max-width: 500px; margin: 100px auto; padding: 30px; background: white; border-radius: 10px;">';
        echo '<p class="error" style="color: red;">查询错误: ' . $e->getMessage() . '</p>';
        echo '<a href="index.php">返回</a>';
        echo '</div>';
    }
} else {
    header('Location: index.php');
}
?>
