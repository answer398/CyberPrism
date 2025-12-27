import request from './request'

// ===== 用户管理 =====
export const getAllUsers = () => {
  return request.get('/admin/users')
}

export const getUserDetail = (userId) => {
  return request.get(`/admin/users/${userId}`)
}

export const createUser = (data) => {
  return request.post('/admin/users', data)
}

export const updateUser = (userId, data) => {
  return request.put(`/admin/users/${userId}`, data)
}

export const deleteUser = (userId) => {
  return request.delete(`/admin/users/${userId}`)
}

export const resetUserPassword = (userId, data) => {
  return request.post(`/admin/users/${userId}/reset-password`, data)
}

// ===== 题目管理 =====
export const getAllChallenges = () => {
  return request.get('/admin/challenges')
}

export const createChallenge = (data) => {
  return request.post('/admin/challenges', data)
}

export const updateChallenge = (challengeId, data) => {
  return request.put(`/admin/challenges/${challengeId}`, data)
}

export const deleteChallenge = (challengeId) => {
  return request.delete(`/admin/challenges/${challengeId}`)
}

// ===== 容器管理 =====
export const getAllContainers = () => {
  return request.get('/admin/containers')
}

export const stopContainer = (instanceId) => {
  return request.post(`/admin/containers/${instanceId}/stop`)
}

export const extendContainer = (instanceId, minutes) => {
  return request.post(`/admin/containers/${instanceId}/extend`, { minutes })
}

export const deleteContainer = (instanceId) => {
  return request.delete(`/admin/containers/${instanceId}`)
}

export const cleanupExpiredContainers = () => {
  return request.post('/admin/containers/cleanup')
}

// ===== 统计信息 =====
export const getStats = () => {
  return request.get('/admin/stats')
}

export const getRecentSubmissions = (limit = 10) => {
  return request.get('/admin/submissions/recent', { params: { limit } })
}

export const getTopUsers = (limit = 10) => {
  return request.get('/admin/users/top', { params: { limit } })
}

export const getChallengeStats = () => {
  return request.get('/admin/challenges/stats')
}

// ===== Docker镜像管理 =====
export const getDockerImages = () => {
  return request.get('/admin/docker-images')
}

// ===== 提交记录管理 =====
export const getAllSubmissions = (params = {}) => {
  return request.get('/admin/submissions', { params })
}

export const deleteSubmission = (submissionId) => {
  return request.delete(`/admin/submissions/${submissionId}`)
}
