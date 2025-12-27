<template>
  <div class="admin-users-container">
    <el-container>
      <el-aside width="250px">
        <div class="logo">CyberPrism</div>
        <el-menu :default-active="'admin/users'" @select="handleMenuSelect">
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
              <h2>用户管理</h2>
              <el-space>
                <el-input
                  v-model="searchQuery"
                  placeholder="搜索用户名或邮箱"
                  clearable
                  style="width: 250px"
                  @input="handleSearch"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-button type="primary" @click="showAddDialog">添加用户</el-button>
              </el-space>
            </div>
          </template>

          <el-table :data="filteredUsers" v-loading="loading" border>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="username" label="用户名" width="120" />
            <el-table-column prop="display_name" label="姓名" width="120" />
            <el-table-column prop="common_id" label="常用ID" width="120" />
            <el-table-column prop="email" label="邮箱" min-width="180" />
            <el-table-column prop="is_admin" label="权限" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.is_admin" type="danger" size="small">管理员</el-tag>
                <el-tag v-else type="info" size="small">普通用户</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="total_points" label="总分" width="100" />
            <el-table-column prop="solved_count" label="解题数" width="100" />
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="editUser(row)">编辑</el-button>
                <el-button type="warning" size="small" @click="resetPassword(row.id)">重置密码</el-button>
                <el-button
                  v-if="row.username !== 'admin'"
                  type="danger"
                  size="small"
                  @click="deleteUser(row.id)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-main>
    </el-container>

    <!-- 添加/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'add' ? '添加用户' : '编辑用户'"
      width="500px"
    >
      <el-form :model="form" label-width="100px" ref="formRef" :rules="rules">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="dialogMode === 'edit'" placeholder="请输入用户名" />
        </el-form-item>

        <el-form-item label="姓名" prop="display_name">
          <el-input v-model="form.display_name" placeholder="请输入姓名" />
        </el-form-item>

        <el-form-item label="常用ID" prop="common_id">
          <el-input v-model="form.common_id" placeholder="请输入常用ID" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>

        <el-form-item v-if="dialogMode === 'add'" label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" />
        </el-form-item>

        <el-form-item label="权限" prop="is_admin">
          <el-switch
            v-model="form.is_admin"
            active-text="管理员"
            inactive-text="普通用户"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-space>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitLoading">
            {{ dialogMode === 'add' ? '添加' : '保存' }}
          </el-button>
        </el-space>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAllUsers, createUser, updateUser, deleteUser as deleteUserAPI, resetUserPassword } from '@/api/admin'

export default {
  name: 'AdminUsers',
  setup() {
    const router = useRouter()
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    const loading = ref(false)
    const users = ref([])
    const searchQuery = ref('')
    const dialogVisible = ref(false)
    const dialogMode = ref('add')
    const submitLoading = ref(false)
    const formRef = ref(null)

    const form = reactive({
      username: '',
      display_name: '',
      common_id: '',
      email: '',
      password: '',
      is_admin: false
    })

    const rules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '用户名长度为3-20个字符', trigger: 'blur' }
      ],
      display_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
      common_id: [{ required: true, message: '请输入常用ID', trigger: 'blur' }],
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度至少6个字符', trigger: 'blur' }
      ]
    }

    const filteredUsers = computed(() => {
      if (!searchQuery.value) return users.value
      const query = searchQuery.value.toLowerCase()
      return users.value.filter(user =>
        user.username.toLowerCase().includes(query) ||
        user.email.toLowerCase().includes(query) ||
        (user.display_name && user.display_name.toLowerCase().includes(query))
      )
    })

    const loadUsers = async () => {
      loading.value = true
      try {
        users.value = await getAllUsers()
      } finally {
        loading.value = false
      }
    }

    const handleSearch = () => {
      // 搜索功能由computed自动处理
    }

    const showAddDialog = () => {
      dialogMode.value = 'add'
      resetForm()
      dialogVisible.value = true
    }

    const editUser = (user) => {
      dialogMode.value = 'edit'
      Object.assign(form, {
        id: user.id,
        username: user.username,
        display_name: user.display_name,
        common_id: user.common_id,
        email: user.email,
        is_admin: user.is_admin,
        password: ''
      })
      dialogVisible.value = true
    }

    const deleteUser = async (id) => {
      try {
        await ElMessageBox.confirm('确定要删除这个用户吗? 此操作不可恢复!', '警告', {
          type: 'warning',
          confirmButtonText: '确定',
          cancelButtonText: '取消'
        })

        await deleteUserAPI(id)
        ElMessage.success('删除成功')
        loadUsers()
      } catch (error) {
        if (error !== 'cancel') {
          console.error(error)
        }
      }
    }

    const resetPassword = async (id) => {
      try {
        const { value: newPassword } = await ElMessageBox.prompt('请输入新密码 (至少6位)', '重置密码', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          inputPattern: /^.{6,}$/,
          inputErrorMessage: '密码长度至少6个字符'
        })

        await resetUserPassword(id, { new_password: newPassword })
        ElMessage.success('密码重置成功')
      } catch (error) {
        if (error !== 'cancel') {
          console.error(error)
        }
      }
    }

    const submitForm = async () => {
      if (!formRef.value) return

      try {
        await formRef.value.validate()
      } catch {
        return
      }

      const data = {
        username: form.username,
        display_name: form.display_name,
        common_id: form.common_id,
        email: form.email,
        is_admin: form.is_admin
      }

      if (dialogMode.value === 'add') {
        data.password = form.password
      }

      submitLoading.value = true
      try {
        if (dialogMode.value === 'add') {
          await createUser(data)
          ElMessage.success('添加成功')
        } else {
          await updateUser(form.id, data)
          ElMessage.success('更新成功')
        }
        dialogVisible.value = false
        loadUsers()
      } finally {
        submitLoading.value = false
      }
    }

    const resetForm = () => {
      Object.assign(form, {
        username: '',
        display_name: '',
        common_id: '',
        email: '',
        password: '',
        is_admin: false
      })
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
      loadUsers()
    })

    return {
      user,
      loading,
      filteredUsers,
      searchQuery,
      dialogVisible,
      dialogMode,
      submitLoading,
      form,
      formRef,
      rules,
      handleSearch,
      showAddDialog,
      editUser,
      deleteUser,
      resetPassword,
      submitForm,
      handleMenuSelect,
      handleLogout
    }
  }
}
</script>

<style scoped>
.admin-users-container {
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
</style>
