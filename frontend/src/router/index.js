import { createRouter, createWebHashHistory } from 'vue-router';
import ReceiptView from '../components/ReceiptView.vue';
import SlotDetailView from '../components/admin/SlotDetailView.vue';
import Reports from '../components/admin/Reports.vue';
import UserReports from '../components/UserReports.vue';
import ResetPassword from '../components/home/ResetPassword.vue';

const routes = [
  {
    path: '/receipt',
    name: 'ReceiptView',
    component: ReceiptView,
    props: route => ({ bookingId: route.query.bookingId })
  },
  {
    path: '/slot-detail',
    name: 'SlotDetailView',
    component: SlotDetailView,
    props: route => ({ slotId: route.query.slotId, lotId: route.query.lotId })
  },
  {
    path: '/reports',
    name: 'Reports',
    component: Reports
  },
  {
    path: '/user-reports',
    name: 'UserReports',
    component: UserReports
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: ResetPassword,
    props: route => ({ token: route.query.token })
  }
];

const router = createRouter({
  history: createWebHashHistory(),
  routes
});

export default router;
