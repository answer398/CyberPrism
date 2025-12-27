<template>
  <div class="leaderboard-container">
    <el-container>
      <el-aside width="250px">
        <div class="logo">CyberPrism</div>
        <el-menu :default-active="'leaderboard'" @select="handleMenuSelect">
          <el-menu-item index="challenges"><el-icon><Document /></el-icon><span>题目挑战</span></el-menu-item>
          <el-menu-item index="profile"><el-icon><UserFilled /></el-icon><span>个人资料</span></el-menu-item>
          <el-menu-item index="containers"><el-icon><Box /></el-icon><span>我的容器</span></el-menu-item>
          <el-menu-item index="leaderboard"><el-icon><TrendCharts /></el-icon><span>排行榜</span></el-menu-item>
          <el-menu-item v-if="user.is_admin" index="admin"><el-icon><Setting /></el-icon><span>管理后台</span></el-menu-item>
          <el-menu-item index="logout" @click="handleLogout"><el-icon><SwitchButton /></el-icon><span>退出登录</span></el-menu-item>
        </el-menu>
      </el-aside>
      <el-main>
        <el-card>
          <template #header><h2>🏆 排行榜</h2></template>
          <el-table :data="leaderboard" v-loading="loading" border>
            <el-table-column type="index" label="排名" width="80" :index="index => index + 1">
              <template #default="{$index}">
                <span v-if="$index === 0" style="color: #FFD700; font-size: 20px;">🥇</span>
                <span v-else-if="$index === 1" style="color: #C0C0C0; font-size: 20px;">🥈</span>
                <span v-else-if="$index === 2" style="color: #CD7F32; font-size: 20px;">🥉</span>
                <span v-else>{{ $index + 1 }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="display_name" label="用户" />
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="solved_count" label="解题数" width="100" />
            <el-table-column prop="total_points" label="总分" width="100" />
          </el-table>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getLeaderboard } from '@/api/user'

export default {
  setup() {
    const router = useRouter()
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    const leaderboard = ref([])
    const loading = ref(false)

    onMounted(async () => {
      loading.value = true
      try {
        leaderboard.value = await getLeaderboard()
      } finally {
        loading.value = false
      }
    })

    const handleMenuSelect = (index) => {
      if (index === 'admin') router.push('/admin')
      else router.push(`/${index}`)
    }

    const handleLogout = () => {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      ElMessage.success('已退出登录')
      router.push('/login')
    }

    return { user, leaderboard, loading, handleMenuSelect, handleLogout }
  }
}
</script>

<style scoped>
.leaderboard-container { min-height: 100vh; background: #f0f2f5; }
.el-aside { background: #001529; min-height: 100vh; }
.logo { height: 60px; line-height: 60px; text-align: center; color: #fff; font-size: 20px; font-weight: bold; background: rgba(255,255,255,0.1); }
.el-menu { border: none; background: #001529; }
:deep(.el-menu-item) { color: rgba(255,255,255,0.65); }
:deep(.el-menu-item:hover) { color: #fff; background: rgba(255,255,255,0.1) !important; }
:deep(.el-menu-item.is-active) { color: #fff; background: #1890ff !important; }
.el-main { padding: 20px; }
</style>
