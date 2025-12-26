<template>
  <div class="dashboard-container">
    <el-container>
      <el-aside width="250px">
        <div class="logo">CyberPrism</div>
        <el-menu :default-active="'dashboard'" @select="handleMenuSelect">
          <el-menu-item index="dashboard">
            <el-icon><HomeFilled /></el-icon>
            <span>个人中心</span>
          </el-menu-item>
          <el-menu-item index="challenges">
            <el-icon><Document /></el-icon>
            <span>题目挑战</span>
          </el-menu-item>
          <el-menu-item index="profile">
            <el-icon><UserFilled /></el-icon>
            <span>个人资料</span>
          </el-menu-item>
          <el-menu-item index="containers">
            <el-icon><Box /></el-icon>
            <span>我的容器</span>
          </el-menu-item>
          <el-menu-item index="leaderboard">
            <el-icon><TrendCharts /></el-icon>
            <span>排行榜</span>
          </el-menu-item>
          <el-menu-item v-if="user.is_admin" index="admin">
            <el-icon><Setting /></el-icon>
            <span>管理后台</span>
          </el-menu-item>
          <el-menu-item @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            <span>退出登录</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-main>
        <el-card>
          <template #header>
            <h2>欢迎回来, {{ user.display_name }}</h2>
          </template>

          <el-row :gutter="20">
            <el-col :span="6">
              <el-card shadow="hover">
                <el-statistic title="解题数" :value="0" />
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover">
                <el-statistic title="技能解锁" :value="0" />
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover">
                <el-statistic title="当前排名" :value="0" />
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover">
                <el-statistic title="运行容器" :value="0" />
              </el-card>
            </el-col>
          </el-row>

          <el-card style="margin-top: 20px">
            <template #header><h3>快速开始</h3></template>
            <el-space>
              <el-button type="primary" @click="$router.push('/challenges')">开始挑战</el-button>
              <el-button @click="$router.push('/profile')">查看能力矩阵</el-button>
            </el-space>
          </el-card>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

export default {
  name: 'Dashboard',
  setup() {
    const router = useRouter()
    const user = JSON.parse(localStorage.getItem('user') || '{}')

    const handleMenuSelect = (index) => {
      if (index === 'admin') {
        router.push('/admin')
      } else {
        router.push(`/${index}`)
      }
    }

    const handleLogout = () => {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      ElMessage.success('已退出登录')
      router.push('/login')
    }

    return {
      user,
      handleMenuSelect,
      handleLogout
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background: #f0f2f5;
}

.el-aside {
  background: #001529;
  min-height: 100vh;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 20px;
  font-weight: bold;
  background: rgba(255,255,255,0.1);
}

.el-menu {
  border: none;
  background: #001529;
}

:deep(.el-menu-item) {
  color: rgba(255,255,255,0.65);
}

:deep(.el-menu-item:hover) {
  color: #fff;
  background: rgba(255,255,255,0.1) !important;
}

:deep(.el-menu-item.is-active) {
  color: #fff;
  background: #1890ff !important;
}

.el-main {
  padding: 20px;
}
</style>
