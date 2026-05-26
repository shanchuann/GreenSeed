import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
    {
      path: '/jobs',
      name: 'jobs',
      component: () => import('@/views/JobsView.vue'),
    },
    {
      path: '/jobs/:id',
      name: 'job-detail',
      component: () => import('@/views/JobDetailView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/auth/RegisterView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/seeker/ProfileView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/applications',
      name: 'applications',
      component: () => import('@/views/seeker/ApplicationsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/recruiter',
      name: 'recruiter',
      component: () => import('@/views/recruiter/DashboardView.vue'),
      meta: { requiresAuth: true, role: 'recruiter' },
    },
    {
      path: '/recruiter/post',
      name: 'post-job',
      component: () => import('@/views/recruiter/PostJobView.vue'),
      meta: { requiresAuth: true, role: 'recruiter' },
    },
    {
      path: '/recruiter/applications/:id',
      name: 'recruiter-applications',
      component: () => import('@/views/recruiter/ApplicationsView.vue'),
      meta: { requiresAuth: true, role: 'recruiter' },
    },
    {
      path: '/recruiter/company/create',
      name: 'company-create',
      component: () => import('@/views/recruiter/CompanyCreateView.vue'),
      meta: { requiresAuth: true, role: 'recruiter' },
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('@/views/admin/DashboardView.vue'),
      meta: { requiresAuth: true, role: 'admin' },
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.guestOnly && auth.isLoggedIn) {
    return { name: 'home' }
  }
  if (to.meta.role && auth.user?.role !== to.meta.role) {
    return { name: 'home' }
  }
})

export default router
