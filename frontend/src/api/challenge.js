import request from './request'

// 获取题目列表
export const getChallenges = (params) => {
  return request.get('/challenges/', { params })
}

// 获取题目详情
export const getChallenge = (id) => {
  return request.get(`/challenges/${id}`)
}

// 提交答案
export const submitAnswer = (id, data) => {
  return request.post(`/challenges/${id}/submit`, data)
}

// 获取题目分类
export const getCategories = () => {
  return request.get('/challenges/categories')
}
