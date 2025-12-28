import { createRouter, createWebHistory } from 'vue-router'
import UploadPage from '../pages/UploadPage.vue'
import ResultsPage from '../pages/ResultsPage.vue'

const routes = [
    {
        path: '/',
        name: 'Upload',
        component: UploadPage
    },
    {
        path: '/results/:filename',
        name: 'Results',
        component: ResultsPage,
        props: true
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
