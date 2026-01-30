<template>
  <div class="admin-dashboard manage-users-page">
    <nav class="admin-navbar">
      <div class="navbar-content">
        <div class="navbar-brand">
          <span>Quick Park</span>
        </div>
        <div class="navbar-menu">
          <a class="nav-item" @click="$emit('switchView','AdminDashboard')">
            <i class="fas fa-tachometer-alt me-2"></i>Dashboard
          </a>
          <a class="nav-item" @click="$emit('switchView','ManageParkingLots')">
            <i class="fas fa-map-marked-alt me-2"></i>Parking Lots
          </a>
          <a class="nav-item active" @click="$emit('switchView','ManageUser')">
            <i class="fas fa-users me-2"></i>Users
          </a>
          <a class="nav-item" @click="$emit('switchView','Reports')">
            <i class="fas fa-chart-bar me-2"></i>Reports
          </a>
        </div>
        <div class="navbar-user">
          <span class="user-name"><i class="fas fa-user-circle me-2"></i>Admin</span>
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
          <h1 class="welcome-title">Manage Users</h1>
          <p class="welcome-subtitle">View registered user details and analyze their parking activity</p>
        </div>

        <div class="search-filter-bar">
          <div class="search-container">
            <div class="search-wrapper">
              <i class="fas fa-search search-icon"></i>
              <input 
                v-model="searchQuery"
                type="text"
                class="search-input"
                placeholder="Search by name or email..."
                @input="handleSearch"
              />
            </div>
          </div>
          <div class="filter-controls">
            <select v-model="roleFilter" class="role-filter" @change="handleRoleFilter">
              <option value="">All Roles</option>
              <option value="user">Users</option>
              <option value="admin">Admins</option>
            </select>
          </div>
        </div>

        <div class="results-info">
          <span class="result-count">
            Showing {{ filteredUsers.length }} user{{ filteredUsers.length !== 1 ? 's' : '' }}
          </span>
        </div>

        <div class="table-section">
          <div class="card-header">
            <h3><i class="fas fa-list me-2"></i>Users List</h3>
          </div>
          <div class="table-container">
            <table class="users-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Total Spent (₹)</th>
                  <th>Registered</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="(user, index) in filteredUsers" :key="`row-${user.id}`">
                  <tr>
                    <td>{{ index + 1 }}</td>
                    <td class="user-name-cell">{{ user.full_name }}</td>
                    <td class="user-email">{{ user.email }}</td>
                    <td>
                      <span class="role-badge" :class="user.role.toLowerCase()">
                        {{ user.role.toUpperCase() }}
                      </span>
                    </td>
                    <td class="revenue-text">₹{{ user.total_spent.toFixed(2) }}</td>
                    <td>{{ formatDate(user.created_at) }}</td>
                    <td class="action-column">
                      <button class="btn-action history" @click="toggleBookings(user)" :title="user.id === expandedUserId ? 'Hide History' : 'Show History'">
                        <i :class="['fas', user.id === expandedUserId ? 'fa-compress-alt' : 'fa-history']"></i>
                      </button>
                      <button class="btn-action delete" @click="deleteUser(user.id)" title="Delete User">
                        <i class="fas fa-trash-alt"></i>
                      </button>
                    </td>
                  </tr>

                  <tr v-if="user.id === expandedUserId" :key="`expand-${user.id}`" class="history-expansion-row">
                    <td :colspan="7" class="p-0">
                      <div class="booking-history-section">
                        <h3 class="history-title">Booking History - {{ user.full_name }}</h3>
                        <p class="history-count">{{ user.bookings.length }} recent bookings</p>
                        
                        <div v-if="user.bookings.length > 0" class="history-grid">
                          <div v-for="booking in user.bookings" :key="`booking-${booking.id}`" class="booking-card">
                            <div class="booking-header">
                              <i class="fas fa-parking"></i>
                              <span class="lot-info">{{ booking.lot_name }} - Spot {{ booking.spot_id }}</span>
                            </div>
                            <div class="booking-details">
                              <div class="detail-row">
                                <span class="detail-label"><i class="fas fa-clock me-1"></i>Start:</span>
                                <span class="detail-value">{{ formatDateTime(booking.start_time) }}</span>
                              </div>
                              <div class="detail-row">
                                <span class="detail-label"><i class="fas fa-flag-checkered me-1"></i>End:</span>
                                <span class="detail-value">{{ formatDateTime(booking.end_time) }}</span>
                              </div>
                              <div class="detail-row amount-row">
                                <span class="detail-label"><i class="fas fa-rupee-sign me-1"></i>Cost:</span>
                                <span class="detail-value amount">₹{{ booking.amount_paid.toFixed(2) }}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                        <p v-else class="no-bookings">No booking history found for this user</p>
                      </div>
                    </td>
                  </tr>
                </template>
                <tr v-if="filteredUsers.length === 0" class="empty-state">
                  <td :colspan="7" class="text-center">
                    <i class="fas fa-search"></i>
                    <p>No users found matching your search</p>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "ManageUser", 
  inject: ["emitter"],
  data() {
    return {
      users: [],
      filteredUsers: [],
      expandedUserId: null,
      searchQuery: "",
      roleFilter: "",
    };
  },
  created() {
    this.fetchUsers();
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      return new Date(dateString).toLocaleDateString('en-IN');
    },
    formatDateTime(dateTimeString) {
      if (!dateTimeString) return 'N/A';
      return new Date(dateTimeString).toLocaleString('en-IN', {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit', hour12: true
      });
    },
    toggleBookings(user) {
      this.expandedUserId = this.expandedUserId === user.id ? null : user.id;
    },
    handleSearch() {
      this.applyFilters();
    },
    handleRoleFilter() {
      this.applyFilters();
    },
    applyFilters() {
      let filtered = this.users;
      if (this.searchQuery.trim()) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(user =>
          user.full_name.toLowerCase().includes(query) ||
          user.email.toLowerCase().includes(query)
        );
      }
      
      if (this.roleFilter) {
        filtered = filtered.filter(user =>
          user.role.toLowerCase() === this.roleFilter.toLowerCase()
        );
      }
      
      this.filteredUsers = filtered;
    },
    async fetchUsers() {
      try {
        const token = localStorage.getItem('accessToken');
        const res = await this.$axios.get("http://127.0.0.1:5000/api/users/details", {
          headers: { Authorization: `Bearer ${token}` },
        });
        this.users = res.data;
        this.filteredUsers = this.users;
      } catch (err) {
        console.error("Error fetching user data:", err);
        if (err.response && err.response.status === 401) {
          this.$emit('switchView', 'Home'); 
        }
      }
    },
    async deleteUser(id) {
      if (confirm("Are you sure you want to delete this user and all associated bookings?")) {
        try {
          const token = localStorage.getItem('accessToken');
          await this.$axios.delete(`http://127.0.0.1:5000/api/users/${id}`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          await this.fetchUsers();
          this.expandedUserId = null;
        } catch (err) {
          console.error("Error deleting user:", err);
          const errorMsg = err.response?.data?.message || "Failed to delete user. Check server status.";
          alert(errorMsg);
        }
      }
    },

    logout(force = false) {
      localStorage.removeItem('accessToken');
      delete axios.defaults.headers.common['Authorization'];
      
      axios.post("http://127.0.0.1:5000/api/logout", {})
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
.admin-dashboard.manage-users-page {
  position: relative;
  min-height: 100vh;
  background: url("@/assets/car-bg.jpg") no-repeat center center;
  background-size: cover;
  background-attachment: fixed;
  display: flex;
  flex-direction: column;
}
.admin-navbar {
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
  background: rgba(10, 20, 30, 0.65);
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
.search-filter-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.search-container {
  flex: 1;
  min-width: 300px;
}

.search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 16px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 42px;
  background: rgba(255, 255, 255, 0.08);
  border: 1.5px solid rgba(52, 152, 219, 0.3);
  border-radius: 12px;
  color: white;
  font-size: 0.9rem;
  outline: none;
  transition: all 0.3s ease;
  font-weight: 500;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.search-input:focus {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(52, 152, 219, 0.6);
  box-shadow: 0 0 20px rgba(52, 152, 219, 0.2);
}

.filter-controls {
  display: flex;
  gap: 10px;
}

.role-filter {
  background: rgba(255, 255, 255, 0.08);
  border: 1.5px solid rgba(52, 152, 219, 0.3);
  color: white;
  padding: 12px 16px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  outline: none;
  font-size: 0.9rem;
}

.role-filter:hover {
  border-color: rgba(52, 152, 219, 0.6);
  background: rgba(255, 255, 255, 0.12);
}

.role-filter:focus {
  border-color: rgba(52, 152, 219, 0.8);
  box-shadow: 0 0 15px rgba(52, 152, 219, 0.2);
}

.role-filter option {
  background: #2c3e50;
  color: white;
}
.results-info {
  margin-bottom: 20px;
  padding: 10px 16px;
  background: rgba(52, 152, 219, 0.1);
  border-left: 3px solid rgba(52, 152, 219, 0.6);
  border-radius: 6px;
  display: inline-block;
}

.result-count {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  font-weight: 600;
}
.table-section {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  margin-bottom: 40px;
  transition: all 0.3s ease;
}

.table-section:hover {
  border-color: rgba(255, 255, 255, 0.25);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.3);
}

.card-header {
  background: rgba(0, 0, 0, 0.2);
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header h3 {
  margin: 0;
  color: white;
  font-size: 1.2rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10px;
}

.table-container {
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  color: white;
}

.users-table thead {
  background: rgba(0, 0, 0, 0.3);
  border-bottom: 2px solid rgba(52, 152, 219, 0.3);
}

.users-table th {
  padding: 16px 20px;
  text-align: left;
  font-weight: 700;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: rgba(255, 255, 255, 0.9);
}

.users-table td {
  padding: 14px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 0.9rem;
}

.users-table tbody tr {
  transition: background 0.2s ease;
}

.users-table tbody tr:hover {
  background: rgba(52, 152, 219, 0.1);
}

.user-name-cell {
  font-weight: 700;
  color: #87ceeb;
}

.user-email {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.85rem;
}

.role-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.role-badge.user {
  background: rgba(52, 152, 219, 0.3);
  color: #3498db;
}

.role-badge.admin {
  background: rgba(255, 165, 0, 0.3);
  color: #ffa500;
}

.revenue-text {
  color: #2ecc71;
  font-weight: 700;
}

.action-column {
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn-action {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.btn-action.history {
  background: rgba(52, 152, 219, 0.3);
  color: #3498db;
}

.btn-action.history:hover {
  background: rgba(52, 152, 219, 0.6);
  transform: scale(1.1);
}

.btn-action.delete {
  background: rgba(220, 53, 69, 0.3);
  color: #dc3545;
}

.btn-action.delete:hover {
  background: rgba(220, 53, 69, 0.6);
  transform: scale(1.1);
}
.empty-state td {
  text-align: center;
  padding: 40px 20px !important;
  color: rgba(255, 255, 255, 0.6);
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 15px;
  display: block;
  opacity: 0.5;
}
.history-expansion-row td {
  border-top: 2px solid rgba(52, 152, 219, 0.3) !important;
  background-color: rgba(20, 30, 40, 0.9) !important;
  padding: 0 !important;
}

.booking-history-section {
  width: 100%;
  padding: 30px;
}

.history-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #3498db;
  margin-bottom: 5px;
  text-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
}

.history-count {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 20px;
  font-weight: 600;
}

.history-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.booking-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(52, 152, 219, 0.2);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.booking-card:hover {
  border-color: rgba(52, 152, 219, 0.5);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
}

.booking-header {
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.2), rgba(46, 204, 113, 0.1));
  padding: 12px 16px;
  border-bottom: 1px solid rgba(52, 152, 219, 0.2);
  display: flex;
  align-items: center;
  gap: 10px;
  color: #3498db;
  font-weight: 700;
}

.lot-info {
  color: white;
  font-weight: 600;
}

.booking-details {
  padding: 16px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 0.9rem;
}

.detail-row:last-child {
  margin-bottom: 0;
}

.detail-label {
  color: rgba(255, 255, 255, 0.7);
  font-weight: 600;
  display: flex;
  align-items: center;
}

.detail-value {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

.amount-row {
  background: rgba(46, 204, 113, 0.1);
  padding: 10px 12px;
  border-radius: 8px;
  margin-top: 8px;
}

.detail-value.amount {
  color: #2ecc71;
  font-weight: 700;
  font-size: 1.1rem;
}

.no-bookings {
  color: rgba(255, 255, 255, 0.6);
  text-align: center;
  padding: 30px;
  font-style: italic;
}
@media (max-width: 1200px) {
  .navbar-menu {
    gap: 25px;
    margin-left: 40px;
  }

  .users-table th,
  .users-table td {
    padding: 12px 15px;
    font-size: 0.85rem;
  }

  .search-filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-container {
    min-width: auto;
  }

  .role-filter {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .navbar-content {
    flex-wrap: wrap;
    padding: 0 15px;
  }

  .navbar-menu {
    order: 3;
    width: 100%;
    margin-left: 0;
    margin-top: 12px;
    gap: 12px;
  }

  .nav-item {
    flex: 1;
    justify-content: center;
    font-size: 0.8rem;
    padding: 8px 10px;
  }

  .nav-item i {
    display: none;
  }

  .navbar-user {
    width: 100%;
    margin-left: 0;
    margin-top: 12px;
    gap: 10px;
  }

  .user-name {
    display: none;
  }

  .btn-logout {
    width: 100%;
    justify-content: center;
  }

  .dashboard-wrapper {
    padding: 25px 12px;
  }

  .welcome-title {
    font-size: 2rem;
  }

  .welcome-subtitle {
    font-size: 0.95rem;
  }

  .search-filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-container {
    min-width: auto;
  }

  .role-filter {
    width: 100%;
  }

  .users-table {
    font-size: 0.8rem;
  }

  .users-table th,
  .users-table td {
    padding: 10px 12px;
  }

  .btn-action {
    width: 32px;
    height: 32px;
    font-size: 0.8rem;
  }

  .history-grid {
    grid-template-columns: 1fr;
  }

  .booking-history-section {
    padding: 20px;
  }

  .history-title {
    font-size: 1.2rem;
  }
}

@media (max-width: 480px) {
  .navbar-brand {
    font-size: 1.2rem;
  }

  .welcome-title {
    font-size: 1.6rem;
  }

  .dashboard-wrapper {
    padding: 20px 10px;
  }

  .users-table th,
  .users-table td {
    padding: 8px 10px;
    font-size: 0.75rem;
  }

  .search-input {
    font-size: 0.85rem;
    padding: 10px 14px 10px 38px;
  }

  .role-filter {
    font-size: 0.85rem;
    padding: 10px 12px;
  }

  .action-column {
    gap: 4px;
  }

  .btn-action {
    width: 28px;
    height: 28px;
    font-size: 0.7rem;
  }

  .history-grid {
    grid-template-columns: 1fr;
  }

  .booking-header {
    font-size: 0.85rem;
    padding: 10px 12px;
  }

  .booking-details {
    padding: 12px;
  }

  .detail-row {
    font-size: 0.8rem;
    margin-bottom: 8px;
  }
}
</style>