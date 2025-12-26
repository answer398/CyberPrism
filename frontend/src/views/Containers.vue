<template>
  <div class="containers-container">
    <el-container>
      <el-aside width="250px">
        <div class="logo">CyberPrism</div>
        <el-menu :default-active="'containers'" @select="handleMenuSelect">
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
            <h2>我的容器</h2>
          </template>

          <div v-loading="loading">
            <el-empty v-if="containers.length === 0" description="暂无运行中的容器" />

            <el-table v-else :data="containers" border>
              <el-table-column prop="id" label="ID" width="60" />
              <el-table-column prop="challenge_title" label="题目" width="200" />
              <el-table-column prop="container_name" label="容器名称" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{row}">
                  <el-tag v-if="row.status === 'running'" type="success">运行中</el-tag>
                  <el-tag v-else-if="row.status === 'stopped'" type="info">已停止</el-tag>
                  <el-tag v-else type="warning">{{ row.status }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="host_port" label="访问端口" width="100">
                <template #default="{row}">
                  <el-link :href="`http://${getHostname()}:${row.host_port}`" target="_blank" type="primary">
                    {{ row.host_port }}
                  </el-link>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="创建时间" width="180">
                <template #default="{row}">
                  {{ formatTime(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column prop="expires_at" label="过期时间" width="180">
                <template #default="{row}">
                  <span :class="{'expired-soon': isExpiringSoon(row.expires_at)}">
                    {{ formatTime(row.expires_at) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200" fixed="right">
                <template #default="{row}">
                  <el-button size="small" @click="extendTime(row.id)" :disabled="row.status !== 'running'">
                    延时
                  </el-button>
                  <el-popconfirm
                    title="确定停止此容器吗?"
                    @confirm="stopContainer(row.id)"
                  >
                    <template #reference>
                      <el-button size="small" type="danger" :disabled="row.status !== 'running'">
                        停止
                      </el-button>
                    </template>
                  </el-popconfirm>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMyContainers, stopContainer as stopContainerAPI, extendContainer } from '@/api/container'

export default {
  name: 'Containers',
  setup() {
    const router = useRouter()
    const user = JSON.parse(localStorage.getItem('user') || '{}')

    const loading = ref(false)
    const containers = ref([])

    const loadContainers = async () => {
      loading.value = true
      try {
        containers.value = await getMyContainers()
      } catch (error) {
        console.error(error)
      } finally {
        loading.value = false
      }
    }

    const stopContainer = async (id) => {
      try {
        await stopContainerAPI(id)
        ElMessage.success('容器已停止')
        loadContainers()
      } catch (error) {
        console.error(error)
      }
    }

    const extendTime = async (id) => {
      try {
        const { value: minutes } = await ElMessageBox.prompt('请输入延长时间(分钟)', '延长容器时间', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          inputPattern: /^\d+$/,
          inputErrorMessage: '请输入有效的分钟数',
          inputValue: '30'
        })

        const time = parseInt(minutes)
        if (time < 10 || time > 60) {
          ElMessage.warning('延长时间必须在10-60分钟之间')
          return
        }

        await extendContainer(id, time)
        ElMessage.success(`已延长${time}分钟`)
        loadContainers()
      } catch (error) {
        if (error !== 'cancel') {
          console.error(error)
        }
      }
    }

    const formatTime = (timeStr) => {
      if (!timeStr) return '-'
      return new Date(timeStr).toLocaleString('zh-CN')
    }

    const isExpiringSoon = (expiresAt) => {
      if (!expiresAt) return false
      const diff = new Date(expiresAt) - new Date()
      return diff > 0 && diff < 10 * 60 * 1000 // 10分钟内过期
    }

    const getHostname = () => {
      return window.location.hostname
    }

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

    onMounted(() => {
      loadContainers()
    })

    return {
      user,
      loading,
      containers,
      stopContainer,
      extendTime,
      formatTime,
      isExpiringSoon,
      getHostname,
      handleMenuSelect,
      handleLogout
    }
  }
}
</script>

<style scoped>
.containers-container {
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

.expired-soon {
  color: #f56c6c;
  font-weight: bold;
}
</style>
