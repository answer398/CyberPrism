<template>
  <div class="admin-dashboard-container">
    <el-container>
      <el-aside width="250px">
        <div class="logo">CyberPrism</div>
        <el-menu :default-active="'admin/dashboard'" @select="handleMenuSelect">
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
          <el-sub-menu v-if="user.is_admin" index="admin">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>管理后台</span>
            </template>
            <el-menu-item index="admin/dashboard">
              <el-icon><DataAnalysis /></el-icon>
              <span>控制台</span>
            </el-menu-item>
            <el-menu-item index="admin/users">
              <el-icon><User /></el-icon>
              <span>用户管理</span>
            </el-menu-item>
            <el-menu-item index="admin/challenges">
              <el-icon><Document /></el-icon>
              <span>题目管理</span>
            </el-menu-item>
            <el-menu-item index="admin/submissions">
              <el-icon><List /></el-icon>
              <span>提交记录</span>
            </el-menu-item>
            <el-menu-item index="admin/containers">
              <el-icon><Box /></el-icon>
              <span>容器管理</span>
            </el-menu-item>
          </el-sub-menu>
          <el-menu-item @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            <span>退出登录</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-main>
        <el-card>
          <template #header>
            <h2>管理后台</h2>
          </template>

          <el-row :gutter="20">
      <!-- 统计卡片 -->
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="总用户数" :value="stats.total_users">
            <template #prefix>
              <el-icon style="color: #409EFF"><User /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="总题目数" :value="stats.total_challenges">
            <template #prefix>
              <el-icon style="color: #67C23A"><Document /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="总提交数" :value="stats.total_submissions">
            <template #prefix>
              <el-icon style="color: #E6A23C"><Edit /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="运行容器数" :value="stats.running_containers">
            <template #prefix>
              <el-icon style="color: #F56C6C"><Box /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 最近提交 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <h3>最近提交</h3>
              <el-button link @click="loadRecentSubmissions">刷新</el-button>
            </div>
          </template>
          <el-table
            :data="recentSubmissions"
            v-loading="submissionsLoading"
            max-height="400"
            size="small"
          >
            <el-table-column prop="username" label="用户" width="100" />
            <el-table-column prop="challenge_title" label="题目" min-width="150" show-overflow-tooltip />
            <el-table-column prop="is_correct" label="结果" width="80">
              <template #default="{ row }">
                <el-tag v-if="row.is_correct" type="success" size="small">正确</el-tag>
                <el-tag v-else type="danger" size="small">错误</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="submitted_at" label="时间" width="160">
              <template #default="{ row }">
                {{ formatTime(row.submitted_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 活跃用户 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <h3>活跃用户 TOP 10</h3>
              <el-button link @click="loadTopUsers">刷新</el-button>
            </div>
          </template>
          <el-table
            :data="topUsers"
            v-loading="usersLoading"
            max-height="400"
            size="small"
          >
            <el-table-column type="index" label="排名" width="80" :index="index => index + 1" />
            <el-table-column prop="display_name" label="用户" width="120" />
            <el-table-column prop="username" label="用户名" width="100" />
            <el-table-column prop="solved_count" label="解题数" width="80" />
            <el-table-column prop="total_points" label="总分" width="80" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 题目统计 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <h3>题目分类统计</h3>
          </template>
          <el-table
            :data="challengeStats"
            v-loading="statsLoading"
            size="small"
          >
            <el-table-column prop="category" label="分类" min-width="120" />
            <el-table-column prop="count" label="题目数" width="100" />
            <el-table-column prop="avg_points" label="平均分值" width="100">
              <template #default="{ row }">
                {{ row.avg_points?.toFixed(1) || 0 }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 系统信息 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <h3>系统信息</h3>
          </template>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="平台名称">CyberPrism</el-descriptions-item>
            <el-descriptions-item label="版本号">v1.0</el-descriptions-item>
            <el-descriptions-item label="后端状态">
              <el-tag type="success" size="small">运行中</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="数据库">SQLite</el-descriptions-item>
            <el-descriptions-item label="容器引擎">Docker</el-descriptions-item>
            <el-descriptions-item label="管理员账户">{{ adminInfo.username }}</el-descriptions-item>
            <el-descriptions-item label="管理员邮箱">{{ adminInfo.email }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getStats, getRecentSubmissions, getTopUsers, getChallengeStats } from '@/api/admin'

export default {
  name: 'AdminDashboard',
  setup() {
    const router = useRouter()
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    const statsLoading = ref(false)
    const submissionsLoading = ref(false)
    const usersLoading = ref(false)

    const stats = ref({
      total_users: 0,
      total_challenges: 0,
      total_submissions: 0,
      running_containers: 0
    })

    const recentSubmissions = ref([])
    const topUsers = ref([])
    const challengeStats = ref([])
    const adminInfo = JSON.parse(localStorage.getItem('user') || '{}')

    const loadStats = async () => {
      statsLoading.value = true
      try {
        const data = await getStats()
        stats.value = data
      } finally {
        statsLoading.value = false
      }
    }

    const loadRecentSubmissions = async () => {
      submissionsLoading.value = true
      try {
        recentSubmissions.value = await getRecentSubmissions(10)
      } finally {
        submissionsLoading.value = false
      }
    }

    const loadTopUsers = async () => {
      usersLoading.value = true
      try {
        topUsers.value = await getTopUsers(10)
      } finally {
        usersLoading.value = false
      }
    }

    const loadChallengeStats = async () => {
      statsLoading.value = true
      try {
        challengeStats.value = await getChallengeStats()
      } finally {
        statsLoading.value = false
      }
    }

    const formatTime = (timeStr) => {
      if (!timeStr) return '-'
      return new Date(timeStr).toLocaleString('zh-CN')
    }

    const handleMenuSelect = (index) => {
      if (index.startsWith('admin/')) {
        router.push(`/${index}`)
      } else if (index === 'admin') {
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

    onMounted(() => {
      loadStats()
      loadRecentSubmissions()
      loadTopUsers()
      loadChallengeStats()

      // 每30秒刷新一次统计数据
      const interval = setInterval(() => {
        loadStats()
        loadRecentSubmissions()
      }, 30000)

      return () => clearInterval(interval)
    })

    return {
      stats,
      statsLoading,
      submissionsLoading,
      usersLoading,
      recentSubmissions,
      topUsers,
      challengeStats,
      adminInfo,
      user,
      loadRecentSubmissions,
      loadTopUsers,
      formatTime,
      handleMenuSelect,
      handleLogout
    }
  }
}
</script>

<style scoped>
.admin-dashboard-container {
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

:deep(.el-sub-menu__title) {
  color: rgba(255,255,255,0.65);
}

:deep(.el-sub-menu__title:hover) {
  color: #fff;
  background: rgba(255,255,255,0.1) !important;
}

:deep(.el-sub-menu.is-active .el-sub-menu__title) {
  color: #fff;
}

:deep(.el-sub-menu .el-menu-item) {
  background: #000c17 !important;
  min-width: 200px;
}

:deep(.el-sub-menu .el-menu-item span) {
  color: rgba(255,255,255,0.65) !important;
}

:deep(.el-sub-menu .el-menu-item .el-icon) {
  color: rgba(255,255,255,0.65) !important;
}

:deep(.el-sub-menu .el-menu-item:hover) {
  background: #001529 !important;
}

:deep(.el-sub-menu .el-menu-item:hover span) {
  color: #fff !important;
}

:deep(.el-sub-menu .el-menu-item:hover .el-icon) {
  color: #fff !important;
}

:deep(.el-sub-menu .el-menu-item.is-active) {
  background: #1890ff !important;
}

:deep(.el-sub-menu .el-menu-item.is-active span) {
  color: #fff !important;
}

:deep(.el-sub-menu .el-menu-item.is-active .el-icon) {
  color: #fff !important;
}

.el-main {
  padding: 20px;
}

.stat-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
}

:deep(.el-statistic__head) {
  font-size: 14px;
  color: #606266;
}

:deep(.el-statistic__number) {
  font-size: 28px;
  font-weight: bold;
}
</style>
