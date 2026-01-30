<template>
  <div>
    <Navbar 
      v-if="['Home', 'Login', 'Register', 'ForgotPassword', 'ResetPassword'].includes(currentView) && $route.name !== 'ReceiptView' && $route.name !== 'SlotDetailView'" 
      @switchView="switchView" 
    />

    <div class="container-fluid p-0">
      <router-view v-if="['ReceiptView', 'SlotDetailView'].includes($route.name)"></router-view>
      <component 
        v-else
        :is="currentView" 
        @switchView="switchView" 
        @loginSuccess="handleLogin" 
        @bookingSuccess="handleBookingSuccess"
        :initialData="initialDashboardData"
        :userDetails="initialDashboardData.user"
        :key="componentKey" 
      />
    </div>
  </div>
</template>

<script>
import mitt from "mitt";

import Navbar from "./components/home/Navbar.vue";
import Home from "./components/home/Home.vue";
import Login from "./components/home/Login.vue";
import Register from "./components/home/Register.vue";
import AdminDashboard from "./components/admin/AdminDashboard.vue";
import UserDashboard from "./components/UserDashboard.vue";
import BookParking from "./components/BookParking.vue";
import ForgotPassword from "./components/home/ForgotPassword.vue";
import ResetPassword from "./components/home/ResetPassword.vue";
import ManageParkingLots from "./components/admin/ManageParkingLots.vue";
import ParkingLotForm from "./components/admin/ParkingLotForm.vue";
import ManageUser from "./components/admin/ManageUser.vue";
import Reports from "./components/admin/Reports.vue";
import UserReports from "./components/UserReports.vue";
import UserBookingHistory from "./components/UserBookingHistory.vue";
import UserProfile from "./components/UserProfile.vue";
import ReceiptView from "./components/ReceiptView.vue";
import SlotDetailView from "./components/admin/SlotDetailView.vue";
const emitter = mitt();

export default {
  name: "App",
  components: { 
    Navbar, 
    Home, 
    Login, 
    Register, 
    AdminDashboard, 
    UserDashboard, 
    BookParking,
    ForgotPassword,
    ResetPassword, 
    ManageParkingLots, 
    ParkingLotForm, 
    ManageUser,
    Reports,
    UserReports,
    UserBookingHistory,
    UserProfile,
    ReceiptView,
    SlotDetailView 
  },
  data() {
    return {
      currentView: "Home",
      userRole: null,
      initialDashboardData: {},
      componentKey: 0, 
    };
  },
  provide() {
    return {
      emitter
    };
  },
  created() { 
    emitter.on("parkingLotChanged", this.reloadDashboard);
    if (localStorage.getItem('accessToken')) {
    }
  },
  beforeUnmount() {
    emitter.off("parkingLotChanged", this.reloadDashboard);
  },
  methods: {
    switchView(view) {
      this.currentView = view;
      if (view === 'BookParking' && !this.initialDashboardData.user) {
        this.fetchUserData();
      }
    },
    handleLogin(payload) {
      this.userRole = payload.role;
      this.initialDashboardData = payload.initialData;

      if (this.userRole === "admin") { 
        this.currentView = "AdminDashboard";
      } else if (this.userRole === "user") {
        this.currentView = "UserDashboard";
      }
    },
    handleBookingSuccess() {
      this.componentKey += 1;
    },
    reloadDashboard() {
      this.componentKey += 1;
    },
    async fetchUserData() {
      try {
        const token = localStorage.getItem('accessToken');
        if (!token) return;
        
        const response = await fetch('http://127.0.0.1:5000/api/me', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          if (data.ok) {
            this.initialDashboardData.user = data.user;
          }
        }
      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    }
  },
};
</script>

<style>
body, html, #app {
  margin: 0;
  padding: 0;
  height: 100%;
  background-color: #212121;
  color: white;
}
</style>