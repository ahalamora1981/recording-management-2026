import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import MainLayout from '../views/MainLayout.vue'
import QueryView from '../views/QueryView.vue'
import ImportView from '../views/ImportView.vue'
import UsersView from '../views/UsersView.vue'

const routes = [
  {
    path: '/',
    redirect: '/query'
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'query',
        name: 'query',
        component: QueryView
      },
      {
        path: 'import',
        name: 'import',
        component: ImportView
      },
      {
        path: 'users',
        name: 'users',
        component: UsersView,
        meta: { requiresAdmin: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.requiresAdmin && localStorage.getItem('isAdmin') !== 'true') {
    next('/query')
  } else if (to.path === '/login' && token) {
    next('/query')
  } else {
    next()
  }
})

export default router
