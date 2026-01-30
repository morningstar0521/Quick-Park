<template>
  <div class="admin-dashboard manage-parking-lots-page">
    <nav class="admin-navbar">
      <div class="navbar-content">
        <div class="navbar-brand">
          <span>Quick Park</span>
        </div>
        <div class="navbar-menu">
          <a class="nav-item" @click="$emit('switchView','AdminDashboard')">
            <i class="fas fa-tachometer-alt me-2"></i>Dashboard
          </a>
          <a class="nav-item active" @click="$emit('switchView','ManageParkingLots')">
            <i class="fas fa-map-marked-alt me-2"></i>Parking Lots
          </a>
          <a class="nav-item" @click="$emit('switchView','ManageUser')">
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
          <h1 class="welcome-title">Manage Parking Lots</h1>
          <p class="welcome-subtitle">View, edit, or add new parking facilities to the system</p>
        </div>

        <div v-if="currentContent === 'list'">
          <div class="action-bar">
            <div class="search-container">
              <div class="search-wrapper">
                <i class="fas fa-search search-icon"></i>
                <input 
                  v-model="searchQuery"
                  type="text"
                  class="search-input"
                  placeholder="Search by parking lot name or city..."
                  @input="handleSearch"
                />
              </div>
            </div>
            <button class="btn-add-lot" @click="addParkingLot">
              <i class="fas fa-plus me-2"></i> Add New Parking Lot
            </button>
          </div>

          <div class="results-info">
            <span class="result-count">
              Showing {{ paginatedLots.length > 0 ? (currentPage - 1) * itemsPerPage + 1 : 0 }} - {{ Math.min(currentPage * itemsPerPage, filteredLots.length) }} of {{ filteredLots.length }} parking lots
            </span>
          </div>

          <div class="table-section">
            <div class="card-header">
              <h3><i class="fas fa-list me-2"></i>Parking Lots</h3>
            </div>
            <div class="table-container">
              <table class="lots-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Name</th>
                    <th>City</th>
                    <th>Type</th>
                    <th>Total Spots</th>
                    <th>Occupied</th>
                    <th>Rate/Hour (₹)</th>
                    <th>Total Revenue (₹)</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <template v-for="(lot, index) in paginatedLots" :key="lot.id">
                    <tr>
                      <td>{{ (currentPage - 1) * itemsPerPage + index + 1 }}</td>
                      <td class="lot-name">{{ lot.name }}</td>
                      <td>{{ lot.city }}</td>
                      <td>{{ lot.parkingType }}</td>
                      <td>{{ lot.totalSpots }}</td>
                      <td><span class="badge-occupied">{{ lot.occupiedSpots }}</span></td>
                      <td>₹{{ lot.ratePerHour ? lot.ratePerHour.toFixed(2) : '0.00' }}</td>
                      <td class="revenue-text">₹{{ lot.revenueGenerated ? lot.revenueGenerated.toFixed(2) : '0.00' }}</td>
                      <td>
                        <span class="status-badge" :class="lot.status.toLowerCase()">
                          {{ lot.status }}
                        </span>
                      </td>
                      <td class="action-column">
                        <button class="btn-action view" @click="showLayout(lot)" title="View Layout">
                          <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn-action edit" @click="editLot(lot.id)" title="Edit">
                          <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-action delete" @click="deleteLot(lot.id)" title="Delete">
                          <i class="fas fa-trash-alt"></i>
                        </button>
                      </td>
                    </tr>

                    <tr v-if="selectedLot && selectedLot.id === lot.id" class="layout-row">
                      <td :colspan="10" class="p-0">
                        <div class="parking-layout-section">
                          <h3 class="layout-title">Parking Layout: {{ selectedLot.name }}</h3>
                          <p class="layout-legend">
                            <span class="legend-available">● Available</span> ({{ selectedLot.totalSpots - selectedLot.occupiedSpots }}) | 
                            <span class="legend-booked">● Booked</span> ({{ selectedLot.occupiedSpots }}) | 
                            <span class="legend-total">Total: {{ selectedLot.totalSpots }}</span>
                          </p>

                          <div class="layout-visualizer">
                            <div class="layout-grid">
                              <div 
                                v-for="spot in selectedLot.spots" 
                                :key="spot.id"
                                :class="['parking-spot', { 'booked': spot.isBooked, 'available': !spot.isBooked }]"
                                :title="getSpotTooltip(spot)"
                                @click="viewSpotDetails(spot, selectedLot.name, selectedLot.ratePerHour)">
                                <div class="spot-number">{{ spot.spot_number || spot.id }}</div>
                                <div class="spot-status">
                                  <i v-if="spot.isBooked" class="fas fa-times-circle"></i>
                                  <i v-else class="fas fa-check-circle"></i>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  </template>
                </tbody>
              </table>
            </div>

            <div class="pagination-section" v-if="totalPages > 1">
              <div class="pagination-controls">
                <button 
                  class="btn-pagination" 
                  @click="previousPage"
                  :disabled="currentPage === 1">
                  <i class="fas fa-chevron-left"></i> Previous
                </button>

                <div class="page-numbers">
                  <button 
                    v-for="page in visiblePages" 
                    :key="page"
                    class="btn-page"
                    :class="{ active: page === currentPage }"
                    @click="goToPage(page)">
                    {{ page }}
                  </button>
                </div>

                <button 
                  class="btn-pagination" 
                  @click="nextPage"
                  :disabled="currentPage === totalPages">
                  Next <i class="fas fa-chevron-right"></i>
                </button>
              </div>

              <div class="pagination-info">
                <span>Page {{ currentPage }} of {{ totalPages }}</span>
                <select v-model.number="itemsPerPage" class="items-per-page-select">
                  <option value="5">5 items</option>
                  <option value="10">10 items</option>
                  <option value="15">15 items</option>
                  <option value="20">20 items</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <ParkingLotForm 
          v-if="currentContent === 'add'" 
          @lot-saved="handleLotSaved"
          @cancel="currentContent = 'list'"
        />

        <ParkingLotForm 
          v-if="currentContent === 'edit'" 
          :initialLot="lotToEdit"
          @lot-saved="handleLotSaved"
          @cancel="currentContent = 'list'"
        />
      </div>
    </div>
    
    <SpotDetailsModal
      v-if="showSpotModal"
      :spot="spotModalData"
      @close="showSpotModal = false"
    />
  </div>
</template>

<script>
import axios from "axios";
import ParkingLotForm from "./ParkingLotForm.vue";
import SpotDetailsModal from "./SpotDetailsModal.vue"; 
const generateSpots = (lot) => {
  const spots = [];
  const actualOccupied = Math.min(lot.occupiedSpots || 0, lot.totalSpots || 0);
  
  for (let i = 1; i <= lot.totalSpots; i++) {
    const isBooked = (i <= actualOccupied);
    let spotRevenue = 0;
    let durationHours = 0;
    
    if (isBooked) {
      durationHours = Math.ceil(Math.random() * 8); 
      spotRevenue = durationHours * (lot.ratePerHour || 0);
    }

    spots.push({
      id: i,
      isBooked,
      durationHours,
      spotRevenue,
    });
  }
  return spots;
};

export default {
  name: "ManageParkingLots",
  components: { ParkingLotForm, SpotDetailsModal }, 
  inject: ["emitter"], 
  data() {
    return {
      currentContent: "list",
      lotToEdit: null,
      selectedLot: null,
      parkingLots: [],
      searchQuery: "",
      filteredLots: [],
      currentPage: 1,
      itemsPerPage: 10,
      showSpotModal: false,
      spotModalData: {},
    };
  },
  created() {
    this.fetchParkingLots();
  },
  computed: {
    paginatedLots() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.filteredLots.slice(start, end);
    },
    totalPages() {
      return Math.ceil(this.filteredLots.length / this.itemsPerPage);
    },
    visiblePages() {
      let pages = [];
      const maxVisible = 5;
      const halfVisible = Math.floor(maxVisible / 2);
      
      let start = Math.max(1, this.currentPage - halfVisible);
      let end = Math.min(this.totalPages, start + maxVisible - 1);
      
      if (end - start < maxVisible - 1) {
        start = Math.max(1, end - maxVisible + 1);
      }
      
      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      return pages;
    }
  },
  methods: {
    viewSpotDetails(spot, lotName, ratePerHour) {
      if (!spot.isBooked) {
        return;
      }
      this.spotModalData = {
        spot_id: spot.id,
        lot_name: lotName,
        user_id: spot.user_id ? `UID${spot.user_id}` : 'N/A',
        customer_name: spot.customer_name || 'N/A',
        vehicle_number: spot.vehicle_number || 'N/A',
        start_time: spot.start_time || 'N/A',
        duration_hours: spot.durationHours || 0,
        rate_per_hour: ratePerHour || 0,
        spot_revenue: spot.spotRevenue || 0, 
      };
      
      this.showSpotModal = true;
    },
    
    calculateLotRevenue(lot) {
      lot.totalSpots = Number(lot.totalSpots);
      return lot;
    },

    async fetchParkingLots() {
      try {
        const token = localStorage.getItem('accessToken');
        const response = await this.$axios.get("http://127.0.0.1:5000/api/parking-lots", {
          headers: { Authorization: `Bearer ${token}` },
        });
        this.parkingLots = response.data.map(lot => this.calculateLotRevenue(lot));
        this.filteredLots = this.parkingLots;
        this.currentPage = 1;
      } catch (err) {
        console.error("Error fetching parking lots:", err);
        if (err.response && (err.response.status === 401 || err.response.status === 422)) {
             this.$emit('switchView', 'Home'); 
        }
      }
    },
    
    handleSearch() {
      this.currentPage = 1;
      if (this.searchQuery.trim() === "") {
        this.filteredLots = this.parkingLots;
      } else {
        const query = this.searchQuery.toLowerCase();
        this.filteredLots = this.parkingLots.filter(lot => 
          lot.name.toLowerCase().includes(query) || 
          lot.city.toLowerCase().includes(query)
        );
      }
    },
    
    previousPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    },
    
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    },
    
    goToPage(page) {
      this.currentPage = page;
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    
    async showLayout(lot) {
      if (this.selectedLot && this.selectedLot.id === lot.id) {
        this.selectedLot = null;
      } else {
        try {
          const response = await this.$axios.get(`http://127.0.0.1:5000/api/admin/parking-lots/${lot.id}/spots`);
          console.log("Admin parking spots response:", response.data);
          if (response.data.ok) {
            const spots = response.data.spots.map(spot => ({
              id: spot.id,
              spot_number: spot.spot_number,
              isBooked: !spot.is_available,
              durationHours: spot.duration_hours || 0,
              spotRevenue: spot.spot_revenue || 0,
              customer_name: spot.customer_name,
              vehicle_number: spot.vehicle_number,
              start_time: spot.start_time,
              user_id: spot.user_id
            }));
            console.log("Admin spots loaded:", spots);
            this.selectedLot = { ...lot, spots };
          }
        } catch (err) {
          console.error("Error fetching spot data:", err);
          const spots = generateSpots(lot);
          this.selectedLot = { ...lot, spots };
        }
      }
    },
    
    getSpotTooltip(spot) {
      if (spot.isBooked) {
        return `Spot ${spot.id}: Occupied (${spot.durationHours} Hrs) - Revenue: ₹${spot.spotRevenue.toFixed(2)}`;
      }
      return `Spot ${spot.id}: Available`;
    },
    
    addParkingLot() {
      this.lotToEdit = null;
      this.selectedLot = null;
      this.currentContent = "add";
    },
    
    editLot(id) {
      this.lotToEdit = this.parkingLots.find((lot) => lot.id === id);
      this.selectedLot = null;
      this.currentContent = "edit";
    },
    
    async handleLotSaved() {
      try {
        await this.fetchParkingLots(); 
        this.currentContent = "list";
        this.lotToEdit = null;
        this.selectedLot = null;
        this.emitter.emit("parkingLotChanged"); 
      } catch (err) {
        console.error("Error after saving lot during refresh:", err);
        this.currentContent = "list";
        console.error("Parking lot saved, but failed to refresh the list.");
      }
    },
    
    async deleteLot(id) {
      try {
        const lot = this.parkingLots.find(l => l.id === id);
        if (lot && lot.occupied_spots > 0) {
          alert(`Cannot delete parking lot "${lot.name}". There are ${lot.occupied_spots} occupied spots. Please wait for all spots to be vacated before deleting.`);
          return;
        }
        if (confirm("Are you sure you want to permanently delete this parking lot?")) {
          const token = localStorage.getItem('accessToken');
          await this.$axios.delete(`http://127.0.0.1:5000/api/parking-lots/${id}`, {
              headers: {
                  'Authorization': `Bearer ${token}`
              }
          });
          await this.fetchParkingLots(); 
          this.selectedLot = null;
          this.emitter.emit("parkingLotChanged"); 
        }
      } catch (err) {
          console.error("Error deleting lot:", err);
          const errorMsg = err.response?.data?.message || "Failed to delete lot. Check server status.";
          alert(errorMsg);
      }
    },
    async logout(force = false) {
      const token = localStorage.getItem('accessToken');
      localStorage.removeItem('accessToken');
      delete axios.defaults.headers.common['Authorization']; 
      
      try {
        await this.$axios.post("http://127.0.0.1:5000/api/logout", {}, {
            headers: { Authorization: `Bearer ${token}` }
        });
      } catch (err) {
          console.warn("Server-side logout failed, proceeding with client-side logout:", err);
      } finally {
          if (force) {
            alert("Session expired or unauthorized. Please log in again.");
          }
          this.$emit("switchView", "Home");
      }
    },
  },
};
</script>

<style scoped>
.admin-dashboard.manage-parking-lots-page {
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
.action-bar {
  margin-bottom: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
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

.btn-add-lot {
  background: linear-gradient(135deg, #2ecc71, #27ae60);
  color: white;
  border: none;
  padding: 12px 28px;
  border-radius: 25px;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 8px 20px rgba(46, 204, 113, 0.3);
  white-space: nowrap;
}

.btn-add-lot:hover {
  background: linear-gradient(135deg, #27ae60, #229954);
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(46, 204, 113, 0.4);
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

.lots-table {
  width: 100%;
  border-collapse: collapse;
  color: white;
}

.lots-table thead {
  background: rgba(0, 0, 0, 0.3);
  border-bottom: 2px solid rgba(52, 152, 219, 0.3);
}

.lots-table th {
  padding: 16px 20px;
  text-align: left;
  font-weight: 700;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: rgba(255, 255, 255, 0.9);
}

.lots-table td {
  padding: 14px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 0.9rem;
}

.lots-table tbody tr {
  transition: background 0.2s ease;
}

.lots-table tbody tr:hover {
  background: rgba(52, 152, 219, 0.1);
}

.lot-name {
  font-weight: 700;
  color: #87ceeb;
}

.badge-occupied {
  background: rgba(255, 193, 7, 0.3);
  color: #ffc107;
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.85rem;
}

.revenue-text {
  color: #2ecc71;
  font-weight: 700;
}

.status-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.status-badge.active {
  background: rgba(46, 204, 113, 0.3);
  color: #2ecc71;
}

.status-badge.maintenance {
  background: rgba(255, 165, 0, 0.3);
  color: #ffa500;
}

.status-badge.deactivated {
  background: rgba(220, 53, 69, 0.3);
  color: #dc3545;
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

.btn-action.view {
  background: rgba(52, 152, 219, 0.3);
  color: #3498db;
}

.btn-action.view:hover {
  background: rgba(52, 152, 219, 0.6);
  transform: scale(1.1);
}

.btn-action.edit {
  background: rgba(255, 193, 7, 0.3);
  color: #ffc107;
}

.btn-action.edit:hover {
  background: rgba(255, 193, 7, 0.6);
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
.layout-row td {
  border-top: 2px solid rgba(52, 152, 219, 0.3) !important;
  background-color: rgba(20, 30, 40, 0.9) !important;
  padding: 0 !important;
}

.parking-layout-section {
  width: 100%;
  padding: 30px;
}

.layout-title {
  font-size: 1.6rem;
  font-weight: 800;
  color: #3498db;
  margin-bottom: 15px;
  text-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
}

.layout-legend {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 25px;
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.legend-available,
.legend-booked,
.legend-total {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
}

.legend-available {
  color: #3498db;
}

.legend-booked {
  color: #2ecc71;
}

.legend-total {
  color: rgba(255, 255, 255, 0.8);
}

.layout-visualizer {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(52, 152, 219, 0.2);
  border-radius: 12px;
  padding: 25px;
}

.layout-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: flex-start;
}

.parking-spot {
  position: relative;
  width: 70px;
  height: 70px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 4px;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.parking-spot.available {
  background: linear-gradient(135deg, #3498db, #2980b9);
  border-color: #2980b9;
  color: white;
}

.parking-spot.booked {
  background: linear-gradient(135deg, #2ecc71, #27ae60);
  border-color: #27ae60;
  color: white;
}

.parking-spot:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
}

.spot-number {
  font-size: 0.9rem;
  font-weight: 800;
}

.spot-status {
  font-size: 1rem;
}
.pagination-section {
  background: rgba(0, 0, 0, 0.2);
  padding: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-pagination {
  background: rgba(52, 152, 219, 0.2);
  border: 1.5px solid rgba(52, 152, 219, 0.4);
  color: rgba(255, 255, 255, 0.8);
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-pagination:hover:not(:disabled) {
  background: rgba(52, 152, 219, 0.4);
  border-color: rgba(52, 152, 219, 0.7);
  transform: translateY(-2px);
}

.btn-pagination:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 6px;
}

.btn-page {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(52, 152, 219, 0.3);
  color: rgba(255, 255, 255, 0.7);
  width: 36px;
  height: 36px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-page:hover {
  background: rgba(52, 152, 219, 0.2);
  border-color: rgba(52, 152, 219, 0.6);
}

.btn-page.active {
  background: linear-gradient(135deg, #3498db, #2980b9);
  border-color: #2980b9;
  color: white;
  font-weight: 700;
}

.pagination-info {
  display: flex;
  align-items: center;
  gap: 15px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 600;
  font-size: 0.9rem;
}

.items-per-page-select {
  background: rgba(255, 255, 255, 0.08);
  border: 1.5px solid rgba(52, 152, 219, 0.3);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  outline: none;
}

.items-per-page-select:hover {
  border-color: rgba(52, 152, 219, 0.6);
  background: rgba(255, 255, 255, 0.12);
}

.items-per-page-select:focus {
  border-color: rgba(52, 152, 219, 0.8);
  box-shadow: 0 0 15px rgba(52, 152, 219, 0.2);
}

.items-per-page-select option {
  background: #2c3e50;
  color: white;
}
@media (max-width: 1200px) {
  .navbar-menu {
    gap: 25px;
    margin-left: 40px;
  }

  .lots-table th,
  .lots-table td {
    padding: 12px 15px;
    font-size: 0.85rem;
  }

  .pagination-section {
    flex-direction: column;
    align-items: flex-start;
  }

  .pagination-info {
    width: 100%;
    justify-content: space-between;
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

  .action-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-container {
    min-width: auto;
  }

  .btn-add-lot {
    width: 100%;
    justify-content: center;
  }

  .lots-table {
    font-size: 0.8rem;
  }

  .lots-table th,
  .lots-table td {
    padding: 10px 12px;
  }

  .btn-action {
    width: 32px;
    height: 32px;
    font-size: 0.8rem;
  }

  .parking-spot {
    width: 60px;
    height: 60px;
    font-size: 0.8rem;
  }

  .pagination-section {
    flex-direction: column;
    align-items: stretch;
    padding: 16px;
  }

  .pagination-controls {
    justify-content: center;
    flex-wrap: wrap;
  }

  .pagination-info {
    flex-direction: column;
    justify-content: center;
    text-align: center;
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

  .lots-table th,
  .lots-table td {
    padding: 8px 10px;
    font-size: 0.75rem;
  }

  .btn-add-lot {
    width: 100%;
    justify-content: center;
    padding: 10px 20px;
  }

  .parking-spot {
    width: 50px;
    height: 50px;
    gap: 2px;
    font-size: 0.7rem;
  }

  .spot-number {
    font-size: 0.8rem;
  }

  .spot-status {
    font-size: 0.85rem;
  }
}
</style>