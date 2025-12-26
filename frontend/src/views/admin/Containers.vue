<template>
  <div class="admin-containers-container">
    <el-container>
      <el-aside width="250px">
        <div class="logo">CyberPrism</div>
        <el-menu :default-active="'admin/containers'" @select="handleMenuSelect">
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
            <div class="card-header">
              <h2>容器管理</h2>
              <el-space>
                <el-button type="primary" @click="loadContainers" :icon="Refresh">刷新</el-button>
                <el-button type="danger" @click="cleanupExpired">清理过期容器</el-button>
              </el-space>
            </div>
          </template>

          <el-table :data="containers" v-loading="loading" border>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="username" label="用户" width="120" />
            <el-table-column prop="challenge_title" label="题目" min-width="150" />
            <el-table-column prop="container_id" label="容器ID" width="150" show-overflow-tooltip />
            <el-table-column prop="host_port" label="端口" width="100" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.status === 'running'" type="success" size="small">运行中</el-tag>
                <el-tag v-else-if="row.status === 'stopped'" type="info" size="small">已停止</el-tag>
                <el-tag v-else-if="row.status === 'expired'" type="warning" size="small">已过期</el-tag>
                <el-tag v-else type="danger" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="剩余时间" width="120">
              <template #default="{ row }">
                <span v-if="row.status === 'running'">{{ getRemainingTime(row) }}</span>
                <span v-else style="color: #909399;">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="160">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button
                  v-if="row.status === 'running'"
                  type="warning"
                  size="small"
                  @click="stopContainer(row.id)"
                >
                  停止
                </el-button>
                <el-button
                  v-if="row.status === 'running'"
                  type="primary"
                  size="small"
                  @click="extendTime(row.id)"
                >
                  延长
                </el-button>
                <el-button
                  v-if="row.status !== 'running'"
                  type="danger"
                  size="small"
                  @click="deleteContainer(row.id)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="statistics" v-if="containers.length > 0">
            <el-divider />
            <el-descriptions :column="4" size="small">
              <el-descriptions-item label="总容器数">{{ containers.length }}</el-descriptions-item>
              <el-descriptions-item label="运行中">
                <el-tag type="success" size="small">{{ runningCount }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="已停止">
                <el-tag type="info" size="small">{{ stoppedCount }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="已过期">
                <el-tag type="warning" size="small">{{ expiredCount }}</el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import {
  getAllContainers,
  stopContainer as stopContainerAPI,
  extendContainer as extendContainerAPI,
  deleteContainer as deleteContainerAPI,
  cleanupExpiredContainers
} from '@/api/admin'

export default {
  name: 'AdminContainers',
  setup() {
    const router = useRouter()
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    const loading = ref(false)
    const containers = ref([])

    const runningCount = computed(() => containers.value.filter(c => c.status === 'running').length)
    const stoppedCount = computed(() => containers.value.filter(c => c.status === 'stopped').length)
    const expiredCount = computed(() => containers.value.filter(c => c.status === 'expired').length)

    const loadContainers = async () => {
      loading.value = true
      try {
        containers.value = await getAllContainers()
      } finally {
        loading.value = false
      }
    }

    const stopContainer = async (id) => {
      try {
        await ElMessageBox.confirm('确定要停止这个容器吗?', '提示', {
          type: 'warning',
          confirmButtonText: '确定',
          cancelButtonText: '取消'
        })

        await stopContainerAPI(id)
        ElMessage.success('容器已停止')
        loadContainers()
      } catch (error) {
        if (error !== 'cancel') {
          console.error(error)
        }
      }
    }

    const extendTime = async (id) => {
      try {
        const { value: minutes } = await ElMessageBox.prompt('请输入延长时间 (分钟)', '延长容器时间', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          inputPattern: /^[1-9]\d*$/,
          inputErrorMessage: '请输入有效的分钟数',
          inputValue: '30'
        })

        await extendContainerAPI(id, parseInt(minutes))
        ElMessage.success(`容器时间已延长 ${minutes} 分钟`)
        loadContainers()
      } catch (error) {
        if (error !== 'cancel') {
          console.error(error)
        }
      }
    }

    const deleteContainer = async (id) => {
      try {
        await ElMessageBox.confirm('确定要删除这个容器记录吗?', '警告', {
          type: 'warning',
          confirmButtonText: '确定',
          cancelButtonText: '取消'
        })

        await deleteContainerAPI(id)
        ElMessage.success('删除成功')
        loadContainers()
      } catch (error) {
        if (error !== 'cancel') {
          console.error(error)
        }
      }
    }

    const cleanupExpired = async () => {
      try {
        await ElMessageBox.confirm('将清理所有已过期和已停止的容器，确定继续吗?', '清理容器', {
          type: 'warning',
          confirmButtonText: '确定',
          cancelButtonText: '取消'
        })

        loading.value = true
        await cleanupExpiredContainers()
        ElMessage.success('清理完成')
        loadContainers()
      } catch (error) {
        if (error !== 'cancel') {
          console.error(error)
        }
        loading.value = false
      }
    }

    const getRemainingTime = (container) => {
      const expiresAt = new Date(container.expires_at)
      const now = new Date()
      const diff = expiresAt - now

      if (diff <= 0) {
        return '已过期'
      }

      const minutes = Math.floor(diff / 60000)
      if (minutes < 60) {
        return `${minutes} 分钟`
      }

      const hours = Math.floor(minutes / 60)
      const remainingMinutes = minutes % 60
      return `${hours} 小时 ${remainingMinutes} 分钟`
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
      loadContainers()
      // 每30秒自动刷新一次
      const interval = setInterval(loadContainers, 30000)
      return () => clearInterval(interval)
    })

    return {
      user,
      loading,
      containers,
      runningCount,
      stoppedCount,
      expiredCount,
      Refresh,
      loadContainers,
      stopContainer,
      extendTime,
      deleteContainer,
      cleanupExpired,
      getRemainingTime,
      formatTime,
      handleMenuSelect,
      handleLogout
    }
  }
}
</script>

<style scoped>
.admin-containers-container {
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
}

.statistics {
  margin-top: 20px;
}
</style>
