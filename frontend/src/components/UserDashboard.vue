<template>
  <div class="user-dashboard">
    <nav class="user-navbar">
      <div class="navbar-content">
        <div class="navbar-brand">
          <span>Quick Park</span>
        </div>
        <div class="navbar-menu">
          <a class="nav-item active" @click="$emit('switchView','UserDashboard')">
            <i class="fas fa-home me-2"></i>Dashboard
          </a>
          <a class="nav-item" @click="showBookParking">
            <i class="fas fa-car me-2"></i>Book Parking
          </a>
          <a class="nav-item" @click="$emit('switchView','UserBookingHistory')">
            <i class="fas fa-history me-2"></i>History
          </a>
          <a class="nav-item" @click="showReports">
            <i class="fas fa-chart-bar me-2"></i>Reports
          </a>
        </div>
        <div class="navbar-user">
          <span class="user-name"><i class="fas fa-user-circle me-2"></i>{{ userName }}</span>
          <button class="btn-profile" @click="showProfile" title="View Profile">
            <i class="fas fa-user"></i>
          </button>
          <button class="btn-logout" @click="logout">
            <i class="fas fa-sign-out-alt me-1"></i>Logout
          </button>
        </div>
      </div>
    </nav>
    <div class="dashboard-wrapper">
      <div class="overlay"></div>
      
      <div class="dashboard-main">
        <div class="welcome-section">
          <h1 class="welcome-title">Welcome, {{ userName }}!</h1>
          <p class="welcome-subtitle">Your parking dashboard - manage bookings and view activity</p>
        </div>
        <div class="metrics-section">
          <div class="metrics-grid-top">
            <div class="metric-card-large blue-card">
              <div class="metric-header">
                <i class="fas fa-car"></i>
                <span>Active Bookings</span>
              </div>
              <div class="metric-large-value">{{ activeBookings }}</div>
              <div class="metric-subtext">Current parking sessions</div>
            </div>

            <div class="metric-card-large green-card">
              <div class="metric-header">
                <i class="fas fa-history"></i>
                <span>Total Bookings</span>
              </div>
              <div class="metric-large-value">{{ pastBookings + activeBookings }}</div>
              <div class="metric-subtext">All-time parking sessions</div>
            </div>

            <div class="metric-card-large purple-card">
              <div class="metric-header">
                <i class="fas fa-rupee-sign"></i>
                <span>Total Spent</span>
              </div>
              <div class="metric-large-value">₹{{ totalSpent.toFixed(0) }}</div>
              <div class="metric-subtext">Parking fees paid</div>
            </div>
          </div>
        </div>

        <div class="content-section">
          <div v-if="currentView === null" class="chart-container">
            <div class="card-header">
              <h3><i class="fas fa-car me-2"></i>Active Parking Sessions</h3>
            </div>
            <div class="chart-inner">
              <div v-if="getActiveBookings.length === 0" class="empty-state">
                <i class="fas fa-inbox fa-3x"></i>
                <p>No active parking sessions</p>
              </div>
              <div v-else class="bookings-list">
                <div v-for="booking in getActiveBookings" :key="booking.id" class="booking-card-item">
                  <div class="booking-card-left">
                    <div class="booking-lot-badge">{{ booking.lot_name }}</div>
                    <div class="booking-spot">Spot #{{ booking.spot_number || booking.spot_id }}</div>
                  </div>
                  <div class="booking-card-middle">
                    <div class="booking-vehicle">{{ booking.vehicle_number }}</div>
                    <div class="booking-time">Started: {{ formatDateTime(booking.start_time) }}</div>
                    <div class="booking-rate">₹{{ booking.rate_per_hour }}/hour</div>
                  </div>
                  <div class="booking-card-right">
                    <button class="btn-parkout" @click="parkOut(booking)">
                      <i class="fas fa-sign-out-alt me-1"></i> Park Out
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="currentView === null" class="chart-container">
            <div class="card-header">
              <h3><i class="fas fa-list me-2"></i>Recent Bookings</h3>
            </div>
            <div class="chart-inner">
              <div v-if="getCompletedBookings.length === 0" class="empty-state">
                <i class="fas fa-inbox fa-3x"></i>
                <p>No completed bookings yet</p>
              </div>
              <div v-else class="bookings-list">
                <div v-for="booking in getCompletedBookings.slice(0, 5)" :key="booking.id" class="booking-card-item completed">
                  <div class="booking-card-left">
                    <div class="booking-lot-badge">{{ booking.lot_name }}</div>
                    <div class="booking-spot">Spot #{{ booking.spot_number || booking.spot_id }}</div>
                  </div>
                  <div class="booking-card-middle">
                    <div class="booking-vehicle">{{ booking.vehicle_number }}</div>
                    <div class="booking-duration">{{ booking.duration_hours ? booking.duration_hours.toFixed(1) + ' hours' : 'N/A' }}</div>
                    <div class="booking-amount">Amount: <span class="text-amount">₹{{ booking.amount_paid.toFixed(2) }}</span></div>
                  </div>
                  <div class="booking-card-right">
                    <button class="btn-receipt" @click="viewReceipt(booking)">
                      <i class="fas fa-receipt me-1"></i> Receipt
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "UserDashboard",
  props: {
    bgImage: {
      type: String,
      default: require('@/assets/user-bg.jpg')  
    },
    initialData: { 
        type: Object,
        default: () => ({ user: {}, bookings: [] })
    }
  },
  data() {
    return {
      userName: "Guest User", 
      currentView: null, 
      activeBookings: 0,
      pastBookings: 0,
      totalSpent: 0,
      bookings: [],
      userDetails: {},
      historySearch: '',
      historySortBy: 'recent',
    };
  },
  created() {
    this.loadInitialData();
    this.fetchUserData();
  },
  activated() {
    this.refreshBookings();
    this.fetchUserData();
  },
  computed: {
    getActiveBookings() {
      return this.bookings.filter(b => b.status === 'Active');
    },
    getCompletedBookings() {
      return this.bookings.filter(b => b.status === 'Completed');
    },
    filteredHistory() {
      let history = this.bookings.filter(b => b.status === 'Completed');
      if (this.historySearch) {
        const search = this.historySearch.toLowerCase();
        history = history.filter(b => 
          b.lot_name.toLowerCase().includes(search) || 
          b.vehicle_number.toLowerCase().includes(search)
        );
      }
      if (this.historySortBy === 'recent') {
        history.sort((a, b) => new Date(b.start_time) - new Date(a.start_time));
      } else if (this.historySortBy === 'oldest') {
        history.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
      } else if (this.historySortBy === 'expensive') {
        history.sort((a, b) => b.amount_paid - a.amount_paid);
      } else if (this.historySortBy === 'cheapest') {
        history.sort((a, b) => a.amount_paid - b.amount_paid);
      }
      
      return history;
    }
  },
  methods: {
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },
    loadInitialData() {
        if (this.initialData.ok && this.initialData.user) {
            const userData = this.initialData;
            this.userName = userData.user.full_name || "User";
            this.userDetails = userData.user;
            this.bookings = userData.bookings || [];
            this.calculateMetrics(this.bookings);
        } else {
            this.fetchUserData(); 
        }
    },
    calculateMetrics(bookings) {
        this.activeBookings = bookings.filter(b => b.status === 'Active').length;
        this.pastBookings = bookings.filter(b => b.status === 'Completed').length;
        this.totalSpent = bookings.reduce((sum, b) => sum + parseFloat(b.amount_paid || 0), 0);
    },
    async fetchUserData() {
      try {
        console.log("Fetching user data...");
        const res = await this.$axios.get("http://127.0.0.1:5000/api/user/dashboard"); 
        const userData = res.data;
        console.log("User dashboard response:", userData);
        
        if (userData.ok) {
            this.userName = userData.user.full_name || "User";
            this.userDetails = userData.user;
            this.bookings = userData.bookings;
            console.log("User bookings loaded:", this.bookings);
            this.calculateMetrics(this.bookings);
        } else {
            console.error("API Error:", userData.message);
            if (userData.message === "Access denied") {
                this.logout(true);
            }
        }
      } catch (err) {
        console.error("Error fetching user data:", err);
        if (err.response && err.response.status === 401) {
            this.logout(true); 
        }
      }
    },
    formatDateTime(dateTimeString) {
        if (!dateTimeString) return 'N/A';
        return new Date(dateTimeString).toLocaleString('en-IN', {
            year: 'numeric', month: 'numeric', day: 'numeric',
            hour: '2-digit', minute: '2-digit', hour12: true
        });
    },
    showBookParking() {
      this.$emit('switchView', 'BookParking');
    },
    showHistory() {
      this.currentView = 'history';
      this.historySearch = '';
      this.historySortBy = 'recent';
    },
    backToDashboard() {
      this.currentView = null;
    },
    showReports() {
      this.$emit('switchView', 'UserReports');
    },
    showProfile() {
      this.$emit('switchView', 'UserProfile');
    },
    async refreshBookings() {
      try {
        console.log("Refreshing bookings...");
        const response = await this.$axios.get("http://127.0.0.1:5000/api/user/bookings");
        console.log("Bookings response:", response.data);
        if (response.data.ok) {
          this.bookings = response.data.bookings;
          console.log("Bookings loaded:", this.bookings);
          this.calculateMetrics(this.bookings);
        } else {
          console.error("API Error:", response.data.message);
        }
      } catch (err) {
        console.error("Error refreshing bookings:", err);
        if (err.response && err.response.status === 401) {
          this.logout(true);
        }
      }
    },
    showLotSummary() {
      alert("Navigating to Lot Summary...");
    },
    async parkOut(booking) {
      const startTime = new Date(booking.start_time);
      const currentTime = new Date();
      const durationHours = (currentTime - startTime) / (1000 * 60 * 60);
      const estimatedCost = Math.ceil(durationHours) * booking.rate_per_hour;
      
      const confirmMessage = `
        🚗 PARK OUT CONFIRMATION 🚗
        
        Location: ${booking.lot_name}
        Spot: #${booking.spot_id}
        Vehicle: ${booking.vehicle_number}
        Start Time: ${startTime.toLocaleString()}
        Current Duration: ${durationHours.toFixed(1)} hours
        
        💰 COST CALCULATION:
        • Rate: ₹${booking.rate_per_hour}/hour
        • Duration: ${Math.ceil(durationHours)} hours (rounded up)
        • Estimated Cost: ₹${estimatedCost}
        
        ⚠️ This action will finalize your parking session and process payment.
        
        Do you want to proceed with park out?
      `;

      if (!confirm(confirmMessage)) {
        return;
      }
      
      try {
        const res = await this.$axios.post(
          `http://127.0.0.1:5000/api/bookings/park-out`,
          { bookingId: booking.id }
        );
        
        if (res.data.ok) {
            const bookingData = res.data.booking;
            const finalAmount = bookingData.amount_paid;
            const endTime = bookingData.end_time;
            const startTime = bookingData.start_time;
            const actualDuration = bookingData.duration_hours;
            const durationMinutes = bookingData.duration_minutes;
            const hoursCharged = bookingData.hours_charged;
            const ratePerHour = bookingData.rate_per_hour;

            this.bookings = this.bookings.map(b => 
                b.id === booking.id ? 
                { 
                    ...b, 
                    status: 'Completed', 
                    end_time: endTime, 
                    amount_paid: finalAmount,
                    duration_hours: actualDuration,
                    start_time: startTime
                } : b
            );
            
            this.calculateMetrics(this.bookings); 

            const successMessage = `
              ✅ PARK OUT SUCCESSFUL! ✅
              
              🕐 TIME DETAILS:
              • Start Time: ${new Date(startTime).toLocaleString()}
              • End Time: ${new Date(endTime).toLocaleString()}
              • Total Duration: ${actualDuration.toFixed(2)} hours (${durationMinutes.toFixed(0)} minutes)
              
              💰 COST BREAKDOWN:
              • Rate: ₹${ratePerHour}/hour
              • Hours Charged: ${hoursCharged} hours (rounded up)
              • Total Amount: ₹${finalAmount.toFixed(2)}
              
              💳 Payment has been processed automatically.
              You can view the detailed receipt anytime.
            `;
            alert(successMessage);
        } else {
            alert(`Park out failed: ${res.data.message}`);
        }
        
      } catch (err) {
        console.error("Error during park out:", err);
        if (err.response && err.response.status === 401) {
            this.logout(true);
        } else {
            alert("Failed to park out. Please check if the booking is active and try again.");
        }
      }
    },
    async viewReceipt(booking) {
      try {
        const receiptUrl = `#/receipt?bookingId=${booking.id}`;
        window.open(receiptUrl, '_blank');
      } catch (err) {
        console.error("Error opening receipt:", err);
        alert("Failed to open receipt");
      }
    },
    logout(force = false) {
      localStorage.removeItem('accessToken');
      delete this.$axios.defaults.headers.common['Authorization'];

      this.$axios.post("http://127.0.0.1:5000/api/logout", {})
        .finally(() => {
            if (force) {
                alert("Session expired or unauthorized. Please log in again.");
            }
            this.$emit("switchView", "Home");
        });
    },
  },
};
</script>

<style scoped>
.user-dashboard {
  position: relative;
  min-height: 100vh;
  background: url("@/assets/user-bg.jpg") no-repeat center center;
  background-size: cover;
  background-attachment: fixed;
  display: flex;
  flex-direction: column;
}

.user-navbar {
  background: linear-gradient(135deg, #1a252f 0%, #2c3e50 50%, #3498db 100%);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  padding: 16px 0;
  position: relative;
  z-index: 100;
  border-bottom: 1px solid rgba(52, 152, 219, 0.2);
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 30px;
  width: 100%;
}

.navbar-brand {
  display: flex;
  align-items: center;
  font-size: 1.6rem;
  font-weight: 800;
  color: white;
  text-decoration: none;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  letter-spacing: -0.5px;
}

.navbar-menu {
  display: flex;
  gap: 35px;
  align-items: center;
  flex: 1;
  margin-left: 60px;
}

.nav-item {
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 10px 14px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  font-size: 0.95rem;
  position: relative;
}

.nav-item::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: #ffffff;
  transition: width 0.3s ease;
  border-radius: 1px;
}

.nav-item:hover::after,
.nav-item.active::after {
  width: 100%;
}

.nav-item:hover,
.nav-item.active {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.15);
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-left: auto;
}

.user-name {
  color: white;
  font-weight: 600;
  display: flex;
  align-items: center;
  font-size: 0.95rem;
}

.btn-logout {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.1));
  border: 1.5px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 9px 18px;
  border-radius: 22px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
  backdrop-filter: blur(10px);
}

.btn-logout:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.15));
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.btn-profile {
  background: linear-gradient(135deg, #3498db, #2980b9);
  border: none;
  color: white;
  padding: 9px 15px;
  border-radius: 22px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1.1rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
}

.btn-profile:hover {
  background: linear-gradient(135deg, #2980b9, #1f618d);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(52, 152, 219, 0.4);
}

.dashboard-wrapper {
  position: relative;
  flex: 1;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 40px 20px;
  overflow-y: auto;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(15, 23, 42, 0.55);
  z-index: 1;
  backdrop-filter: blur(2px);
}

.dashboard-main {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
}

.welcome-section {
  text-align: center;
  margin-bottom: 40px;
  animation: slideDown 0.6s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.welcome-title {
  font-size: 2.8rem;
  font-weight: 800;
  color: white;
  text-shadow: 0 3px 10px rgba(0, 0, 0, 0.5);
  margin-bottom: 8px;
  letter-spacing: -1px;
}

.welcome-subtitle {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
  font-weight: 500;
}

.metrics-section {
  margin-bottom: 40px;
}

.metrics-grid-top {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 22px;
  margin-bottom: 18px;
}

.metric-card-large {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 28px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  color: white;
}

.metric-card-large::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.15) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.metric-card-large:hover {
  transform: translateY(-10px);
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.3);
}

.metric-card-large:hover::before {
  opacity: 1;
}

.metric-card-large.blue-card {
  border-left: 4px solid #3498db;
}

.metric-card-large.green-card {
  border-left: 4px solid #2ecc71;
}

.metric-card-large.purple-card {
  border-left: 4px solid #9b59b6;
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  font-size: 0.9rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-header i {
  font-size: 1.3rem;
  opacity: 0.9;
}

.metric-large-value {
  font-size: 2.5rem;
  font-weight: 800;
  color: white;
  line-height: 1;
  margin-bottom: 8px;
}

.metric-subtext {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.content-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
  gap: 22px;
  margin-bottom: 30px;
}

.chart-container {
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.chart-container:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25);
}

.card-header {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.02);
}

.card-header h3 {
  font-size: 1.3rem;
  font-weight: 700;
  color: white;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header i {
  color: #3498db;
  font-size: 1.2rem;
}

.chart-inner {
  padding: 24px;
  min-height: 200px;
}

.bookings-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.booking-card-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.booking-card-item:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateX(4px);
}

.booking-card-item.completed {
  opacity: 0.85;
}

.booking-card-left {
  min-width: 140px;
}

.booking-lot-badge {
  display: inline-block;
  padding: 6px 12px;
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.3), rgba(52, 152, 219, 0.1));
  border: 1px solid rgba(52, 152, 219, 0.5);
  border-radius: 8px;
  color: #3498db;
  font-weight: 700;
  font-size: 0.85rem;
  margin-bottom: 8px;
}

.booking-spot {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.booking-card-middle {
  flex: 1;
}

.booking-vehicle {
  font-weight: 700;
  color: white;
  font-size: 1rem;
  margin-bottom: 4px;
}

.booking-time {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 4px;
}

.booking-rate {
  font-size: 0.9rem;
  color: #2ecc71;
  font-weight: 600;
}

.booking-duration {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 4px;
}

.booking-amount {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
}

.text-amount {
  color: #2ecc71;
  font-weight: 700;
  font-size: 1rem;
}

.booking-card-right {
  flex-shrink: 0;
}

.btn-parkout,
.btn-receipt {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}

.btn-parkout {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
}

.btn-parkout:hover {
  background: linear-gradient(135deg, #c82333, #bd2130);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(220, 53, 69, 0.4);
}

.btn-receipt {
  background: linear-gradient(135deg, #17a2b8, #138496);
  color: white;
  box-shadow: 0 4px 12px rgba(23, 162, 184, 0.3);
}

.btn-receipt:hover {
  background: linear-gradient(135deg, #138496, #0c5460);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(23, 162, 184, 0.4);
}

.empty-state {
  text-align: center;
  padding: 50px 20px;
  color: rgba(255, 255, 255, 0.5);
}

.empty-state i {
  font-size: 2.5rem;
  margin-bottom: 12px;
  color: rgba(255, 255, 255, 0.3);
}

.empty-state p {
  font-size: 1rem;
  margin: 0;
}
@media (max-width: 1200px) {
  .content-section {
    grid-template-columns: 1fr;
  }

  .navbar-menu {
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .dashboard-wrapper {
    padding: 24px 12px;
  }

  .dashboard-main {
    width: 100%;
  }

  .welcome-title {
    font-size: 2rem;
  }

  .welcome-subtitle {
    font-size: 0.95rem;
  }

  .metrics-grid-top {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .metric-card-large {
    padding: 20px;
  }

  .metric-large-value {
    font-size: 2rem;
  }

  .navbar-menu {
    display: none;
  }

  .navbar-content {
    padding: 0 16px;
  }

  .booking-card-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .booking-card-left {
    min-width: auto;
    width: 100%;
  }

  .booking-card-middle {
    width: 100%;
  }

  .booking-card-right {
    align-self: flex-end;
  }

  .profile-header {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }

  .profile-info {
    text-align: center;
  }

  .profile-avatar {
    width: 100px;
    height: 100px;
  }

  .profile-details .detail-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }

  .profile-actions {
    justify-content: center;
    flex-wrap: wrap;
  }

  .form-group {
    margin-bottom: 14px;
  }

  .btn {
    flex: 1;
    justify-content: center;
    min-width: 140px;
  }
}

@media (max-width: 480px) {
  .welcome-title {
    font-size: 1.5rem;
  }

  .metric-card-large {
    padding: 16px;
  }

  .metric-header {
    font-size: 0.8rem;
  }

  .metric-large-value {
    font-size: 1.8rem;
  }

  .card-header h3 {
    font-size: 1.1rem;
  }
}
</style>