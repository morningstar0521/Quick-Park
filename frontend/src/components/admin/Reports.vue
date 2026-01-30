<template>
  <div class="admin-dashboard reports-page">
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
          <a class="nav-item" @click="$emit('switchView','ManageUser')">
            <i class="fas fa-users me-2"></i>Users
          </a>
          <a class="nav-item active" @click="$emit('switchView','Reports')">
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
          <div class="welcome-header">
            <div class="welcome-text">
              <h1 class="welcome-title">Reports</h1>
              <p class="welcome-subtitle">Comprehensive analytics and performance insights for parking slots</p>
            </div>
            <button v-if="selectedLot && slotReports.length > 0" @click="downloadLotReport" class="btn-download-top">
              <i class="fas fa-download me-2"></i>Download Lot Report
            </button>
          </div>
        </div>

        <div class="lots-section">
          <div class="section-header">
            <h3><i class="fas fa-map-marked-alt me-2"></i>Select Parking Lot</h3>
          </div>
          <div class="lots-grid">
            <div 
              v-for="lot in parkingLots" 
              :key="lot.id" 
              class="lot-card"
              @click="selectLot(lot)"
              :class="{ 'selected': selectedLot && selectedLot.id === lot.id }"
            >
              <div class="lot-header">
                <h4 class="lot-name">{{ lot.name }}</h4>
                <span class="lot-address">{{ lot.address }}</span>
              </div>
              <div class="lot-stats">
                <div class="stat-item">
                  <span class="stat-label">Total Spots:</span>
                  <span class="stat-value">{{ lot.total_spots }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Rate:</span>
                  <span class="stat-value">₹{{ lot.rate_per_hour }}/hr</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="chart-section">
          <div class="section-header">
            <h3><i class="fas fa-chart-bar me-2"></i>Parking Lots Revenue Comparison</h3>
          </div>
          <div class="chart-container">
            <canvas id="lotsComparisonChart" ref="lotsComparisonChart"></canvas>
          </div>
        </div>

        <div v-if="selectedLot" class="summary-section">
          <div class="section-header">
            <h3><i class="fas fa-chart-line me-2"></i>Summary Statistics</h3>
          </div>
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon"><i class="fas fa-parking"></i></div>
              <div class="stat-info">
                <span class="stat-title">Total Spots</span>
                <span class="stat-number">{{ selectedLot.total_spots }}</span>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon"><i class="fas fa-calendar-check"></i></div>
              <div class="stat-info">
                <span class="stat-title">Total Bookings</span>
                <span class="stat-number">{{ totalBookings }}</span>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon"><i class="fas fa-rupee-sign"></i></div>
              <div class="stat-info">
                <span class="stat-title">Total Revenue</span>
                <span class="stat-number">₹{{ totalRevenue.toFixed(2) }}</span>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon"><i class="fas fa-chart-pie"></i></div>
              <div class="stat-info">
                <span class="stat-title">Avg Revenue/Spot</span>
                <span class="stat-number">₹{{ avgRevenue.toFixed(2) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="selectedLot && slotReports.length > 0" class="analytics-section">
          <div class="section-header">
            <h3><i class="fas fa-chart-area me-2"></i>Parking Lot Analytics</h3>
          </div>
          
          <div class="analytics-grid">
            <div class="analytics-card">
              <h4 class="analytics-title"><i class="fas fa-clock me-2"></i>Peak Hours</h4>
              <canvas id="peakHoursChart" ref="peakHoursChart"></canvas>
            </div>
            
            <div class="analytics-card">
              <h4 class="analytics-title"><i class="fas fa-chart-line me-2"></i>Revenue Trend (30 Days)</h4>
              <canvas id="revenueTrendChart" ref="revenueTrendChart"></canvas>
            </div>
            
            <div class="analytics-card">
              <h4 class="analytics-title"><i class="fas fa-percentage me-2"></i>Occupancy Trend (30 Days)</h4>
              <canvas id="occupancyTrendChart" ref="occupancyTrendChart"></canvas>
            </div>
          </div>
        </div>
        <div v-if="selectedLot && slotReports.length > 0" class="detailed-report-section">
          <div class="section-header">
            <h3><i class="fas fa-table me-2"></i>Spot Performance Details</h3>
            <div class="table-controls">
              <input 
                v-model="searchSpot" 
                type="text" 
                placeholder="Search by spot number..."
                class="search-input"
              >
              <select v-model="sortBy" class="sort-select">
                <option value="spot_number">Sort by Spot #</option>
                <option value="total_bookings">Sort by Bookings</option>
                <option value="total_revenue">Sort by Revenue</option>
              </select>
            </div>
          </div>

          <div class="table-wrapper">
            <table class="slots-report-table">
              <thead>
                <tr>
                  <th>Spot #</th>
                  <th>Status</th>
                  <th>Total Bookings</th>
                  <th>Total Revenue (₹)</th>
                  <th>Avg Revenue (₹)</th>
                  <th>Occupancy Rate</th>
                  <th>Last Used</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="slot in filteredAndSortedSlots" :key="slot.id" class="slot-row" @click="openSpotDetail(slot)" style="cursor: pointer;">
                  <td class="cell-spot"><strong>{{ slot.spot_number }}</strong></td>
                  <td class="cell-status">
                    <span class="status-badge" :class="{ 'occupied': slot.is_booked, 'available': !slot.is_booked }">
                      {{ slot.is_booked ? '🔴 Occupied' : '🟢 Available' }}
                    </span>
                  </td>
                  <td class="cell-bookings">{{ slot.total_bookings }}</td>
                  <td class="cell-revenue">{{ slot.total_revenue.toFixed(2) }}</td>
                  <td class="cell-avg-revenue">{{ (slot.total_revenue / (slot.total_bookings || 1)).toFixed(2) }}</td>
                  <td class="cell-occupancy">
                    <div class="occupancy-bar">
                      <div class="occupancy-fill" :style="{ width: calculateOccupancy(slot) + '%' }"></div>
                      <span class="occupancy-text">{{ calculateOccupancy(slot) }}%</span>
                    </div>
                  </td>
                  <td class="cell-last-used">{{ formatDate(slot.last_used_at) || 'Never' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="selectedLot && slotReports.length === 0" class="empty-state">
          <i class="fas fa-inbox"></i>
          <p>No slots data available for this parking lot</p>
        </div>
      </div>
    </div>

    <div v-if="selectedSpot" class="modal-overlay" @click.self="closeSpotDetail">
      <div class="modal-content spot-detail-modal">
        <div class="modal-header">
          <h3><i class="fas fa-info-circle me-2"></i>Spot #{{ selectedSpot.spot_number }} Details</h3>
          <button @click="closeSpotDetail" class="modal-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="detail-grid">
            <div class="detail-item">
              <label>Status</label>
              <span class="status-badge" :class="{ 'occupied': selectedSpot.is_booked, 'available': !selectedSpot.is_booked }">
                {{ selectedSpot.is_booked ? '🔴 Occupied' : '🟢 Available' }}
              </span>
            </div>
            <div class="detail-item">
              <label>Total Bookings</label>
              <span>{{ selectedSpot.total_bookings }}</span>
            </div>
            <div class="detail-item">
              <label>Total Revenue (₹)</label>
              <span>{{ selectedSpot.total_revenue.toFixed(2) }}</span>
            </div>
            <div class="detail-item">
              <label>Average Revenue (₹)</label>
              <span>{{ (selectedSpot.total_revenue / (selectedSpot.total_bookings || 1)).toFixed(2) }}</span>
            </div>
            <div class="detail-item">
              <label>Occupancy Rate</label>
              <span>{{ calculateOccupancy(selectedSpot) }}%</span>
            </div>
            <div class="detail-item">
              <label>Last Used</label>
              <span>{{ formatDate(selectedSpot.last_used_at) || 'Never' }}</span>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="downloadSpotAsCSV" class="download-btn-modal">
            <i class="fas fa-download me-2"></i>Download as CSV
          </button>
          <button @click="closeSpotDetail" class="cancel-btn">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

function createChartConfig(chartType, labels, datasets, options = {}) {
  const validatedDatasets = datasets
    .filter(ds => ds && typeof ds === 'object')
    .map(ds => ({
      ...ds,
      fill: (chartType === 'line' || ds.type === 'line') ? (ds.fill !== undefined ? ds.fill : false) : false,
      data: Array.isArray(ds.data) ? ds.data : [],
      label: ds.label || 'Dataset',
      borderWidth: ds.borderWidth !== undefined ? ds.borderWidth : 1,
      pointRadius: (chartType === 'line' || ds.type === 'line' || ds.type === 'scatter') ? (ds.pointRadius !== undefined ? ds.pointRadius : 4) : undefined,
      pointHoverRadius: (chartType === 'line' || ds.type === 'line' || ds.type === 'scatter') ? (ds.pointHoverRadius !== undefined ? ds.pointHoverRadius : 6) : undefined,
      clip: ds.clip !== undefined ? ds.clip : false,
    }))
    .filter(ds => ds.data.length > 0);

  if (validatedDatasets.length === 0) {
    validatedDatasets.push({
      label: 'No Data',
      data: [],
      fill: false,
      borderColor: '#ccc',
      backgroundColor: '#f9f9f9'
    });
  }

  return {
    type: chartType,
    data: {
      labels: Array.isArray(labels) ? labels : [],
      datasets: validatedDatasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      animation: false,
      filler: { 
        propagate: false,
        drawTime: 'beforeDatasetsDraw'
      },
      ...options
    }
  };
}

export default {
  name: 'Reports',
  data() {
    return {
      parkingLots: [],
      selectedLot: null,
      selectedSpot: null,
      slotReports: [],
      analyticsData: null,
      charts: {},
      searchSpot: '',
      sortBy: 'spot_number'
    };
  },
  created() {
    this.fetchParkingLots();
  },
  mounted() {
  },
  computed: {
    totalBookings() {
      return this.slotReports.reduce((sum, slot) => sum + (slot.total_bookings || 0), 0);
    },
    totalRevenue() {
      return this.slotReports.reduce((sum, slot) => sum + (slot.total_revenue || 0), 0);
    },
    avgRevenue() {
      return this.slotReports.length > 0 ? this.totalRevenue / this.slotReports.length : 0;
    },
    filteredAndSortedSlots() {
      let filtered = this.slotReports.filter(slot => 
        slot.spot_number.toString().includes(this.searchSpot)
      );
      
      filtered.sort((a, b) => {
        if (this.sortBy === 'spot_number') {
          return a.spot_number - b.spot_number;
        } else if (this.sortBy === 'total_bookings') {
          return b.total_bookings - a.total_bookings;
        } else if (this.sortBy === 'total_revenue') {
          return b.total_revenue - a.total_revenue;
        }
        return 0;
      });
      
      return filtered;
    }
  },
  methods: {
    async fetchParkingLots() {
      try {
        const token = localStorage.getItem('accessToken');
        const response = await this.$axios.get("http://127.0.0.1:5000/api/parking-lots", {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.parkingLots = response.data;
        console.log("Parking lots data:", this.parkingLots);
        this.$nextTick(() => {
          this.renderLotsComparisonChart();
        });
      } catch (err) {
        console.error("Error fetching parking lots:", err);
        alert("Failed to fetch parking lots");
      }
    },

    renderLotsComparisonChart() {
      try {
        const canvas = document.getElementById('lotsComparisonChart');
        if (!canvas) {
          console.warn("Canvas element #lotsComparisonChart not found");
          return;
        }

        if (!this.parkingLots || this.parkingLots.length === 0) {
          console.warn("No parking lots available");
          return;
        }
        if (this.charts['lotsComparison']) {
          try {
            this.charts['lotsComparison'].destroy();
          } catch (e) {
            console.warn("Error destroying previous chart:", e);
          }
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) {
          console.warn("Cannot get 2D context from canvas");
          return;
        }

        const labels = this.parkingLots.map(lot => lot.name);
        const revenues = this.parkingLots.map(lot => lot.revenueGenerated || 0);
        
        const maxRevenue = Math.max(...revenues);
        const maxIndex = revenues.indexOf(maxRevenue);
        const colors = revenues.map((revenue, index) => 
          index === maxIndex ? '#51cf66' : '#4dabf7'
        );

        const config = createChartConfig('bar', labels, [{
          label: 'Total Revenue (₹)',
          data: revenues,
          backgroundColor: colors,
          borderColor: colors.map(color => color === '#51cf66' ? '#40c057' : '#339af0'),
          borderWidth: 2,
          borderRadius: 8,
          borderSkipped: false,
          fill: false
        }], {
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            },
            title: {
              display: true,
              text: 'Revenue Comparison Across All Parking Lots',
              font: {
                size: 16,
                weight: 'bold'
              },
              color: '#2c3e50'
            }
          },
          scales: {
            y: {
              type: 'linear',
              position: 'left',
              beginAtZero: true,
              grid: {
                color: 'rgba(0,0,0,0.1)'
              },
              ticks: {
                font: { size: 12 },
                callback: function(value) {
                  return '₹' + value;
                }
              }
            },
            x: {
              type: 'category',
              position: 'bottom',
              grid: {
                display: false
              },
              ticks: {
                font: { size: 12 }
              }
            }
          }
        });

        this.charts['lotsComparison'] = new ChartJS(ctx, config);
      } catch (e) {
        console.error("Error rendering lots comparison chart:", e);
      }
    },

    selectLot(lot) {
      this.selectedLot = lot;
      this.fetchSlotReports(lot.id);
    },

    async viewLotReports(lot) {
      this.selectedLot = lot;
      await this.fetchSlotReports(lot.id);
    },

    async fetchSlotReports(lotId) {
      try {
        const token = localStorage.getItem('accessToken');
        const response = await this.$axios.get(`http://127.0.0.1:5000/api/admin/reports/slots/${lotId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (response.data.ok) {
          this.slotReports = response.data.slot_reports;
          this.fetchLotAnalytics(lotId);
          this.$nextTick(() => {
            this.renderCharts();
          });
        }
      } catch (err) {
        console.error("Error fetching slot reports:", err);
        alert("Failed to fetch slot reports");
      }
    },

    async fetchLotAnalytics(lotId) {
      try {
        const token = localStorage.getItem('accessToken');
        const response = await this.$axios.get(`http://127.0.0.1:5000/api/admin/reports/lot-analytics/${lotId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (response.data.ok) {
          this.analyticsData = response.data.analytics;
        }
      } catch (err) {
        console.error("Error fetching lot analytics:", err);
      }
    },

    renderCharts() {
      if (this.slotReports && this.slotReports.length > 0) {
        this.$nextTick(() => {
          setTimeout(() => {
            this.$nextTick(() => {
              try {
                if (this.analyticsData) {
                  this.renderAnalyticsCharts();
                }
              } catch (err) {
                console.error("Error rendering charts:", err);
              }
            });
          }, 500);
        });
      }
    },

    renderAnalyticsCharts() {
      try {
        if (this.analyticsData) {
          setTimeout(() => this.renderPeakHoursChart(), 100);
          setTimeout(() => this.renderRevenueTrendChart(), 300);
          setTimeout(() => this.renderOccupancyTrendChart(), 500);
        }
      } catch (err) {
        console.error("Error rendering analytics charts:", err);
      }
    },

    viewSlotDetail(slot) {
      const slotDetailUrl = `#/slot-detail?slotId=${slot.id}&lotId=${this.selectedLot.id}`;
      window.open(slotDetailUrl, '_blank');
    },

    calculateOccupancy(slot) {
      if (!slot.total_bookings) return 0;
      const maxBookings = 30;
      return Math.min(Math.round((slot.total_bookings / maxBookings) * 100), 100);
    },
    renderPeakHoursChart() {
      try {
        const canvas = this.$refs.peakHoursChart;
        if (!canvas) {
          console.warn('peakHoursChart canvas ref not available');
          return;
        }

        if (!canvas.offsetParent && !canvas.offsetWidth) {
          console.warn('peakHoursChart canvas not yet rendered in DOM');
          return;
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) {
          console.warn('Cannot get 2d context from peakHoursChart');
          return;
        }

        if (!this.analyticsData) return;

        if (this.charts['peakHours']) {
          this.charts['peakHours'].destroy();
          this.charts['peakHours'] = null;
        }

        const data = this.analyticsData.hourly_distribution;
        if (!data || Object.keys(data).length === 0) {
          console.warn('No hourly distribution data');
          return;
        }
        
        const labels = Array.from({length: 24}, (_, i) => `${i}:00`);
        const values = Object.values(data);
        const config = createChartConfig('line', labels, [{
          label: 'Bookings per Hour',
          data: values,
          borderColor: '#3498db',
          borderWidth: 2,
          pointBackgroundColor: '#3498db',
          pointBorderColor: 'white',
          pointBorderWidth: 2,
          pointRadius: 5,
          pointHoverRadius: 7,
          fill: false,
          tension: 0.4
        }], {
          plugins: { 
            legend: { display: false },
            tooltip: { enabled: true }
          },
          scales: {
            y: { 
              type: 'linear', 
              beginAtZero: true
            },
            x: { type: 'category' }
          }
        });

        this.charts['peakHours'] = new ChartJS(ctx, config);
      } catch (e) {
        console.error("Error rendering peak hours chart:", e);
      }
    },

    renderRevenueTrendChart() {
      try {
        const canvas = this.$refs.revenueTrendChart;
        if (!canvas) {
          console.warn('revenueTrendChart canvas ref not available');
          return;
        }

        if (!canvas.offsetParent && !canvas.offsetWidth) {
          console.warn('revenueTrendChart canvas not yet rendered in DOM');
          return;
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) {
          console.warn('Cannot get 2d context from revenueTrendChart');
          return;
        }

        if (!this.analyticsData) return;

        if (this.charts['revenueTrend']) {
          this.charts['revenueTrend'].destroy();
          this.charts['revenueTrend'] = null;
        }

        const data = this.analyticsData.daily_revenue_trend;
        if (!data || Object.keys(data).length === 0) {
          console.warn('No daily revenue trend data');
          return;
        }
        
        const labels = Object.keys(data).map(d => new Date(d).toLocaleDateString('en-IN', {month:'short', day:'numeric'}));
        const values = Object.values(data);
        const config = createChartConfig('bar', labels, [{
          label: 'Daily Revenue (₹)',
          data: values,
          backgroundColor: '#2ecc71',
          borderColor: '#27ae60',
          borderWidth: 1,
          fill: false
        }], {
          plugins: { 
            legend: { display: false },
            tooltip: { enabled: true }
          },
          scales: {
            y: { type: 'linear', beginAtZero: true },
            x: { type: 'category' }
          }
        });

        this.charts['revenueTrend'] = new ChartJS(ctx, config);
      } catch (e) {
        console.error("Error rendering revenue trend chart:", e);
      }
    },

    renderOccupancyTrendChart() {
      try {
        const canvas = this.$refs.occupancyTrendChart;
        if (!canvas) {
          console.warn('occupancyTrendChart canvas ref not available');
          return;
        }

        if (!canvas.offsetParent && !canvas.offsetWidth) {
          console.warn('occupancyTrendChart canvas not yet rendered in DOM');
          return;
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) {
          console.warn('Cannot get 2d context from occupancyTrendChart');
          return;
        }

        if (!this.analyticsData) return;

        if (this.charts['occupancyTrend']) {
          this.charts['occupancyTrend'].destroy();
          this.charts['occupancyTrend'] = null;
        }

        const data = this.analyticsData.occupancy_trend;
        if (!data || Object.keys(data).length === 0) {
          console.warn('No occupancy trend data');
          return;
        }
        
        const labels = Object.keys(data).map(d => new Date(d).toLocaleDateString('en-IN', {month:'short', day:'numeric'}));
        const values = Object.values(data);
        const config = createChartConfig('line', labels, [{
          label: 'Occupancy (%)',
          data: values,
          borderColor: '#e74c3c',
          borderWidth: 2,
          pointBackgroundColor: '#e74c3c',
          pointBorderColor: 'white',
          pointBorderWidth: 2,
          pointRadius: 4,
          fill: false,
          tension: 0.4
        }], {
          plugins: { 
            legend: { display: false },
            tooltip: { enabled: true }
          },
          scales: {
            y: { 
              type: 'linear', 
              beginAtZero: true, 
              max: 100
            },
            x: { type: 'category' }
          }
        });

        this.charts['occupancyTrend'] = new ChartJS(ctx, config);
      } catch (e) {
        console.error("Error rendering occupancy trend chart:", e);
      }
    },

    downloadAsCSV() {
      if (!this.slotReports || this.slotReports.length === 0) {
        alert('No data to download');
        return;
      }

      const headers = ['Spot #', 'Total Bookings', 'Total Revenue (₹)', 'Avg Revenue (₹)', 'Occupancy %', 'Last Booking'];
      const rows = this.slotReports.map(slot => [
        slot.spot_number,
        slot.total_bookings,
        slot.total_revenue.toFixed(2),
        (slot.total_revenue / Math.max(slot.total_bookings, 1)).toFixed(2),
        slot.occupancy_percentage.toFixed(2),
        slot.last_booking_date ? new Date(slot.last_booking_date).toLocaleDateString('en-IN') : 'N/A'
      ]);

      const csvContent = [
        headers.join(','),
        ...rows.map(row => row.join(','))
      ].join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', `parking-report-${this.selectedLot.id}-${new Date().toISOString().split('T')[0]}.csv`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    },

    async downloadLotReport() {
      if (!this.selectedLot) {
        alert('Please select a parking lot first');
        return;
      }

      try {
        const token = localStorage.getItem('accessToken');
        console.log('Token:', token ? 'Present' : 'Missing');
        console.log('Lot ID:', this.selectedLot.id);
        
        console.log('Testing JWT endpoint...');
        const jwtTest = await this.$axios.get('http://127.0.0.1:5000/api/admin/reports/test-jwt', {
          headers: { Authorization: `Bearer ${token}` }
        });
        console.log('JWT test response:', jwtTest.data);
        
        if (!jwtTest.data.ok) {
          alert('JWT verification failed: ' + jwtTest.data.message);
          return;
        }

        if (jwtTest.data.role !== 'admin') {
          alert('You do not have admin role. Role: ' + jwtTest.data.role);
          return;
        }

        console.log('JWT verified, downloading CSV...');
        const response = await this.$axios.get(`http://127.0.0.1:5000/api/admin/reports/lot-csv/${this.selectedLot.id}`, {
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob'
        });

        console.log('Response received:', response.status);
        const blob = response.data;
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `parking-lot-report-${this.selectedLot.id}-${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        alert('Report downloaded successfully!');
      } catch (error) {
        console.error('Full error:', error);
        console.error('Response status:', error.response?.status);
        console.error('Response headers:', error.response?.headers);
        
        let errorMsg = 'Error downloading report';
        
        if (error.response?.status === 403) {
          errorMsg = 'Access denied - Admin role required';
        } else if (error.response?.status === 404) {
          errorMsg = 'Parking lot not found';
        } else if (error.response?.status === 500) {
          errorMsg = 'Server error generating CSV - check backend logs';
        } else if (error.message) {
          errorMsg = error.message;
        }
        
        alert(errorMsg);
      }
    },

    openSpotDetail(slot) {
      this.selectedSpot = slot;
    },

    closeSpotDetail() {
      this.selectedSpot = null;
    },

    downloadSpotAsCSV() {
      if (!this.selectedSpot) {
        alert('No spot selected');
        return;
      }

      const headers = ['Property', 'Value'];
      const rows = [
        ['Spot Number', this.selectedSpot.spot_number],
        ['Status', this.selectedSpot.is_booked ? 'Occupied' : 'Available'],
        ['Total Bookings', this.selectedSpot.total_bookings],
        ['Total Revenue (₹)', this.selectedSpot.total_revenue.toFixed(2)],
        ['Average Revenue (₹)', (this.selectedSpot.total_revenue / Math.max(this.selectedSpot.total_bookings, 1)).toFixed(2)],
        ['Occupancy Rate (%)', this.calculateOccupancy(this.selectedSpot).toFixed(2)],
        ['Last Used', this.formatDate(this.selectedSpot.last_used_at) || 'Never'],
        ['Report Generated', new Date().toLocaleString('en-IN')]
      ];

      const csvContent = [
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
      ].join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', `spot-${this.selectedSpot.spot_number}-report-${new Date().toISOString().split('T')[0]}.csv`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    },

    closeDetailedModal() {
      this.showDetailedModal = false;
      this.selectedSlot = null;
    },

    formatDate(dateString) {
      if (!dateString) return '';
      return new Date(dateString).toLocaleDateString('en-IN');
    },

    formatTime(dateString) {
      if (!dateString) return '';
      return new Date(dateString).toLocaleTimeString('en-IN', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
      });
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
    }
  }
}
</script>

<style scoped>
.admin-dashboard.reports-page {
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
  margin-bottom: 40px;
  animation: slideDown 0.6s ease;
}

.welcome-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 30px;
}

.welcome-text {
  text-align: left;
  flex: 1;
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
.section-header {
  background: rgba(0, 0, 0, 0.2);
  padding: 18px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 20px;
  border-radius: 12px 12px 0 0;
}

.section-header h3 {
  margin: 0;
  color: white;
  font-size: 1.2rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10px;
}
.lots-section {
  margin-bottom: 40px;
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
}

.lots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  padding: 24px;
}

.lot-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  border: 1.5px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.lot-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.3s ease;
  pointer-events: none;
}

.lot-card:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(52, 152, 219, 0.5);
  box-shadow: 0 12px 40px rgba(52, 152, 219, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transform: translateY(-6px);
}

.lot-card:hover::before {
  left: 100%;
}

.lot-card.selected {
  background: rgba(81, 207, 102, 0.15);
  border: 2px solid rgba(81, 207, 102, 0.7);
  box-shadow: 0 14px 48px rgba(81, 207, 102, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2);
  transform: translateY(-6px);
}

.lot-card.selected::after {
  content: '✓';
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, rgba(81, 207, 102, 0.9), rgba(64, 192, 87, 0.9));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 1.2rem;
  animation: checkmark 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 4px 12px rgba(81, 207, 102, 0.4);
}

@keyframes checkmark {
  0% {
    transform: scale(0) rotate(-180deg);
    opacity: 0;
  }
  70% {
    transform: scale(1.15) rotate(10deg);
  }
  100% {
    transform: scale(1) rotate(0);
    opacity: 1;
  }
}

.lot-header {
  margin-bottom: 15px;
}

.lot-name {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: white;
  margin-bottom: 4px;
}

.lot-address {
  display: block;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.lot-stats {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 15px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}

.stat-label {
  color: rgba(255, 255, 255, 0.7);
  font-weight: 600;
  transition: color 0.3s ease;
}

.stat-value {
  color: #3498db;
  font-weight: 700;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.lot-card.selected .stat-label {
  color: rgba(255, 255, 255, 0.85);
}

.lot-card.selected .stat-value {
  color: #51cf66;
  text-shadow: 0 0 10px rgba(81, 207, 102, 0.4);
}
.chart-section {
  margin-bottom: 40px;
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
}

.chart-container {
  padding: 24px;
  position: relative;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.slots-section {
  margin-bottom: 40px;
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
}

.slots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  padding: 24px;
}

.slot-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  border: 1.5px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
}

.slot-card:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(52, 152, 219, 0.4);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.slot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.slot-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: white;
}

.slot-status {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

.slot-status.occupied {
  background: rgba(231, 76, 60, 0.2);
  color: #e74c3c;
}

.slot-status.available {
  background: rgba(46, 204, 113, 0.2);
  color: #2ecc71;
}

.slot-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 15px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}

.info-label {
  color: rgba(255, 255, 255, 0.7);
  font-weight: 600;
  display: flex;
  align-items: center;
}

.info-value {
  color: #3498db;
  font-weight: 700;
  font-size: 1rem;
}

.btn-view-details {
  width: 100%;
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.3), rgba(52, 152, 219, 0.1));
  border: 1.5px solid rgba(52, 152, 219, 0.4);
  color: white;
  padding: 10px 14px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.btn-view-details:hover {
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.5), rgba(52, 152, 219, 0.2));
  border-color: rgba(52, 152, 219, 0.8);
  transform: translateY(-2px);
}
.summary-section {
  margin-bottom: 40px;
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  animation: slideIn 0.4s ease;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 18px;
  padding: 28px;
}

.stat-card {
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.12), rgba(81, 207, 102, 0.08));
  border: 1.5px solid rgba(52, 152, 219, 0.25);
  border-radius: 14px;
  padding: 26px 22px;
  display: flex;
  align-items: center;
  gap: 18px;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: visible;
  min-height: 88px;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent);
  transition: left 0.5s ease;
  pointer-events: none;
  border-radius: 14px;
}

.stat-card:hover {
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.18), rgba(81, 207, 102, 0.12));
  border-color: rgba(52, 152, 219, 0.45);
  box-shadow: 0 12px 40px rgba(52, 152, 219, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.15);
  transform: translateY(-6px);
}

.stat-card:hover::before {
  left: 100%;
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.3), rgba(52, 152, 219, 0.15));
  border: 1.5px solid rgba(52, 152, 219, 0.4);
  font-size: 1.8rem;
  color: #3498db;
  flex-shrink: 0;
  transition: all 0.3s ease;
  box-shadow: 0 6px 16px rgba(52, 152, 219, 0.15);
}

.stat-card:hover .stat-icon {
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.45), rgba(52, 152, 219, 0.25));
  border-color: rgba(52, 152, 219, 0.6);
  color: #5dade2;
  transform: scale(1.1) rotate(-5deg);
  box-shadow: 0 8px 24px rgba(52, 152, 219, 0.25);
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  min-width: 0;
  position: relative;
  z-index: 1;
}

.stat-title {
  display: block;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.65);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.1px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stat-number {
  display: block;
  font-size: 2rem;
  font-weight: 900;
  color: white;
  text-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
  letter-spacing: -0.5px;
  line-height: 1.2;
  word-break: break-word;
  white-space: normal;
  overflow-wrap: break-word;
}

.stat-card:hover .stat-number {
  color: #e0f2fe;
  text-shadow: 0 3px 12px rgba(52, 152, 219, 0.4);
}
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  backdrop-filter: blur(8px);
  animation: backdropFade 0.3s ease;
}

@keyframes backdropFade {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-card {
  background: linear-gradient(135deg, rgba(20, 45, 70, 0.98), rgba(35, 65, 95, 0.98));
  border: 1px solid rgba(52, 152, 219, 0.3);
  border-radius: 16px;
  max-width: 1000px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 
    0 25px 50px rgba(0, 0, 0, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 28px 32px;
  border-bottom: 2px solid rgba(52, 152, 219, 0.2);
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.08), rgba(81, 207, 102, 0.08));
}

.modal-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 800;
  color: white;
  display: flex;
  align-items: center;
  gap: 12px;
}

.modal-title::before {
  content: '📊';
  font-size: 1.4rem;
}

.btn-close {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.4rem;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 8px 12px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
}

.btn-close:hover {
  background: rgba(231, 76, 60, 0.2);
  color: #e74c3c;
  border-color: rgba(231, 76, 60, 0.3);
  transform: rotate(90deg);
}

.modal-content {
  padding: 32px;
}
.report-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
  padding: 24px;
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.08), rgba(52, 152, 219, 0.04));
  border-radius: 14px;
  border: 1.5px solid rgba(52, 152, 219, 0.2);
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 10px;
  border: 1px solid rgba(52, 152, 219, 0.15);
  transition: all 0.3s ease;
}

.summary-item:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(52, 152, 219, 0.3);
  transform: translateY(-2px);
}

.summary-label {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.summary-value {
  font-size: 1.6rem;
  font-weight: 800;
  color: #51cf66;
  text-shadow: 0 0 10px rgba(81, 207, 102, 0.2);
}
.charts-section {
  margin-bottom: 32px;
}

.chart-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}

.chart-row .chart-container {
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.06), rgba(52, 152, 219, 0.03));
  border: 1.5px solid rgba(52, 152, 219, 0.15);
  border-radius: 14px;
  padding: 20px;
  height: 320px;
  max-height: 320px;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  overflow: hidden;
}

.chart-row .chart-container:hover {
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.1), rgba(52, 152, 219, 0.05));
  border-color: rgba(52, 152, 219, 0.3);
  box-shadow: 0 8px 24px rgba(52, 152, 219, 0.1);
}

.chart-row .chart-container.full-width {
  grid-column: 1 / -1;
  height: 360px;
  max-height: 360px;
}

.chart-title {
  margin: 0 0 12px 0;
  font-size: 1rem;
  font-weight: 700;
  color: white;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.chart-title::before {
  content: '';
  width: 4px;
  height: 20px;
  background: linear-gradient(180deg, #3498db, #2ecc71);
  border-radius: 2px;
}
.chart-row .chart-container > canvas {
  flex: 1;
  max-width: 100%;
  max-height: 100%;
}
.chart-row .chart-container {
  position: relative;
}

.recent-bookings {
  margin-top: 32px;
  padding: 0;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(20, 45, 70, 0.8), rgba(35, 65, 95, 0.8));
  border: 1.5px solid rgba(52, 152, 219, 0.25);
  overflow: hidden;
}

.bookings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.12), rgba(81, 207, 102, 0.08));
  border-bottom: 2px solid rgba(52, 152, 219, 0.2);
}

.bookings-title {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 800;
  color: white;
  display: flex;
  align-items: center;
  gap: 10px;
}

.bookings-count {
  background: rgba(52, 152, 219, 0.3);
  color: #3498db;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
  border: 1px solid rgba(52, 152, 219, 0.4);
}

.bookings-table-wrapper {
  padding: 0;
  overflow-x: auto;
}

.bookings-empty {
  padding: 40px 28px;
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
}

.bookings-empty i {
  font-size: 2.5rem;
  color: rgba(52, 152, 219, 0.3);
  margin-bottom: 12px;
  display: block;
}

.bookings-empty p {
  margin: 0;
  font-size: 1rem;
  font-weight: 500;
}

.bookings-table {
  width: 100%;
  border-collapse: collapse;
  background: transparent;
}

.bookings-table thead {
  background: linear-gradient(90deg, rgba(52, 152, 219, 0.2), rgba(52, 152, 219, 0.1));
  position: sticky;
  top: 0;
  z-index: 10;
}

.bookings-table th {
  padding: 18px 20px;
  text-align: left;
  font-weight: 800;
  color: white;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-bottom: 2px solid rgba(52, 152, 219, 0.3);
  background: linear-gradient(90deg, rgba(52, 152, 219, 0.15), rgba(52, 152, 219, 0.08));
}

.bookings-table tbody tr {
  transition: all 0.25s ease;
  border-bottom: 1px solid rgba(52, 152, 219, 0.1);
}

.bookings-table tbody tr:hover {
  background: linear-gradient(90deg, rgba(52, 152, 219, 0.15), rgba(52, 152, 219, 0.08));
  border-color: rgba(52, 152, 219, 0.3);
}

.bookings-table tbody tr:hover td {
  color: white;
  box-shadow: inset 2px 0 0 rgba(52, 152, 219, 0.3);
}

.bookings-table td {
  padding: 16px 20px;
  color: rgba(255, 255, 255, 0.85);
  font-size: 0.9rem;
  font-weight: 500;
  vertical-align: middle;
}

.cell-date {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

.cell-time {
  color: rgba(255, 255, 255, 0.8);
  font-family: 'Courier New', monospace;
  font-weight: 500;
}

.cell-duration {
  color: #74c0fc;
  font-weight: 700;
}

.cell-amount {
  color: #51cf66;
  font-weight: 800;
  font-size: 1rem;
  text-shadow: 0 0 8px rgba(81, 207, 102, 0.25);
}
.analytics-section {
  margin-bottom: 40px;
  margin-top: 20px;
}

.analytics-section h2 {
  color: #ecf0f1;
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 25px;
  text-transform: uppercase;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.analytics-section h2 i {
  color: #3498db;
  font-size: 1.8rem;
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.analytics-card {
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  padding: 24px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.analytics-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.3);
  transform: translateY(-2px);
}

.analytics-card.full-width {
  grid-column: 1 / -1;
}

.analytics-title {
  color: #ecf0f1;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.analytics-title i {
  font-size: 1.3rem;
  min-width: 24px;
}

.analytics-card canvas {
  max-width: 100%;
  height: auto;
}
@media (max-width: 1200px) {
  .analytics-grid {
    grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  }
}

@media (max-width: 768px) {
  .analytics-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .analytics-card {
    padding: 18px;
  }

  .analytics-section h2 {
    font-size: 1.3rem;
  }

  .analytics-title {
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .analytics-section h2 {
    font-size: 1.1rem;
  }

  .analytics-card {
    padding: 16px;
  }

  .analytics-title {
    font-size: 0.95rem;
    gap: 6px;
  }

  .analytics-title i {
    font-size: 1.1rem;
  }
}
.detailed-report-section {
  margin-bottom: 40px;
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  overflow: hidden;
  animation: slideIn 0.4s ease;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.table-controls {
  display: flex;
  gap: 14px;
  align-items: center;
  margin-left: auto;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.download-btn {
  background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
  border: none;
  color: white;
  padding: 11px 18px;
  border-radius: 9px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.25);
}

.download-btn:hover {
  background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.35);
}

.download-btn:active {
  transform: translateY(0);
}

.download-lot-btn {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  border: none;
  color: white;
  padding: 12px 20px;
  border-radius: 9px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 4px 14px rgba(52, 152, 219, 0.3);
}

.download-lot-btn:hover {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 22px rgba(52, 152, 219, 0.4);
}

.download-lot-btn:active {
  transform: translateY(0);
}

.btn-download-top {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  border: none;
  color: white;
  padding: 14px 24px;
  border-radius: 10px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 4px 14px rgba(52, 152, 219, 0.3);
  white-space: nowrap;
  flex-shrink: 0;
}

.btn-download-top:hover {
  background: linear-gradient(135deg, #2980b9 0%, #1f618d 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 22px rgba(52, 152, 219, 0.4);
}

.btn-download-top:active {
  transform: translateY(0);
}

.search-input {
  background: rgba(255, 255, 255, 0.08);
  border: 1.5px solid rgba(52, 152, 219, 0.25);
  color: white;
  padding: 11px 16px;
  border-radius: 9px;
  font-size: 0.9rem;
  min-width: 200px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.45);
  font-weight: 400;
}

.search-input:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.14);
  border-color: rgba(52, 152, 219, 0.6);
  box-shadow: 0 0 16px rgba(52, 152, 219, 0.25), inset 0 1px 2px rgba(255, 255, 255, 0.1);
  color: #e0f2fe;
}

.sort-select {
  background: rgba(255, 255, 255, 0.08);
  border: 1.5px solid rgba(52, 152, 219, 0.25);
  color: white;
  padding: 11px 14px;
  border-radius: 9px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-width: 160px;
  font-weight: 500;
}

.sort-select:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.14);
  border-color: rgba(52, 152, 219, 0.6);
  box-shadow: 0 0 16px rgba(52, 152, 219, 0.25), inset 0 1px 2px rgba(255, 255, 255, 0.1);
}

.sort-select option {
  background: #1a2f42;
  color: white;
  padding: 8px 12px;
}

.sort-select option:hover {
  background: #2a4f62;
}

.table-wrapper {
  overflow-x: auto;
  padding: 0;
  -webkit-overflow-scrolling: touch;
}

.table-wrapper::-webkit-scrollbar {
  height: 8px;
}

.table-wrapper::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.04);
}

.table-wrapper::-webkit-scrollbar-thumb {
  background: rgba(52, 152, 219, 0.3);
  border-radius: 4px;
}

.table-wrapper::-webkit-scrollbar-thumb:hover {
  background: rgba(52, 152, 219, 0.5);
}

.slots-report-table {
  width: 100%;
  border-collapse: collapse;
  background: transparent;
  font-size: 0.95rem;
}

.slots-report-table thead {
  background: linear-gradient(90deg, rgba(52, 152, 219, 0.3), rgba(81, 207, 102, 0.2));
  position: sticky;
  top: 0;
  z-index: 15;
  border-bottom: 2px solid rgba(52, 152, 219, 0.5);
}

.slots-report-table th {
  padding: 18px 22px;
  text-align: left;
  font-weight: 800;
  color: #e0f2fe;
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 1.3px;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  background: linear-gradient(90deg, rgba(52, 152, 219, 0.25), rgba(52, 152, 219, 0.15));
}

.slots-report-table th:last-child {
  border-right: none;
}

.slots-report-table tbody tr {
  transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
  border-bottom: 1px solid rgba(52, 152, 219, 0.1);
  position: relative;
}

.slots-report-table tbody tr::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 3px;
  background: transparent;
  transition: all 0.28s ease;
}

.slots-report-table tbody tr:hover {
  background: linear-gradient(90deg, rgba(52, 152, 219, 0.15), rgba(81, 207, 102, 0.1));
  border-color: rgba(52, 152, 219, 0.35);
  box-shadow: inset 3px 0 12px rgba(52, 152, 219, 0.15);
}

.slots-report-table tbody tr:hover::before {
  background: linear-gradient(180deg, #3498db, #2ecc71);
  width: 4px;
}

.slots-report-table td {
  padding: 16px 22px;
  color: rgba(255, 255, 255, 0.85);
  font-weight: 500;
  vertical-align: middle;
  border-right: 1px solid rgba(255, 255, 255, 0.04);
}

.slots-report-table td:last-child {
  border-right: none;
}

.slots-report-table tbody tr:hover td {
  color: white;
}

.cell-spot {
  color: #3498db;
  font-weight: 800;
  font-size: 1.05rem;
  text-shadow: 0 0 8px rgba(52, 152, 219, 0.2);
}

.cell-status {
  font-weight: 600;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 22px;
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.status-badge.occupied {
  background: linear-gradient(135deg, rgba(231, 76, 60, 0.25), rgba(231, 76, 60, 0.15));
  color: #ff7675;
  border: 1.5px solid rgba(231, 76, 60, 0.5);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.15);
}

.status-badge.occupied:hover {
  background: linear-gradient(135deg, rgba(231, 76, 60, 0.35), rgba(231, 76, 60, 0.25));
  border-color: rgba(231, 76, 60, 0.7);
  box-shadow: 0 6px 16px rgba(231, 76, 60, 0.25);
}

.status-badge.available {
  background: linear-gradient(135deg, rgba(46, 204, 113, 0.25), rgba(46, 204, 113, 0.15));
  color: #51cf66;
  border: 1.5px solid rgba(46, 204, 113, 0.5);
  box-shadow: 0 4px 12px rgba(46, 204, 113, 0.15);
}

.status-badge.available:hover {
  background: linear-gradient(135deg, rgba(46, 204, 113, 0.35), rgba(46, 204, 113, 0.25));
  border-color: rgba(46, 204, 113, 0.7);
  box-shadow: 0 6px 16px rgba(46, 204, 113, 0.25);
}

.cell-bookings {
  color: #74c0fc;
  font-weight: 700;
  font-size: 1.02rem;
  text-shadow: 0 0 8px rgba(116, 192, 252, 0.2);
}

.cell-revenue {
  color: #51cf66;
  font-weight: 800;
  font-size: 1.08rem;
  text-shadow: 0 0 10px rgba(81, 207, 102, 0.3);
}

.cell-avg-revenue {
  color: #ffd93d;
  font-weight: 800;
  font-size: 1.05rem;
  text-shadow: 0 0 8px rgba(255, 217, 61, 0.25);
}

.cell-occupancy {
  max-width: 130px;
  min-width: 110px;
}

.occupancy-bar {
  position: relative;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.04), rgba(52, 152, 219, 0.08));
  border: 1.5px solid rgba(52, 152, 219, 0.25);
  border-radius: 10px;
  height: 32px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.occupancy-bar:hover {
  border-color: rgba(52, 152, 219, 0.4);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2), 0 4px 12px rgba(52, 152, 219, 0.15);
}

.occupancy-fill {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  background: linear-gradient(90deg, rgba(52, 152, 219, 0.4), rgba(52, 152, 219, 0.7));
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 9px;
  box-shadow: inset 1px 0 3px rgba(255, 255, 255, 0.3), 0 0 12px rgba(52, 152, 219, 0.2);
}

.occupancy-text {
  position: relative;
  z-index: 2;
  color: white;
  font-weight: 800;
  font-size: 0.85rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  letter-spacing: 0.5px;
}

.cell-last-used {
  color: rgba(255, 255, 255, 0.75);
  font-weight: 500;
  font-size: 0.9rem;
  font-family: 'Courier New', monospace;
  letter-spacing: 0.3px;
}

.empty-state {
  text-align: center;
  padding: 60px 40px;
  color: rgba(255, 255, 255, 0.5);
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.04), rgba(81, 207, 102, 0.04));
  border-top: 1px solid rgba(52, 152, 219, 0.1);
}

.empty-state i {
  font-size: 3rem;
  color: rgba(52, 152, 219, 0.25);
  margin-bottom: 16px;
  display: block;
  opacity: 0.7;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
}

.empty-state p {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 500;
  letter-spacing: 0.3px;
}
@media (max-width: 1200px) {
  .report-summary {
    grid-template-columns: repeat(2, 1fr);
  }

  .chart-row {
    grid-template-columns: 1fr;
  }

  .chart-row .chart-container {
    height: 360px;
    max-height: 360px;
  }

  .chart-row .chart-container.full-width {
    height: 380px;
    max-height: 380px;
  }
}

@media (max-width: 768px) {
  .navbar-menu {
    gap: 15px;
    margin-left: 20px;
  }

  .welcome-title {
    font-size: 2rem;
  }

  .welcome-header {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }

  .btn-download-top {
    width: 100%;
    justify-content: center;
  }

  .welcome-text {
    text-align: center;
  }

  .lots-grid,
  .slots-grid {
    grid-template-columns: 1fr;
  }

  .report-summary {
    grid-template-columns: 1fr;
  }

  .modal-card {
    border-radius: 8px;
  }

  .modal-header {
    padding: 16px;
  }

  .chart-row .chart-container {
    height: 300px;
    max-height: 300px;
  }

  .chart-row .chart-container.full-width {
    height: 320px;
    max-height: 320px;
  }

  .chart-title {
    font-size: 0.9rem;
    margin-bottom: 8px;
  }

  .modal-content {
    padding: 16px;
  }

  .bookings-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
    padding: 16px 20px;
  }

  .bookings-title {
    font-size: 1rem;
  }

  .bookings-count {
    font-size: 0.75rem;
    padding: 4px 10px;
  }

  .bookings-table th,
  .bookings-table td {
    padding: 12px 14px;
    font-size: 0.8rem;
  }

  .bookings-table th {
    font-size: 0.7rem;
  }

  .bookings-empty {
    padding: 30px 20px;
  }

  .bookings-empty i {
    font-size: 2rem;
  }

  .bookings-empty p {
    font-size: 0.9rem;
  }
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: linear-gradient(135deg, rgba(44, 62, 80, 0.95) 0%, rgba(52, 73, 94, 0.95) 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from { transform: translateY(30px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.2);
}

.modal-header h3 {
  color: #ecf0f1;
  font-size: 1.3rem;
  font-weight: 700;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-header i {
  color: #3498db;
  font-size: 1.4rem;
}

.modal-close {
  background: none;
  border: none;
  color: #95a5a6;
  font-size: 1.5rem;
  cursor: pointer;
  transition: all 0.3s;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}

.modal-close:hover {
  background: rgba(52, 152, 219, 0.2);
  color: #3498db;
  transform: rotate(90deg);
}

.modal-body {
  padding: 24px;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

.detail-item {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(52, 152, 219, 0.15);
  padding: 16px;
  border-radius: 10px;
  transition: all 0.3s;
}

.detail-item:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(52, 152, 219, 0.3);
}

.detail-item label {
  display: block;
  color: #95a5a6;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.detail-item span {
  color: #ecf0f1;
  font-size: 1rem;
  font-weight: 600;
  display: block;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.1);
  justify-content: flex-end;
}

.download-btn-modal {
  background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
  border: none;
  color: white;
  padding: 11px 18px;
  border-radius: 9px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.25);
}

.download-btn-modal:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.35);
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ecf0f1;
  padding: 11px 18px;
  border-radius: 9px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 600;
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

.spot-detail-modal {
  max-width: 550px;
}

@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }

  .modal-footer {
    flex-direction: column-reverse;
  }

  .download-btn-modal,
  .cancel-btn {
    width: 100%;
  }
}
</style>