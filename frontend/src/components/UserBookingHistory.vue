<template>
  <div class="user-dashboard">
    <nav class="user-navbar">
      <div class="navbar-content">
        <div class="navbar-brand">
          <span>Quick Park</span>
        </div>
        <div class="navbar-menu">
          <a class="nav-item" @click="showDashboard">
            <i class="fas fa-home me-2"></i>Dashboard
          </a>
          <a class="nav-item" @click="showBookParking">
            <i class="fas fa-car me-2"></i>Book Parking
          </a>
          <a class="nav-item active" @click="showHistory">
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
            <h1 class="welcome-title">Find Your Booking History</h1>
            <p class="welcome-subtitle">Review your past parking sessions and view receipts</p>
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
              <div class="metric-large-value">{{ totalBookings }}</div>
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

        <div class="history-section">
          <div class="card-header">
            <h3><i class="fas fa-history me-2"></i>Booking History</h3>
            <div class="history-controls">
              <input v-model="historySearch" type="text" class="history-search" placeholder="Search lot name or vehicle...">
              <select v-model="historySortBy" class="history-sort">
                <option value="recent">Most Recent</option>
                <option value="oldest">Oldest First</option>
                <option value="expensive">Most Expensive</option>
                <option value="cheapest">Cheapest</option>
              </select>
            </div>
          </div>
          
          <div class="chart-inner">
            <div v-if="isLoading" class="empty-state">
              <i class="fas fa-spinner fa-spin fa-3x"></i>
              <p>Loading booking history...</p>
            </div>
            
            <div v-else-if="filteredHistory.length === 0" class="empty-state">
              <i class="fas fa-inbox fa-3x"></i>
              <p>No booking history found</p>
            </div>
            
            <div v-else class="history-list">
              <div v-for="(booking, index) in filteredHistory" :key="booking.id" class="history-item">
                <div class="history-index">
                  <span class="history-number">{{ index + 1 }}</span>
                </div>
                
                <div class="history-details">
                  <div class="history-lot-info">
                    <h4 class="history-lot">{{ booking.lot_name }}</h4>
                    <span class="history-spot">Spot #{{ booking.spot_number || booking.spot_id }}</span>
                  </div>
                  
                  <div class="history-vehicle-info">
                    <p class="history-vehicle"><i class="fas fa-car me-1"></i>{{ booking.vehicle_number }}</p>
                    <p class="history-date"><i class="fas fa-calendar me-1"></i>{{ formatDate(booking.start_time) }}</p>
                  </div>
                </div>
                
                <div class="history-duration">
                  <div class="duration-label">Duration</div>
                  <div class="duration-value">{{ booking.duration_hours ? booking.duration_hours.toFixed(1) : '0' }}h</div>
                  <div class="duration-subtext">{{ booking.duration_minutes ? `${Math.floor(booking.duration_minutes % 60)}m` : '0m' }}</div>
                </div>
                
                <div class="history-amount">
                  <div class="amount-label">Amount Paid</div>
                  <div class="amount-value">₹{{ booking.amount_paid.toFixed(2) }}</div>
                  <div class="amount-rate">@ ₹{{ booking.rate_per_hour }}/hr</div>
                </div>
                
                <div class="history-actions">
                  <button class="btn-history-receipt" @click="viewReceipt(booking)">
                    <i class="fas fa-receipt me-1"></i>Receipt
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <div class="history-footer" style="padding: 10px;">
            <span style="color: rgba(255,255,255,0.4); font-size: 0.8rem;">End of history</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "UserHistory",
  data() {
    return {
      isLoading: true,
      userName: "User", 
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
    this.fetchData();
  },
  computed: {
    totalBookings() {
      return this.pastBookings + this.activeBookings;
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
    async fetchData() {
      this.isLoading = true;
      try {
        console.log("Fetching user data and bookings...");
        const res = await this.$axios.get("http://127.0.0.1:5000/api/user/dashboard");
        const userData = res.data;
        
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
      } finally {
        this.isLoading = false;
      }
    },
    calculateMetrics(bookings) {
        this.activeBookings = bookings.filter(b => b.status === 'Active').length;
        this.pastBookings = bookings.filter(b => b.status === 'Completed').length;
        this.totalSpent = bookings.reduce((sum, b) => sum + parseFloat(b.amount_paid || 0), 0);
    },
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
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
    showDashboard() {
      this.$emit('switchView', 'UserDashboard');
    },
    showBookParking() {
      this.$emit('switchView', 'BookParking');
    },
    showHistory() {
      console.log("Already on History page.");
      this.fetchData();
    },
    showReports() {
      this.$emit('switchView', 'UserReports');
    },
    showProfile() {
      this.$emit('switchView', 'UserProfile');
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
.history-section {
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  animation: slideDown 0.6s ease;
}

.history-section .card-header {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.02);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.history-section .card-header h3 {
  font-size: 1.3rem;
  font-weight: 700;
  color: white;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.history-section .card-header i {
  color: #3498db;
  font-size: 1.2rem;
}

.history-controls {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.history-search {
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(0, 0, 0, 0.3);
  color: white;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  min-width: 250px;
  font-family: inherit;
}

.history-search::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.history-search:focus {
  border-color: #3498db;
  background: rgba(52, 152, 219, 0.1);
  outline: none;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.history-sort {
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(0, 0, 0, 0.3);
  color: white;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  min-width: 150px;
  font-family: inherit;
  cursor: pointer;
}

.history-sort option {
  background: #1a252f;
  color: white;
}

.history-sort:focus {
  border-color: #3498db;
  background: rgba(52, 152, 219, 0.1);
  outline: none;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 18px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.history-item:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateX(4px);
}

.history-index {
  min-width: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.history-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.3), rgba(52, 152, 219, 0.1));
  border: 1.5px solid rgba(52, 152, 219, 0.5);
  border-radius: 50%;
  color: #3498db;
  font-weight: 700;
  font-size: 1rem;
}

.history-details {
  flex: 2;
  display: flex;
  gap: 20px;
}

.history-lot-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 150px;
}

.history-lot {
  font-weight: 700;
  color: white;
  font-size: 1rem;
  margin: 0;
}

.history-spot {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.history-vehicle-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-vehicle {
  font-size: 0.9rem;
  color: white;
  font-weight: 600;
  margin: 0;
}

.history-date {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.history-duration {
  text-align: center;
  padding: 12px 18px;
  background: rgba(46, 204, 113, 0.1);
  border-radius: 8px;
  border-left: 3px solid #2ecc71;
  min-width: 100px;
}

.duration-label {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.duration-value {
  font-size: 1.3rem;
  font-weight: 700;
  color: #2ecc71;
}

.duration-subtext {
  font-size: 0.85rem;
  color: rgba(46, 204, 113, 0.8);
}

.history-amount {
  text-align: center;
  padding: 12px 18px;
  background: rgba(155, 89, 182, 0.1);
  border-radius: 8px;
  border-left: 3px solid #9b59b6;
  min-width: 120px;
}

.amount-label {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.amount-value {
  font-size: 1.4rem;
  font-weight: 700;
  color: #9b59b6;
}

.amount-rate {
  font-size: 0.8rem;
  color: rgba(155, 89, 182, 0.8);
}

.history-actions {
  display: flex;
  gap: 8px;
  min-width: 120px;
}

.btn-history-receipt {
  padding: 9px 16px;
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.3), rgba(52, 152, 219, 0.1));
  border: 1px solid rgba(52, 152, 219, 0.5);
  color: #3498db;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}

.btn-history-receipt:hover {
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.5), rgba(52, 152, 219, 0.2));
  border-color: rgba(52, 152, 219, 0.8);
  transform: translateY(-2px);
}

.history-footer {
  padding: 16px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.02);
  display: flex;
  justify-content: center;
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
  .profile-header {
    flex-direction: column;
    text-align: center;
    gap: 16px;
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
  
  .history-section .card-header {
    flex-direction: column;
  }

  .history-item {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .history-details {
    width: 100%;
    order: 1;
    flex-direction: column;
    gap: 10px;
  }

  .history-index {
    order: 0;
    align-self: center;
  }
  
  .history-duration,
  .history-amount {
    width: 100%;
    order: 2;
  }
  
  .history-actions {
    order: 3;
    justify-content: center;
  }

  .history-controls {
    flex-direction: column;
    gap: 12px;
    width: 100%;
  }

  .history-search,
  .history-sort {
    width: 100%;
    min-width: 0;
  }
}
</style>