import request from './request'

// 用户注册
export const register = (data) => {
  return request.post('/auth/register', data)
}

// 用户登录
export const login = (data) => {
  return request.post('/auth/login', data)
}

// 获取当前用户信息
export const getCurrentUser = () => {
  return request.get('/auth/me')
}

// 更新用户信息
export const updateUser = (data) => {
  return request.put('/auth/me', data)
}

// 获取用户资料和技能标签
export const getUserProfile = () => {
  return request.get('/users/profile')
}

// 获取排行榜
export const getLeaderboard = () => {
  return request.get('/users/leaderboard')
}
