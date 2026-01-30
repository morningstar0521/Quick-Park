<template>
  <div class="slot-detail-container">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
      <div class="container-fluid">
        <a class="navbar-brand fw-bold" href="#">Quick Park</a>
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item">
            <a class="nav-link" @click="goBackToReports">
              <i class="fas fa-arrow-left me-2"></i>Back to Reports
            </a>
          </li>
        </ul>
        <ul class="navbar-nav ms-auto">
          <li class="nav-item d-flex align-items-center me-3 text-white">
            <i class="fas fa-user-circle me-2"></i> Admin
          </li>
          <li class="nav-item">
            <button class="btn btn-outline-light btn-sm" @click="logout">
              Logout
            </button>
          </li>
        </ul>
      </div>
    </nav>

    <div class="dashboard-content">
      <div class="slot-header">
        <h2 class="section-title">
          <i class="fas fa-chart-line me-3"></i>Spot #{{ slotData?.spot_number }} - Detailed Analytics
        </h2>
        <p class="slot-subtitle">{{ lotData?.name }} - Comprehensive performance analysis</p>
      </div>

      <div class="summary-cards">
        <div class="summary-card">
          <div class="summary-icon">
            <i class="fas fa-calendar-check"></i>
          </div>
          <div class="summary-content">
            <div class="summary-value">{{ slotData?.total_bookings || 0 }}</div>
            <div class="summary-label">Total Bookings</div>
          </div>
        </div>
        
        <div class="summary-card">
          <div class="summary-icon">
            <i class="fas fa-rupee-sign"></i>
          </div>
          <div class="summary-content">
            <div class="summary-value">₹{{ (slotData?.total_revenue || 0).toFixed(2) }}</div>
            <div class="summary-label">Total Revenue</div>
          </div>
        </div>
        
        <div class="summary-card">
          <div class="summary-icon">
            <i class="fas fa-clock"></i>
          </div>
          <div class="summary-content">
            <div class="summary-value">{{ (slotData?.total_revenue / slotData?.total_bookings || 0).toFixed(2) }}</div>
            <div class="summary-label">Avg per Booking</div>
          </div>
        </div>
        
        <div class="summary-card">
          <div class="summary-icon">
            <i class="fas fa-chart-bar"></i>
          </div>
          <div class="summary-content">
            <div class="summary-value">{{ slotData?.is_booked ? 'Occupied' : 'Available' }}</div>
            <div class="summary-label">Current Status</div>
          </div>
        </div>
      </div>
      <div class="charts-section">
        <div class="chart-row">
          <div class="chart-container">
            <h4 class="chart-title">Booking Count Analysis</h4>
            <canvas id="bookingsBarChart" width="400" height="300"></canvas>
          </div>

          <div class="chart-container">
            <h4 class="chart-title">Revenue Distribution</h4>
            <canvas id="revenuePieChart" width="400" height="300"></canvas>
          </div>
        </div>

        <div class="chart-row">
          <div class="chart-container full-width">
            <h4 class="chart-title">Revenue Trend Over Time</h4>
            <canvas id="revenueLineChart" width="800" height="300"></canvas>
          </div>
        </div>

        <div class="chart-row">
          <div class="chart-container full-width">
            <h4 class="chart-title">Performance Comparison</h4>
            <canvas id="comparisonChart" width="800" height="300"></canvas>
          </div>
        </div>
      </div>

      <div class="bookings-section">
        <h3 class="subsection-title">Recent Bookings History</h3>
        <div class="bookings-table">
          <table class="table table-striped">
            <thead>
              <tr>
                <th>Booking ID</th>
                <th>Date</th>
                <th>Start Time</th>
                <th>End Time</th>
                <th>Duration</th>
                <th>Amount</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="booking in slotData?.recent_bookings || []" :key="booking.id">
                <td>{{ booking.id }}</td>
                <td>{{ formatDate(booking.start_time) }}</td>
                <td>{{ formatTime(booking.start_time) }}</td>
                <td>{{ booking.end_time ? formatTime(booking.end_time) : 'Active' }}</td>
                <td>{{ booking.duration_hours?.toFixed(1) }}h</td>
                <td class="text-success fw-bold">₹{{ booking.amount_paid?.toFixed(2) }}</td>
                <td>
                  <span class="status-badge" :class="{ 'active': !booking.end_time, 'completed': booking.end_time }">
                    {{ booking.end_time ? 'Completed' : 'Active' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';

export default {
  name: 'SlotDetailView',
  data() {
    return {
      slotData: null,
      lotData: null,
      charts: {}
    };
  },
  created() {
    this.loadSlotData();
  },
  mounted() {
    this.$nextTick(() => {
      this.renderAllCharts();
    });
  },
  methods: {
    async loadSlotData() {
      try {
        const slotId = this.$route.query.slotId;
        const lotId = this.$route.query.lotId;
        
        if (!slotId || !lotId) {
          alert('Missing slot or lot information');
          this.goBackToReports();
          return;
        }

        const token = localStorage.getItem('accessToken');
        
        const lotResponse = await this.$axios.get(`http://127.0.0.1:5000/api/parking-lots/${lotId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.lotData = lotResponse.data;

        const slotResponse = await this.$axios.get(`http://127.0.0.1:5000/api/admin/reports/slot/${slotId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (slotResponse.data.ok) {
          this.slotData = slotResponse.data.slot_data;
          this.lotData = slotResponse.data.lot_data;
          this.slotReports = slotResponse.data.lot_reports;
        } else {
          alert('Failed to load slot data');
          this.goBackToReports();
          return;
        }
      } catch (err) {
        console.error("Error loading slot data:", err);
        alert("Failed to load slot data");
        this.goBackToReports();
      }
    },

    renderAllCharts() {
      if (!this.slotData) return;
      
      this.renderBookingsBarChart();
      this.renderRevenuePieChart();
      this.renderRevenueLineChart();
      this.renderComparisonChart();
    },

    renderBookingsBarChart() {
      const ctx = document.getElementById('bookingsBarChart');
      if (!ctx) return;

      if (this.charts['bookingsBar']) {
        this.charts['bookingsBar'].destroy();
      }

      this.charts['bookingsBar'] = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Total Bookings'],
          datasets: [{
            label: 'Number of Bookings',
            data: [this.slotData.total_bookings],
            backgroundColor: '#4dabf7',
            borderColor: '#339af0',
            borderWidth: 2,
            borderRadius: 8,
            borderSkipped: false,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: 'rgba(0,0,0,0.1)' },
              ticks: { font: { size: 12 } }
            },
            x: {
              grid: { display: false },
              ticks: { font: { size: 12 } }
            }
          }
        }
      });
    },

    renderRevenuePieChart() {
      const ctx = document.getElementById('revenuePieChart');
      if (!ctx) return;

      if (this.charts['revenuePie']) {
        this.charts['revenuePie'].destroy();
      }

      const currentRevenue = this.slotData.total_revenue;
      const otherRevenue = Math.max(0, 1000 - currentRevenue);

      this.charts['revenuePie'] = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: [`Spot #${this.slotData.spot_number}`, 'Other Spots'],
          datasets: [{
            data: [currentRevenue, otherRevenue],
            backgroundColor: ['#4dabf7', '#e9ecef'],
            borderColor: '#fff',
            borderWidth: 2,
            hoverOffset: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: { font: { size: 12 }, padding: 20 }
            }
          }
        }
      });
    },

    renderRevenueLineChart() {
      const ctx = document.getElementById('revenueLineChart');
      if (!ctx) return;

      if (this.charts['revenueLine']) {
        this.charts['revenueLine'].destroy();
      }

      const bookings = this.slotData.recent_bookings || [];
      const monthlyData = {};
      
      bookings.forEach(booking => {
        const month = new Date(booking.start_time).toLocaleDateString('en-IN', { month: 'short', year: 'numeric' });
        if (!monthlyData[month]) {
          monthlyData[month] = 0;
        }
        monthlyData[month] += booking.amount_paid || 0;
      });

      const labels = Object.keys(monthlyData).sort();
      const data = labels.map(month => monthlyData[month]);

      if (labels.length === 0) {
        labels.push('Jan 2024', 'Feb 2024', 'Mar 2024', 'Apr 2024');
        data.push(0, 0, 0, 0);
      }

      this.charts['revenueLine'] = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'Monthly Revenue (₹)',
            data: data,
            borderColor: '#51cf66',
            backgroundColor: 'rgba(81, 207, 102, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#51cf66',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 6,
            pointHoverRadius: 8
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: 'rgba(0,0,0,0.1)' },
              ticks: {
                font: { size: 12 },
                callback: function(value) {
                  return '₹' + value;
                }
              }
            },
            x: {
              grid: { color: 'rgba(0,0,0,0.1)' },
              ticks: { font: { size: 12 } }
            }
          }
        }
      });
    },

    renderComparisonChart() {
      const ctx = document.getElementById('comparisonChart');
      if (!ctx) return;

      if (this.charts['comparison']) {
        this.charts['comparison'].destroy();
      }

      const currentRevenue = this.slotData.total_revenue;
      const avgRevenue = currentRevenue * 0.8; 

      this.charts['comparison'] = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: [`Spot #${this.slotData.spot_number}`, 'Average Spot'],
          datasets: [{
            label: 'Revenue (₹)',
            data: [currentRevenue, avgRevenue],
            backgroundColor: ['#4dabf7', '#51cf66'],
            borderColor: ['#339af0', '#40c057'],
            borderWidth: 2,
            borderRadius: 8,
            borderSkipped: false,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: 'rgba(0,0,0,0.1)' },
              ticks: {
                font: { size: 12 },
                callback: function(value) {
                  return '₹' + value;
                }
              }
            },
            x: {
              grid: { display: false },
              ticks: { font: { size: 12 } }
            }
          }
        }
      });
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('en-IN');
    },

    formatTime(dateString) {
      return new Date(dateString).toLocaleTimeString('en-IN', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
      });
    },

    goBackToReports() {
      this.$router.push('/reports');
    },

    logout() {
      localStorage.removeItem('accessToken');
      this.$router.push('/login');
    }
  },

  beforeUnmount() {
    Object.values(this.charts).forEach(chart => {
      if (chart && typeof chart.destroy === 'function') {
        chart.destroy();
      }
    });
  }
};
</script>

<style scoped>
.slot-detail-container {
  background-image: url('@/assets/car-bg.jpg');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  min-height: 100vh;
  position: relative;
}

.slot-detail-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 1;
}

.dashboard-content {
  padding: 2rem;
  position: relative;
  z-index: 2;
}

.slot-header {
  text-align: center;
  margin-bottom: 3rem;
  color: white;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: white;
}

.subsection-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

.slot-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  color: white;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.summary-card {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 1.5rem;
  transition: transform 0.3s ease;
}

.summary-card:hover {
  transform: translateY(-5px);
}

.summary-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #4dabf7, #339af0);
  color: white;
  font-size: 1.5rem;
}

.summary-content {
  flex: 1;
}

.summary-value {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.summary-label {
  font-size: 1rem;
  color: #6c757d;
  font-weight: 500;
}

.charts-section {
  margin: 3rem 0;
}

.chart-row {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.chart-container {
  flex: 1;
  min-width: 400px;
  background: white;
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.chart-container.full-width {
  flex: 100%;
  min-width: 100%;
}

.chart-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 1.5rem;
  text-align: center;
}

.chart-container canvas {
  max-height: 300px;
}

.bookings-section {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.bookings-table {
  overflow-x: auto;
}

.bookings-table .table {
  margin-bottom: 0;
}

.bookings-table th {
  background: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
  font-weight: 600;
  color: #2c3e50;
}

.bookings-table td {
  vertical-align: middle;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.completed {
  background: #cce5ff;
  color: #004085;
}

@media (max-width: 768px) {
  .dashboard-content {
    padding: 1rem;
  }
  
  .summary-cards {
    grid-template-columns: 1fr;
  }
  
  .chart-row {
    flex-direction: column;
  }
  
  .chart-container {
    min-width: 100%;
  }
  
  .section-title {
    font-size: 2rem;
  }
}
</style>
