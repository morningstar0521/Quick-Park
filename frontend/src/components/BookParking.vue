<template>
  <div class="book-parking-page">
    <div class="overlay"></div>
    <nav class="book-navbar">
      <div class="navbar-content">
        <div class="navbar-brand">
          <span>Quick Park</span>
        </div>
        <div class="navbar-menu">
          <a class="nav-item" @click="$emit('switchView','UserDashboard')">
            <i class="fas fa-home me-2"></i>Dashboard
          </a>
          <a class="nav-item active" @click.prevent>
            <i class="fas fa-car me-2"></i>Book Parking
          </a>
          <a class="nav-item" @click="$emit('switchView','UserBookingHistory')">
            <i class="fas fa-history me-2"></i>History
          </a>
          <a class="nav-item" @click="$emit('switchView','UserReports')">
            <i class="fas fa-chart-bar me-2"></i>Reports
          </a>
        </div>
        <div class="navbar-user">
          <span class="user-name"><i class="fas fa-user-circle me-2"></i>{{ userDetails.full_name }}</span>
          <button class="btn-profile" @click="$emit('switchView','UserProfile')" title="View Profile">
            <i class="fas fa-user"></i>
          </button>
          <button class="btn-logout" @click="logout">
            <i class="fas fa-sign-out-alt me-1"></i>Logout
          </button>
        </div>
      </div>
    </nav>

    <div class="dashboard-content">
      <div class="welcome-section">
        <h1 class="welcome-title">Book Your Parking</h1>
        <p class="welcome-subtitle">Find and reserve the perfect parking spot</p>
      </div>

      <div v-if="currentView === 'lots'" class="lots-view">
        <div class="controls-section">
          <div class="search-filter-bar">
            <div class="search-box">
              <i class="fas fa-search"></i>
              <input type="text" placeholder="Search by location or name..." v-model="searchQuery" class="search-input">
            </div>
            <div class="filter-controls">
              <select v-model="selectedType" class="filter-select">
                <option value="">All Types</option>
                <option value="Commercial">Commercial</option>
                <option value="Mall">Mall</option>
                <option value="Residential">Residential</option>
              </select>
            </div>
          </div>
        </div>
      
        <div v-if="hasActiveBooking" class="active-booking-alert">
          <div class="alert-card">
            <div class="alert-icon">
              <i class="fas fa-exclamation-circle"></i>
            </div>
            <div class="alert-content">
              <h4 class="alert-title">Active Booking In Progress</h4>
              <p class="alert-message">You are currently parked at <strong>{{ activeBooking.lot_name }}</strong> (Spot #{{ activeBooking.spot_number }})</p>
              <p class="alert-instruction">Please park out from your current location before booking a new spot.</p>
              <button class="btn-alert-action" @click="$emit('switchView', 'UserDashboard')">
                <i class="fas fa-arrow-right me-1"></i>Go to Dashboard
              </button>
            </div>
          </div>
        </div>
        
        <div v-if="loading" class="loading-state">
          <div class="spinner">
            <i class="fas fa-spinner fa-spin"></i>
          </div>
          <p>Loading parking lots...</p>
        </div>
        
        <div v-else-if="parkingLots.length === 0" class="empty-state">
          <i class="fas fa-parking"></i>
          <p>No parking lots available at the moment</p>
        </div>
        
        <div v-else class="parking-lots-grid">
          <div v-for="lot in filteredParkingLots" :key="lot.id" class="parking-lot-card" :class="{ 'disabled': hasActiveBooking }">
            <div class="lot-card-header">
              <div class="lot-title-area">
                <h3 class="lot-name">{{ lot.name }}</h3>
                <span class="lot-status" :class="{ 'available': lot.availableSpots > 0, 'full': lot.availableSpots === 0 }">
                  {{ lot.availableSpots > 0 ? `${lot.availableSpots} Available` : 'Full' }}
                </span>
              </div>
            </div>
            
            <div class="lot-card-details">
              <div class="detail-group">
                <div class="detail-item">
                  <i class="fas fa-map-marker-alt"></i>
                  <div class="detail-content">
                    <span class="detail-label">Location</span>
                    <span class="detail-value">{{ lot.address }}, {{ lot.city }} {{ lot.pincode }}</span>
                  </div>
                </div>
                
                <div class="detail-item">
                  <i class="fas fa-tag"></i>
                  <div class="detail-content">
                    <span class="detail-label">Type</span>
                    <span class="detail-value">{{ lot.parkingType }}</span>
                  </div>
                </div>

                <div class="detail-item rate-highlight">
                  <i class="fas fa-rupee-sign"></i>
                  <div class="detail-content">
                    <span class="detail-label">Hourly Rate</span>
                    <span class="detail-value">₹{{ lot.ratePerHour }}/hour</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="lot-stats-section">
              <div class="stat-card available">
                <div class="stat-card-inner">
                  <div class="stat-icon-wrapper">
                    <i class="fas fa-check-circle"></i>
                  </div>
                  <div class="stat-content">
                    <span class="stat-label">Available</span>
                    <span class="stat-value">{{ lot.availableSpots }}</span>
                    <span class="stat-subtitle">Ready to book</span>
                  </div>
                </div>
                <div class="stat-progress-bar">
                  <div class="progress" :style="{ width: (lot.availableSpots / lot.totalSpots * 100) + '%' }"></div>
                </div>
              </div>

              <div class="stat-card occupied">
                <div class="stat-card-inner">
                  <div class="stat-icon-wrapper">
                    <i class="fas fa-times-circle"></i>
                  </div>
                  <div class="stat-content">
                    <span class="stat-label">Occupied</span>
                    <span class="stat-value">{{ lot.totalSpots - lot.availableSpots }}</span>
                    <span class="stat-subtitle">In use</span>
                  </div>
                </div>
                <div class="stat-progress-bar">
                  <div class="progress" :style="{ width: ((lot.totalSpots - lot.availableSpots) / lot.totalSpots * 100) + '%' }"></div>
                </div>
              </div>
            </div>
            
            <div class="lot-card-actions">
              <button 
                class="btn btn-view-layout" 
                @click="viewLotLayout(lot)"
                :disabled="lot.availableSpots === 0 || hasActiveBooking">
                <i class="fas fa-th-large me-2"></i>View Layout
              </button>
              <button 
                class="btn btn-book-now" 
                @click="bookParkingLot(lot)"
                :disabled="lot.availableSpots === 0 || hasActiveBooking">
                <i class="fas fa-check me-2"></i>Book Now
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="currentView === 'layout'" class="layout-view">
        <div class="layout-header">
          <button class="btn-back-layout" @click="currentView = 'lots'">
            <i class="fas fa-arrow-left me-2"></i>Back to Lots
          </button>
          <div class="layout-title-section">
            <h1 class="layout-title">{{ selectedLot.name }}</h1>
            <p class="layout-subtitle">{{ selectedLot.address }}, {{ selectedLot.city }}</p>
          </div>
        </div>

        <div class="layout-stats-card">
          <div class="stats-grid">
            <div class="stat-card total-spots">
              <span class="stat-icon"><i class="fas fa-th"></i></span>
              <div class="stat-details">
                <span class="stat-label">Total Spots</span>
                <span class="stat-value">{{ parkingSpots.length }}</span>
              </div>
            </div>
            <div class="stat-card available-spots">
              <span class="stat-icon"><i class="fas fa-check-circle"></i></span>
              <div class="stat-details">
                <span class="stat-label">Available</span>
                <span class="stat-value">{{ availableSpotsCount }}</span>
              </div>
            </div>
            <div class="stat-card occupied-spots">
              <span class="stat-icon"><i class="fas fa-times-circle"></i></span>
              <div class="stat-details">
                <span class="stat-label">Occupied</span>
                <span class="stat-value">{{ bookedSpotsCount }}</span>
              </div>
            </div>
            <div class="stat-card rate-info">
              <span class="stat-icon"><i class="fas fa-rupee-sign"></i></span>
              <div class="stat-details">
                <span class="stat-label">Rate</span>
                <span class="stat-value">₹{{ selectedLot.ratePerHour }}/h</span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="layoutLoading" class="loading-state">
          <div class="spinner">
            <i class="fas fa-spinner fa-spin"></i>
          </div>
          <p>Loading parking layout...</p>
        </div>

        <div v-else class="layout-content">
          <div class="parking-grid-section">
            <div class="grid-header">
              <h3 class="grid-title">Parking Layout</h3>
              <p class="grid-subtitle">View all available and booked spots</p>
            </div>

            <div class="parking-grid horizontal-grid">
              <div 
                v-for="spot in parkingSpots" 
                :key="spot.id"
                :class="['parking-spot-item', { 'available': spot.is_available, 'booked': !spot.is_available }]"
                :title="getSpotTooltip(spot)">
                <div class="spot-content">
                  <div class="spot-number">{{ spot.spot_number }}</div>
                  <div class="spot-icon">
                    <i v-if="spot.is_available" class="fas fa-check-circle"></i>
                    <i v-else class="fas fa-times-circle"></i>
                  </div>
                </div>
              </div>
            </div>

            <div class="layout-legend">
              <div class="legend-item">
                <div class="legend-color available"></div>
                <span>Available Spot</span>
              </div>
              <div class="legend-item">
                <div class="legend-color booked"></div>
                <span>Booked Spot</span>
              </div>
            </div>
          </div>

          <div class="auto-assignment-card">
            <div class="card-icon">
              <i class="fas fa-magic"></i>
            </div>
            <div class="card-content">
              <h4 class="card-title">Auto-Assignment</h4>
              <p class="card-text">Our intelligent system automatically assigns the best available spot for you. No manual selection needed!</p>
              <div class="available-info">
                <i class="fas fa-parking"></i>
                <span>{{ availableSpotsCount }} spots ready to book</span>
              </div>
            </div>
          </div>

          <div class="layout-actions">
            <button 
              class="btn-proceed-booking" 
              @click="proceedToBooking"
              :disabled="availableSpotsCount === 0">
              <i class="fas fa-arrow-right me-2"></i>Continue to Booking
            </button>
          </div>
        </div>
      </div>

      <div v-if="currentView === 'booking'" class="booking-view">
        <div class="booking-header">
          <button class="btn-back-booking" @click="currentView = 'layout'">
            <i class="fas fa-arrow-left me-2"></i>Back to Layout
          </button>
          <div class="booking-title-section">
            <h1 class="booking-title">Complete Your Booking</h1>
            <p class="booking-subtitle">Review details and confirm your parking reservation</p>
          </div>
        </div>

        <div class="booking-content">
          <div class="booking-summary-card">
            <h3 class="summary-title">Parking Location</h3>
            <div class="summary-details">
              <div class="summary-item">
                <span class="summary-label">Lot Name</span>
                <span class="summary-value">{{ selectedLot.name }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">Address</span>
                <span class="summary-value">{{ selectedLot.address }}, {{ selectedLot.city }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">Rate</span>
                <span class="summary-value rate-display">₹{{ selectedLot.ratePerHour }}/hour</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">Spot Assignment</span>
                <span class="summary-value">Auto-Assigned</span>
              </div>
            </div>
          </div>

          <div class="booking-form-section">
            <form @submit.prevent="submitBooking" class="booking-form">
              <div class="form-fields-row">
                <div class="form-field hidden-field">
                  <label for="lotId">Parking Lot ID</label>
                  <input id="lotId" :value="selectedLot.id" type="text" class="form-input" disabled />
                </div>
                <div class="form-field hidden-field">
                  <label for="userId">User ID</label>
                  <input id="userId" :value="userDetails.id" type="text" class="form-input" disabled />
                </div>
              </div>

              <div class="form-fields-row">
                <div class="form-field full-width">
                  <label for="userName"><i class="fas fa-user me-2"></i>Your Name</label>
                  <input id="userName" :value="userDetails.full_name" type="text" class="form-input" disabled />
                </div>
              </div>

              <div class="form-fields-row">
                <div class="form-field full-width">
                  <label for="vehicleNumber"><i class="fas fa-car me-2"></i>Vehicle Number <span class="required">*</span></label>
                  <input 
                    id="vehicleNumber" 
                    v-model="bookingForm.vehicleNumber" 
                    type="text" 
                    class="form-input" 
                    placeholder="e.g., MH01AB1234"
                    required />
                </div>
              </div>

              <div class="cost-summary-section">
                <h4 class="cost-title"><i class="fas fa-calculator me-2"></i>Cost Summary</h4>
                <div class="cost-breakdown">
                  <div class="cost-row">
                    <span class="cost-label">Hourly Rate</span>
                    <span class="cost-value">₹{{ selectedLot.ratePerHour }}</span>
                  </div>
                  <div class="cost-row">
                    <span class="cost-label">Minimum Duration</span>
                    <span class="cost-value">1 hour</span>
                  </div>
                  <div class="cost-row total-row">
                    <span class="cost-label">Estimated Cost</span>
                    <span class="cost-value">₹{{ selectedLot.ratePerHour }}</span>
                  </div>
                </div>
                <p class="cost-note">
                  <i class="fas fa-info-circle me-1"></i>
                  Final cost calculated when you complete your parking session.
                </p>
              </div>

              <div class="booking-actions">
                <button type="button" class="btn-back-form" @click="currentView = 'layout'">
                  <i class="fas fa-arrow-left me-2"></i>Back
                </button>
                <button type="submit" class="btn-confirm-booking" :disabled="!bookingForm.vehicleNumber">
                  <i class="fas fa-check-circle me-2"></i>Confirm Booking
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "BookParking",
  props: {
    userDetails: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      currentView: 'lots', 
      loading: false,
      layoutLoading: false,
      parkingLots: [],
      selectedLot: null,
      parkingSpots: [],
      selectedSpot: null,
      bookingForm: {
        vehicleNumber: ''
      },
      hasActiveBooking: false,
      activeBooking: null,
      searchQuery: '',
      selectedType: ''
    };
  },
  computed: {
    availableSpotsCount() {
      return this.parkingSpots.filter(spot => spot.is_available).length;
    },
    bookedSpotsCount() {
      return this.parkingSpots.filter(spot => !spot.is_available).length;
    },
    filteredParkingLots() {
      let filtered = this.parkingLots;
      
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(lot => 
          lot.name.toLowerCase().includes(query) ||
          lot.address.toLowerCase().includes(query) ||
          lot.city.toLowerCase().includes(query)
        );
      }
      
      if (this.selectedType) {
        filtered = filtered.filter(lot => lot.parkingType === this.selectedType);
      }
      
      return filtered;
    }
  },
  created() {
    this.checkActiveBooking();
    this.fetchParkingLots();
  },
  methods: {
    async checkActiveBooking() {
      try {
        const response = await this.$axios.get("http://127.0.0.1:5000/api/user/bookings");
        if (response.data.ok) {
          const activeBookings = response.data.bookings.filter(booking => booking.is_active);
          if (activeBookings.length > 0) {
            this.hasActiveBooking = true;
            this.activeBooking = activeBookings[0];
          }
        }
      } catch (err) {
        console.error("Error checking active booking:", err);
      }
    },

    async fetchParkingLots() {
      this.loading = true;
      try {
        const response = await this.$axios.get("http://127.0.0.1:5000/api/user/parking-lots");
        if (response.data.ok) {
          this.parkingLots = response.data.lots;
        } else {
          console.error("Error fetching parking lots:", response.data.message);
        }
      } catch (err) {
        console.error("Error fetching parking lots:", err);
        if (err.response && err.response.status === 401) {
          this.logout(true);
        }
      } finally {
        this.loading = false;
      }
    },

    async viewLotLayout(lot) {
      this.selectedLot = lot;
      this.currentView = 'layout';
      this.layoutLoading = true;
      this.selectedSpot = null; 
      
      try {
        const response = await this.$axios.get(`http://127.0.0.1:5000/api/user/parking-lots/${lot.id}/spots`);
        console.log("Parking spots response:", response.data);
        if (response.data.ok) {
          this.parkingSpots = response.data.spots;
          console.log("Parking spots loaded:", this.parkingSpots);
        } else {
          console.error("Error fetching parking spots:", response.data.message);
        }
      } catch (err) {
        console.error("Error fetching parking spots:", err);
        if (err.response && err.response.status === 401) {
          this.logout(true);
        }
      } finally {
        this.layoutLoading = false;
      }
    },

    selectSpot(spot) {
      if (spot.is_available) {
        this.selectedSpot = spot;
      }
    },

    getSpotTooltip(spot) {
      if (spot.is_available) {
        return `Spot ${spot.spot_number}: Available - Click to select`;
      }
      return `Spot ${spot.spot_number}: Booked`;
    },

    bookParkingLot(lot) {
      this.viewLotLayout(lot);
    },

    proceedToBooking() {
      if (this.availableSpotsCount > 0) {
        this.bookingForm.vehicleNumber = ''; 
        this.currentView = 'booking';
      }
    },

    async submitBooking() {
      if (!this.bookingForm.vehicleNumber.trim()) {
        alert("Please enter your vehicle number");
        return;
      }

      const confirmMessage = `
        🚗 BOOKING CONFIRMATION 🚗
        
        Parking Lot: ${this.selectedLot.name}
        Vehicle: ${this.bookingForm.vehicleNumber.trim()}
        Rate: ₹${this.selectedLot.ratePerHour}/hour
        
        ⚠️ IMPORTANT:
        • You will be charged a minimum of ₹${this.selectedLot.ratePerHour} (1 hour)
        • Final cost will be calculated when you park out
        • Payment will be processed automatically
        • Spot will be auto-assigned by our system
        
        Do you want to proceed with this booking?
      `;

      if (!confirm(confirmMessage)) {
        return;
      }

      try {
        const bookingData = {
          lot_id: this.selectedLot.id,
          vehicle_number: this.bookingForm.vehicleNumber.trim()
        };

        const response = await this.$axios.post("http://127.0.0.1:5000/api/user/bookings", bookingData);
        
        if (response.data.ok) {
          const successMessage = `
            ✅ BOOKING CONFIRMED! ✅
            
            Your parking spot has been auto-assigned:
            • Spot: #${response.data.booking.spot_number}
            • Location: ${this.selectedLot.name}
            • Vehicle: ${this.bookingForm.vehicleNumber.trim()}
            
            You can now view your active booking on the Dashboard.
            Remember to park out when you're done!
          `;
          alert(successMessage);
          
          this.$emit('bookingSuccess');
          this.$emit('switchView', 'UserDashboard');
        } else {
          alert(`Booking failed: ${response.data.message}`);
        }
      } catch (err) {
        console.error("Error creating booking:", err);
        if (err.response && err.response.status === 401) {
          this.logout(true);
        } else {
          const errorMsg = err.response?.data?.message || "Failed to create booking. Please try again.";
          alert(errorMsg);
        }
      }
    },

    showLotSummary() {
      alert("Lot Summary functionality coming soon!");
    },

    showProfile() {
      this.$emit('switchView', 'UserDashboard');
    },

    logout(force = false) {
      localStorage.removeItem('accessToken');
      delete this.$axios.defaults.headers.common['Authorization'];
      
      this.$axios.post("http://127.0.0.1:5000/api/logout", {})
        .finally(() => {
          if (force) {
            alert("Session expired. Please log in again.");
          }
          this.$emit("switchView", "Home");
        });
    }
  }
};
</script>

<style scoped>
.book-parking-page {
  position: relative;
  min-height: 100vh;
  background: url("@/assets/user-bg.jpg") no-repeat center center;
  background-size: cover;
  background-attachment: fixed;
  display: flex;
  flex-direction: column;
  color: white;
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

.book-navbar {
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
.dashboard-content {
  position: relative;
  z-index: 2;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  padding: 40px 20px;
  overflow-y: auto;
}
.welcome-section {
  text-align: center;
  margin-bottom: 40px;
  width: 100%;
  max-width: 1400px;
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
.lots-view {
  width: 100%;
  max-width: 1400px;
  animation: slideDown 0.6s ease;
}

.controls-section {
  margin-bottom: 30px;
}

.search-filter-bar {
  display: flex;
  gap: 16px;
  align-items: center;
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  padding: 18px 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.search-box {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  background: rgba(0, 0, 0, 0.3);
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  transition: all 0.3s ease;
}

.search-box:focus-within {
  border-color: #3498db;
  background: rgba(52, 152, 219, 0.1);
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.search-box i {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.95rem;
}

.search-input {
  background: none;
  border: none;
  color: white;
  font-size: 0.95rem;
  width: 100%;
  outline: none;
  font-family: inherit;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.filter-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.filter-select {
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(0, 0, 0, 0.3);
  color: white;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
}

.filter-select:hover,
.filter-select:focus {
  border-color: #3498db;
  background: rgba(52, 152, 219, 0.1);
  outline: none;
}

.filter-select option {
  background: #1a252f;
  color: white;
}
.active-booking-alert {
  margin-bottom: 30px;
  animation: slideDown 0.6s ease;
}

.alert-card {
  display: flex;
  gap: 20px;
  padding: 24px;
  background: rgba(220, 53, 69, 0.1);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(220, 53, 69, 0.3);
  border-radius: 12px;
  border-left: 4px solid #dc3545;
  box-shadow: 0 8px 32px rgba(220, 53, 69, 0.15);
}

.alert-icon {
  font-size: 1.8rem;
  color: #dc3545;
  min-width: 50px;
  display: flex;
  align-items: flex-start;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: white;
  margin-bottom: 8px;
}

.alert-message,
.alert-instruction {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: 6px;
  line-height: 1.5;
}

.btn-alert-action {
  display: inline-block;
  margin-top: 12px;
  padding: 10px 18px;
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.btn-alert-action:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(220, 53, 69, 0.3);
}
.loading-state, .empty-state {
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  padding: 60px 20px;
  width: 100%;
}

.spinner {
  font-size: 3rem;
  color: #3498db;
  margin-bottom: 20px;
  display: inline-block;
}

.loading-state p,
.empty-state p {
  font-size: 1.1rem;
  margin: 0;
}

.empty-state i {
  font-size: 3.5rem;
  color: rgba(255, 255, 255, 0.3);
  margin-bottom: 16px;
  display: block;
}
.parking-lots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 28px;
  width: 100%;
  margin-bottom: 30px;
}

.parking-lot-card {
  background: rgba(255, 255, 255, 0.07);
  backdrop-filter: blur(20px);
  border: 1.5px solid rgba(255, 255, 255, 0.15);
  border-radius: 18px;
  padding: 0;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.15);
  height: 100%;
}

.parking-lot-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.2) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.parking-lot-card::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #3498db, #2ecc71, #9b59b6);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.parking-lot-card:hover:not(.disabled) {
  transform: translateY(-10px);
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(52, 152, 219, 0.4);
  box-shadow: 0 20px 60px rgba(52, 152, 219, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.parking-lot-card:hover:not(.disabled)::before {
  opacity: 1;
}

.parking-lot-card:hover:not(.disabled)::after {
  opacity: 1;
}

.parking-lot-card.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

.lot-card-header {
  margin-bottom: 12px;
  padding: 20px 24px 14px 24px;
  border-bottom: 1.5px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.1) 0%, rgba(255, 255, 255, 0.02) 100%);
}

.lot-title-area {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.lot-name {
  font-size: 1.4rem;
  font-weight: 900;
  color: white;
  margin: 0;
  text-align: left;
  flex: 1;
  letter-spacing: -0.5px;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
  line-height: 1.2;
}

.lot-status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 1px;
  white-space: nowrap;
  backdrop-filter: blur(10px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.18);
  border: 1.5px solid rgba(255, 255, 255, 0.2);
}

.lot-status::before {
  content: '';
  width: 10px;
  height: 10px;
  border-radius: 50%;
  animation: pulse 2.5s infinite;
}

.lot-status.available {
  background: linear-gradient(135deg, rgba(46, 204, 113, 0.4), rgba(46, 204, 113, 0.2));
  color: #2ecc71;
  border: 1.5px solid rgba(46, 204, 113, 0.7);
  box-shadow: 0 0 16px rgba(46, 204, 113, 0.3), 0 6px 16px rgba(0, 0, 0, 0.18);
}

.lot-status.available::before {
  background: #2ecc71;
}

.lot-status.full {
  background: linear-gradient(135deg, rgba(220, 53, 69, 0.4), rgba(220, 53, 69, 0.2));
  color: #dc3545;
  border: 1.5px solid rgba(220, 53, 69, 0.7);
  box-shadow: 0 0 16px rgba(220, 53, 69, 0.3), 0 6px 16px rgba(0, 0, 0, 0.18);
}

.lot-status.full::before {
  background: #dc3545;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.3);
  }
}

.lot-card-details {
  margin-bottom: 12px;
  flex: 1;
  padding: 12px 24px;
  background: rgba(255, 255, 255, 0.02);
}

.detail-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  font-size: 0.9rem;
  padding: 8px 0;
  transition: all 0.3s ease;
}

.detail-item:hover {
  transform: translateX(2px);
}

.detail-item i {
  color: #3498db;
  margin-top: 2px;
  min-width: 18px;
  font-size: 1rem;
  flex-shrink: 0;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
  text-align: left;
  flex: 1;
}

.detail-label {
  font-size: 0.72rem;
  color: rgba(255, 255, 255, 0.68);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 800;
}

.detail-value {
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
  font-size: 0.92rem;
  line-height: 1.4;
  letter-spacing: -0.2px;
}

.detail-item.rate-highlight {
  background: linear-gradient(135deg, rgba(155, 89, 182, 0.35), rgba(155, 89, 182, 0.18));
  border: 2px solid rgba(155, 89, 182, 0.65);
  border-radius: 10px;
  padding: 12px;
  margin: 4px 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(155, 89, 182, 0.25);
}

.detail-item.rate-highlight:hover {
  background: linear-gradient(135deg, rgba(155, 89, 182, 0.45), rgba(155, 89, 182, 0.25));
  border-color: rgba(155, 89, 182, 0.85);
  transform: translateX(4px);
  box-shadow: 0 8px 20px rgba(155, 89, 182, 0.35);
}

.detail-item.rate-highlight i {
  color: #c77dff;
  font-weight: 900;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
}

.detail-item.rate-highlight .detail-label {
  color: #e0b0ff;
  font-weight: 960;
  letter-spacing: 0.6px;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.detail-item.rate-highlight .detail-value {
  color: #ffd6ff;
  font-weight: 950;
  font-size: 1.05rem;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
}

.lot-stats-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 18px;
  margin-bottom: 24px;
  padding: 20px 24px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.01));
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-card {
  padding: 18px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
  border-radius: 14px;
  border: 1.5px solid rgba(255, 255, 255, 0.14);
  text-align: left;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 14px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.18), inset 0 1px 1px rgba(255, 255, 255, 0.12);
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent);
  transition: left 0.6s ease;
  pointer-events: none;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25), inset 0 1px 1px rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.2);
}

.stat-card:hover::before {
  left: 100%;
}

.stat-card-inner {
  display: flex;
  align-items: center;
  gap: 16px;
  z-index: 1;
  position: relative;
}

.stat-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 13px;
  font-size: 1.6rem;
  font-weight: 900;
  flex-shrink: 0;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  border: 1.5px solid rgba(255, 255, 255, 0.25);
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.25);
}

.stat-card.available .stat-icon-wrapper {
  background: linear-gradient(135deg, rgba(46, 204, 113, 0.35), rgba(46, 204, 113, 0.15));
  color: #2ecc71;
  border: 1.5px solid rgba(46, 204, 113, 0.55);
  box-shadow: 0 0 20px rgba(46, 204, 113, 0.35), 0 6px 16px rgba(0, 0, 0, 0.2);
  text-shadow: 0 2px 4px rgba(46, 204, 113, 0.4);
}

.stat-card.occupied .stat-icon-wrapper {
  background: linear-gradient(135deg, rgba(220, 53, 69, 0.35), rgba(220, 53, 69, 0.15));
  color: #dc3545;
  border: 1.5px solid rgba(220, 53, 69, 0.55);
  box-shadow: 0 0 20px rgba(220, 53, 69, 0.35), 0 6px 16px rgba(0, 0, 0, 0.2);
  text-shadow: 0 2px 4px rgba(220, 53, 69, 0.4);
}

.stat-card.rate .stat-icon-wrapper {
  background: linear-gradient(135deg, rgba(155, 89, 182, 0.35), rgba(155, 89, 182, 0.15));
  color: #9b59b6;
  border: 1.5px solid rgba(155, 89, 182, 0.55);
  box-shadow: 0 0 20px rgba(155, 89, 182, 0.35), 0 6px 16px rgba(0, 0, 0, 0.2);
  text-shadow: 0 2px 4px rgba(155, 89, 182, 0.4);
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 7px;
  flex: 1;
  min-width: 0;
}

.stat-label {
  display: block;
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.85);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  font-weight: 960;
  line-height: 1.2;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.stat-value {
  display: block;
  font-size: 1.75rem;
  font-weight: 950;
  color: white;
  letter-spacing: -1px;
  text-shadow: 0 3px 8px rgba(0, 0, 0, 0.35);
  line-height: 1;
}

.stat-card.available .stat-value {
  color: #2ecc71;
  text-shadow: 0 3px 8px rgba(46, 204, 113, 0.4);
}

.stat-card.occupied .stat-value {
  color: #dc3545;
  text-shadow: 0 3px 8px rgba(220, 53, 69, 0.4);
}

.stat-card.rate .stat-value {
  color: #9b59b6;
  text-shadow: 0 3px 8px rgba(155, 89, 182, 0.4);
}

.stat-subtitle {
  display: block;
  font-size: 0.73rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 700;
  letter-spacing: 0.3px;
  line-height: 1.3;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.stat-progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  margin-top: 10px;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.25);
}

.stat-card.available .stat-progress-bar .progress {
  background: linear-gradient(90deg, #2ecc71 0%, #27ae60 100%);
  box-shadow: 0 0 12px rgba(46, 204, 113, 0.5);
}

.stat-card.occupied .stat-progress-bar .progress {
  background: linear-gradient(90deg, #dc3545 0%, #c82333 100%);
  box-shadow: 0 0 12px rgba(220, 53, 69, 0.5);
}

.stat-progress-bar .progress {
  height: 100%;
  border-radius: 3px;
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 12px rgba(52, 152, 219, 0.4);
}

.stat-card.available {
  border-left: 5px solid #2ecc71;
  background: linear-gradient(135deg, rgba(46, 204, 113, 0.14), rgba(46, 204, 113, 0.05));
}

.stat-card.occupied {
  border-left: 5px solid #dc3545;
  background: linear-gradient(135deg, rgba(220, 53, 69, 0.14), rgba(220, 53, 69, 0.05));
}

.stat-card.rate {
  border-left: 5px solid #9b59b6;
  background: linear-gradient(135deg, rgba(155, 89, 182, 0.14), rgba(155, 89, 182, 0.05));
}

.lot-card-actions {
  display: flex;
  gap: 12px;
  width: 100%;
  padding: 18px 24px 24px 24px;
}

.btn {
  flex: 1;
  padding: 13px 16px;
  border: none;
  border-radius: 11px;
  font-weight: 800;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  white-space: nowrap;
  position: relative;
  overflow: hidden;
  letter-spacing: 0.3px;
}

.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.15);
  transition: left 0.4s ease;
}

.btn:hover:not(:disabled)::before {
  left: 100%;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-view-layout {
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.35), rgba(52, 152, 219, 0.18));
  border: 1.5px solid rgba(52, 152, 219, 0.65);
  color: #3498db;
  box-shadow: 0 4px 14px rgba(52, 152, 219, 0.18);
}

.btn-view-layout:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.55), rgba(52, 152, 219, 0.35));
  border-color: rgba(52, 152, 219, 1);
  transform: translateY(-3px);
  box-shadow: 0 10px 24px rgba(52, 152, 219, 0.35);
  color: white;
}

.btn-book-now {
  background: linear-gradient(135deg, #3498db, #2980b9);
  border: none;
  color: white;
  box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
  font-weight: 900;
  letter-spacing: 0.5px;
}

.btn-book-now:hover:not(:disabled) {
  background: linear-gradient(135deg, #2980b9, #1e5a7a);
  transform: translateY(-3px);
  box-shadow: 0 12px 32px rgba(52, 152, 219, 0.5);
}

.btn-book-now:active:not(:disabled) {
  transform: translateY(-1px);
}
.layout-view {
  width: 100%;
  max-width: 1200px;
  animation: slideDown 0.6s ease;
}

.layout-header {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 30px;
}

.btn-back-layout {
  padding: 10px 18px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.btn-back-layout:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.layout-title-section {
  flex: 1;
}

.layout-title {
  font-size: 2.2rem;
  font-weight: 800;
  color: white;
  margin: 0 0 8px 0;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.layout-subtitle {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.layout-stats-card {
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  padding: 24px;
  margin-bottom: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.stat-icon {
  font-size: 1.8rem;
  min-width: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-card.total-spots .stat-icon {
  color: #3498db;
}

.stat-card.available-spots .stat-icon {
  color: #2ecc71;
}

.stat-card.occupied-spots .stat-icon {
  color: #dc3545;
}

.stat-card.rate-info .stat-icon {
  color: #9b59b6;
}

.stat-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-label {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
}

.layout-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.parking-grid-section {
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  padding: 28px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.grid-header {
  margin-bottom: 24px;
  text-align: center;
}

.grid-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: white;
  display: block;
  margin-bottom: 8px;
}

.grid-subtitle {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.6);
  display: block;
}

.parking-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(60px, 1fr));
  gap: 14px;
  margin-bottom: 24px;
}

.parking-spot-item {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px;
  border-radius: 10px;
  border: 2px solid rgba(255, 255, 255, 0.15);
  background: rgba(0, 0, 0, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.8rem;
  font-weight: 600;
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
}

.parking-spot-item.available {
  border-color: #2ecc71;
  background: rgba(46, 204, 113, 0.15);
}

.parking-spot-item.available:hover {
  background: rgba(46, 204, 113, 0.25);
  box-shadow: 0 0 12px rgba(46, 204, 113, 0.3);
  transform: scale(1.05);
}

.parking-spot-item.booked {
  border-color: #dc3545;
  background: rgba(220, 53, 69, 0.15);
  cursor: not-allowed;
  opacity: 0.7;
}

.spot-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.spot-number {
  font-size: 0.9rem;
  font-weight: 700;
  color: white;
}

.spot-icon {
  font-size: 1rem;
}

.layout-legend {
  display: flex;
  justify-content: center;
  gap: 30px;
  padding: 16px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.legend-color.available {
  background: #2ecc71;
  border-color: #2ecc71;
}

.legend-color.booked {
  background: #dc3545;
  border-color: #dc3545;
}

.auto-assignment-card {
  display: flex;
  gap: 20px;
  padding: 24px;
  background: rgba(155, 89, 182, 0.1);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(155, 89, 182, 0.3);
  border-radius: 14px;
  box-shadow: 0 8px 32px rgba(155, 89, 182, 0.1);
}

.card-icon {
  font-size: 2rem;
  color: #9b59b6;
  min-width: 50px;
  display: flex;
  align-items: flex-start;
}

.card-content {
  flex: 1;
}

.card-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: white;
  margin: 0 0 8px 0;
}

.card-text {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.5;
  margin: 0 0 12px 0;
}

.available-info {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: rgba(155, 89, 182, 0.2);
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.layout-actions {
  text-align: center;
}

.btn-proceed-booking {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 13px 28px;
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.btn-proceed-booking:hover:not(:disabled) {
  background: linear-gradient(135deg, #2980b9, #1e5a7a);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(52, 152, 219, 0.4);
}

.btn-proceed-booking:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.booking-view {
  width: 100%;
  max-width: 1200px;
  animation: slideDown 0.6s ease;
}

.booking-header {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 30px;
}

.btn-back-booking {
  padding: 10px 18px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.btn-back-booking:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.booking-title-section {
  flex: 1;
}

.booking-title {
  font-size: 2.2rem;
  font-weight: 800;
  color: white;
  margin: 0 0 8px 0;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.booking-subtitle {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.booking-content {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 30px;
  align-items: start;
}

.booking-summary-card {
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  height: fit-content;
}

.summary-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: white;
  margin: 0 0 20px 0;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.summary-details {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-label {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.summary-value {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.summary-value.rate-display {
  color: #2ecc71;
  font-weight: 600;
}

.booking-form-section {
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  padding: 28px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.booking-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-fields-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 14px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-field.full-width {
  grid-column: 1 / -1;
}

.form-field.hidden-field {
  display: none;
}

.form-field label {
  font-size: 0.9rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  gap: 6px;
}

.required {
  color: #dc3545;
  font-weight: 700;
}

.form-input {
  padding: 12px 14px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(0, 0, 0, 0.3);
  color: white;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  font-family: inherit;
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.form-input:focus {
  border-color: #3498db;
  background: rgba(52, 152, 219, 0.1);
  outline: none;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.form-input:disabled {
  background: rgba(0, 0, 0, 0.2);
  color: rgba(255, 255, 255, 0.5);
  cursor: not-allowed;
}

.cost-summary-section {
  padding: 20px;
  background: rgba(155, 89, 182, 0.1);
  border: 1px solid rgba(155, 89, 182, 0.2);
  border-radius: 10px;
  border-left: 4px solid #9b59b6;
}

.cost-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: white;
  margin: 0 0 14px 0;
}

.cost-breakdown {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 14px;
}

.cost-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}

.cost-label {
  color: rgba(255, 255, 255, 0.7);
}

.cost-value {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

.cost-row.total-row {
  padding-top: 10px;
  border-top: 1px solid rgba(155, 89, 182, 0.3);
  font-weight: 700;
}

.cost-row.total-row .cost-value {
  color: #9b59b6;
  font-size: 1rem;
}

.cost-note {
  margin: 0;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
  display: flex;
  align-items: flex-start;
  gap: 6px;
  line-height: 1.4;
}

.booking-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-back-form {
  padding: 11px 22px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-back-form:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.btn-confirm-booking {
  padding: 11px 24px;
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.btn-confirm-booking:hover:not(:disabled) {
  background: linear-gradient(135deg, #2980b9, #1e5a7a);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(52, 152, 219, 0.4);
}

.btn-confirm-booking:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
@media (max-width: 1024px) {
  .navbar-menu {
    gap: 20px;
    margin-left: 40px;
  }

  .parking-lots-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }

  .booking-content {
    grid-template-columns: 1fr;
  }

  .booking-summary-card {
    width: 100%;
  }

  .lot-stats-section {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .navbar-content {
    padding: 0 16px;
  }

  .navbar-menu {
    display: none;
  }

  .welcome-title {
    font-size: 2rem;
  }

  .welcome-subtitle {
    font-size: 1rem;
  }

  .parking-lots-grid {
    grid-template-columns: 1fr;
  }

  .lot-stats-section {
    grid-template-columns: repeat(2, 1fr);
  }

  .layout-title,
  .booking-title {
    font-size: 1.6rem;
  }

  .search-filter-bar {
    flex-direction: column;
  }

  .parking-grid {
    grid-template-columns: repeat(auto-fit, minmax(50px, 1fr));
  }

  .form-fields-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .dashboard-content {
    padding: 20px 12px;
  }

  .welcome-title {
    font-size: 1.6rem;
  }

  .parking-lot-card {
    padding: 16px;
  }

  .lot-name {
    font-size: 1.1rem;
  }

  .lot-stats-section {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }

  .stat-card {
    padding: 10px;
  }

  .stat-value {
    font-size: 1rem;
  }

  .parking-grid {
    grid-template-columns: repeat(auto-fit, minmax(45px, 1fr));
    gap: 10px;
  }

  .layout-title,
  .booking-title {
    font-size: 1.3rem;
  }

  .booking-actions {
    flex-direction: column-reverse;
  }

  .btn-back-form,
  .btn-confirm-booking {
    width: 100%;
    justify-content: center;
  }
}
</style>
  