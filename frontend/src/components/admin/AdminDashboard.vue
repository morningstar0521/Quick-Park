<template>
  <div class="admin-dashboard">
    <nav class="admin-navbar">
      <div class="navbar-content">
        <div class="navbar-brand">
          <span>Quick Park</span>
        </div>
        <div class="navbar-menu">
          <a class="nav-item active" @click="$emit('switchView','AdminDashboard')">
            <i class="fas fa-tachometer-alt me-2"></i>Dashboard
          </a>
          <a class="nav-item" @click="$emit('switchView','ManageParkingLots')">
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
          <span class="user-name"><i class="fas fa-user-circle me-2"></i>{{ userName }}</span>
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
          <h1 class="welcome-title">Dashboard</h1>
          <p class="welcome-subtitle">Real-time parking system analytics</p>
        </div>

        <div class="metrics-section">
          <div class="metrics-grid-top">
            <div class="metric-card-large blue-card">
              <div class="metric-header">
                <i class="fas fa-map-marker-alt"></i>
                <span>Total Parking Lots</span>
              </div>
              <div class="metric-large-value">{{ metrics.parkingLots }}</div>
              <div class="metric-subtext">Active across city</div>
            </div>

            <div class="metric-card-large green-card">
              <div class="metric-header">
                <i class="fas fa-parking"></i>
                <span>Available Spots</span>
              </div>
              <div class="metric-large-value">{{ metrics.availableSpots }}</div>
              <div class="metric-subtext">Out of {{ metrics.totalSpots }} total</div>
            </div>

            <div class="metric-card-large purple-card">
              <div class="metric-header">
                <i class="fas fa-rupee-sign"></i>
                <span>Today's Revenue</span>
              </div>
              <div class="metric-large-value">₹{{ metrics.revenueToday }}</div>
              <div class="metric-subtext">24-hour earnings</div>
            </div>
          </div>

          <div class="metrics-grid-secondary">
            <div class="metric-card-secondary">
              <div class="secondary-header">
                <i class="fas fa-users"></i>
                <span>Registered Users</span>
              </div>
              <div class="secondary-value">{{ metrics.registeredUsers }}</div>
            </div>

            <div class="metric-card-secondary">
              <div class="secondary-header">
                <i class="fas fa-chart-line"></i>
                <span>Total Revenue</span>
              </div>
              <div class="secondary-value">₹{{ metrics.totalRevenue }}</div>
            </div>

            <div class="metric-card-secondary">
              <div class="secondary-header">
                <i class="fas fa-check-circle"></i>
                <span>Completed Bookings</span>
              </div>
              <div class="secondary-value">{{ metrics.completedBookings }}</div>
            </div>
          </div>
        </div>

        <div class="content-section">
          <div class="chart-container">
            <div class="card-header">
              <h3><i class="fas fa-chart-line me-2"></i>Revenue Trend</h3>
            </div>
            <div class="chart-inner large-chart">
              <canvas id="revenueChart" ref="revenueChart"></canvas>
            </div>
          </div>

          <div class="chart-container">
            <div class="card-header">
              <h3><i class="fas fa-chart-bar me-2"></i>Parking Lots Revenue Comparison</h3>
            </div>
            <div class="chart-inner large-chart">
              <canvas id="lotsComparisonChart" ref="lotsComparisonChart"></canvas>
            </div>
          </div>
        </div>

        <div class="table-section">
          <div class="card-header">
            <h3><i class="fas fa-list me-2"></i>Recent Bookings</h3>
            <span class="badge-info">Last 24 hours</span>
          </div>
          <div class="table-container">
            <table class="bookings-table">
              <thead>
                <tr>
                  <th>Booking ID</th>
                  <th>User</th>
                  <th>Lot</th>
                  <th>Check-in</th>
                  <th>Duration</th>
                  <th>Amount</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="recentBookings.length === 0">
                  <td colspan="7" class="text-center">No bookings in the last 24 hours</td>
                </tr>
                <tr v-for="booking in recentBookings.slice(0, 5)" :key="booking.id">
                  <td><span class="booking-id">{{ booking.id }}</span></td>
                  <td>{{ booking.user }}</td>
                  <td>{{ booking.lot }}</td>
                  <td>{{ booking.checkIn }}</td>
                  <td>{{ booking.duration }}</td>
                  <td>₹{{ booking.amount }}</td>
                  <td><span class="status-badge" :class="booking.status">{{ booking.status }}</span></td>
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
      pointRadius: (chartType === 'line' || ds.type === 'line') ? (ds.pointRadius !== undefined ? ds.pointRadius : 4) : undefined,
      pointHoverRadius: (chartType === 'line' || ds.type === 'line') ? (ds.pointHoverRadius !== undefined ? ds.pointHoverRadius : 6) : undefined,
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
  name: "AdminDashboard",
  inject: {
    emitter: { default: null }
  },
  props: {
    initialData: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      userName: this.initialData.user?.full_name || "System Admin",
      metrics: {
        parkingLots: 0,
        totalSpots: 0,
        availableSpots: 0,
        registeredUsers: 0,
        activeBookings: 0,
        revenueToday: 0,
        totalRevenue: 0,
        completedBookings: 0
      },
      recentBookings: [],
      parkingLots: [],
      charts: {
        occupancy: null,
        revenue: null,
        lotsComparison: null
      }
    };
  },
  created() {
    this.fetchMetrics();
    this.fetchRecentBookings();
    this.fetchParkingLots();
    if (this.emitter) {
      this.emitter.on("parkingLotChanged", this.refreshMetrics);
    }
  },
  mounted() {
    console.log("AdminDashboard mounted, initializing charts");
    this.$nextTick(() => {
      setTimeout(() => {
        console.log("Calling renderCharts after 100ms delay");
        this.renderCharts();
        this.renderLotsComparisonChart();
      }, 100);
    });
  },
  beforeUnmount() {
    if (this.emitter) {
      this.emitter.off("parkingLotChanged");
    }
    if (this.charts.occupancy) this.charts.occupancy.destroy();
    if (this.charts.revenue) this.charts.revenue.destroy();
    if (this.charts.lotsComparison) this.charts.lotsComparison.destroy();
  },
  methods: {
    async fetchMetrics() {
      try {
        const response = await axios.get("http://127.0.0.1:5000/api/admin/metrics");
        if (response.data.ok) {
          this.metrics = response.data.metrics;
        } else {
          console.error("Error fetching metrics:", response.data.message);
        }
      } catch (err) {
        console.error("Error fetching metrics:", err);
        if (err.response && err.response.status === 401) {
          this.logout(true);
        }
      }
    },

    async fetchRecentBookings() {
      try {
        const response = await axios.get("http://127.0.0.1:5000/api/admin/recent-bookings", {
          headers: {
            "Authorization": `Bearer ${localStorage.getItem('accessToken')}`
          }
        });
        if (response.data.ok) {
          this.recentBookings = response.data.data;
        } else {
          console.warn("Could not fetch bookings:", response.data.message);
          this.recentBookings = [
            { id: "BK001", user: "John Doe", lot: "Lot A", checkIn: "09:15 AM", duration: "2h 30m", amount: 50, status: "active" },
            { id: "BK002", user: "Jane Smith", lot: "Lot B", checkIn: "10:45 AM", duration: "1h 15m", amount: 30, status: "completed" },
            { id: "BK003", user: "Mike Johnson", lot: "Lot C", checkIn: "11:20 AM", duration: "3h", amount: 75, status: "active" }
          ];
        }
      } catch (err) {
        console.error("Error fetching bookings:", err);
        this.recentBookings = [
          { id: "BK001", user: "John Doe", lot: "Lot A", checkIn: "09:15 AM", duration: "2h 30m", amount: 50, status: "active" },
          { id: "BK002", user: "Jane Smith", lot: "Lot B", checkIn: "10:45 AM", duration: "1h 15m", amount: 30, status: "completed" },
          { id: "BK003", user: "Mike Johnson", lot: "Lot C", checkIn: "11:20 AM", duration: "3h", amount: 75, status: "active" }
        ];
      }
    },

    renderCharts() {
      this.renderRevenueChart();
      this.renderLotsComparisonChart();
    },

    async renderOccupancyChart() {
      try {
        const response = await axios.get("http://127.0.0.1:5000/api/admin/occupancy-data", {
          headers: {
            "Authorization": `Bearer ${localStorage.getItem('accessToken')}`
          }
        });

        const canvas = this.$refs.occupancyChart;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        if (this.charts.occupancy) this.charts.occupancy.destroy();

        let occupancyData = response.data.ok ? response.data.data : [];
        
        if (occupancyData.length === 0) {
          occupancyData = [
            { name: 'Lot A', occupancy: 75 },
            { name: 'Lot B', occupancy: 45 },
            { name: 'Lot C', occupancy: 60 }
          ];
        }

        const displayData = occupancyData.slice(0, 8);

        const occupancyLabels = displayData.map(lot => lot.name || `Lot ${displayData.indexOf(lot) + 1}`);
        const occupancyValues = displayData.map(lot => lot.occupancy || 0);
        const colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#34495e'];
        const bgColors = displayData.map((_, i) => colors[i % colors.length]);
        const borderColors = displayData.map((_, i) => {
          const darkColors = ['#2980b9', '#27ae60', '#c0392b', '#d68910', '#8e44ad', '#16a085', '#d35400', '#2c3e50'];
          return darkColors[i % darkColors.length];
        });

        const config = createChartConfig('bar', occupancyLabels, [{
          label: 'Occupancy Rate (%)',
          data: occupancyValues,
          backgroundColor: bgColors,
          borderColor: borderColors,
          borderWidth: 2,
          borderRadius: 8,
          clip: false,
          fill: false
        }], {
          indexAxis: 'y',
          layout: {
            padding: 0
          },
          plugins: {
            legend: {
              display: true,
              labels: {
                font: { size: 12, weight: '600' },
                padding: 15,
                usePointStyle: true,
                color: 'white'
              }
            },
            tooltip: {
              backgroundColor: 'rgba(0,0,0,0.8)',
              padding: 12,
              titleFont: { size: 14 },
              bodyFont: { size: 12 },
              callbacks: {
                label: function(context) {
                  return 'Occupancy: ' + Math.round(context.parsed.x) + '%';
                }
              }
            }
          },
          scales: {
            x: {
              type: 'linear',
              beginAtZero: true,
              max: 100,
              clip: {
                left: false,
                top: false,
                right: false,
                bottom: false
              },
              ticks: {
                color: 'rgba(255,255,255,0.8)',
                font: { size: 11 },
                callback: function(value) {
                  return value + '%';
                }
              },
              grid: {
                color: 'rgba(255,255,255,0.1)'
              }
            },
            y: {
              clip: {
                left: false,
                top: false,
                right: false,
                bottom: false
              },
              ticks: {
                color: 'rgba(255,255,255,0.9)',
                font: { size: 12, weight: '600' }
              },
              grid: {
                display: false
              }
            }
          }
        });

        this.charts.occupancy = new ChartJS(ctx, config);
      } catch (err) {
        console.error("Error rendering occupancy chart:", err);
        this.renderOccupancyChartFallback();
      }
    },

    renderOccupancyChartFallback() {
      try {
        const canvas = this.$refs.occupancyChart;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        if (this.charts.occupancy) this.charts.occupancy.destroy();

        const fallbackData = [
          { name: 'Lot A', occupancy: 75 },
          { name: 'Lot B', occupancy: 45 },
          { name: 'Lot C', occupancy: 60 },
          { name: 'Lot D', occupancy: 90 },
          { name: 'Lot E', occupancy: 35 }
        ];

        const labels = fallbackData.map(lot => lot.name);
        const config = createChartConfig('bar', labels, [{
          label: 'Occupancy Rate (%)',
          data: fallbackData.map(lot => lot.occupancy),
          backgroundColor: ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6'],
          borderColor: ['#2980b9', '#27ae60', '#c0392b', '#d68910', '#8e44ad'],
          borderWidth: 2,
          borderRadius: 8,
          clip: false,
          fill: false
        }], {
          indexAxis: 'y',
          layout: {
            padding: 0
          },
          plugins: {
            legend: {
              display: true,
              labels: {
                font: { size: 12, weight: '600' },
                padding: 15,
                usePointStyle: true,
                color: 'white'
              }
            },
            tooltip: {
              backgroundColor: 'rgba(0,0,0,0.8)',
              padding: 12,
              titleFont: { size: 14 },
              bodyFont: { size: 12 }
            }
          },
          scales: {
            x: {
              type: 'linear',
              beginAtZero: true,
              max: 100,
              clip: {
                left: false,
                top: false,
                right: false,
                bottom: false
              },
              ticks: {
                color: 'rgba(255,255,255,0.8)',
                font: { size: 11 },
                callback: function(value) {
                  return value + '%';
                }
              },
              grid: {
                color: 'rgba(255,255,255,0.1)'
              }
            },
            y: {
              clip: {
                left: false,
                top: false,
                right: false,
                bottom: false
              },
              ticks: {
                color: 'rgba(255,255,255,0.9)',
                font: { size: 12, weight: '600' }
              },
              grid: {
                display: false
              }
            }
          }
        });

        this.charts.occupancy = new ChartJS(ctx, config);
      } catch (err) {
        console.error("Error rendering occupancy chart fallback:", err);
      }
    },

    async renderRevenueChart() {
      try {
        const response = await axios.get("http://127.0.0.1:5000/api/admin/revenue-data", {
          headers: {
            "Authorization": `Bearer ${localStorage.getItem('accessToken')}`
          }
        });

        const canvas = this.$refs.revenueChart;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        if (this.charts.revenue) this.charts.revenue.destroy();

        let revenueData = response.data.ok ? response.data.data : [];
        
        if (revenueData.length === 0) {
          revenueData = [
            { date: 'Mon', revenue: 2500 },
            { date: 'Tue', revenue: 3200 },
            { date: 'Wed', revenue: 2800 },
            { date: 'Thu', revenue: 4100 },
            { date: 'Fri', revenue: 3600 },
            { date: 'Sat', revenue: 4800 },
            { date: 'Sun', revenue: 5200 }
          ];
        }

        const labels = revenueData.map(d => d.date);
        const config = createChartConfig('line', labels, [{
          label: 'Revenue (₹)',
          data: revenueData.map(d => d.revenue),
          borderColor: '#2ecc71',
          backgroundColor: 'rgba(46, 204, 113, 0.1)',
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#2ecc71',
          pointBorderColor: '#27ae60',
          pointBorderWidth: 2,
          pointRadius: 5,
          pointHoverRadius: 7,
          clip: false
        }], {
          layout: {
            padding: 0
          },
          plugins: {
            legend: {
              labels: {
                font: { size: 12, weight: '600' },
                padding: 15,
                usePointStyle: true
              }
            },
            tooltip: {
              backgroundColor: 'rgba(0,0,0,0.8)',
              padding: 12,
              titleFont: { size: 14 },
              bodyFont: { size: 12 },
              callbacks: {
                label: function(context) {
                  return '₹' + context.parsed.y.toLocaleString('en-IN');
                }
              }
            }
          },
          scales: {
            x: {
              type: 'category',
              clip: {
                left: false,
                top: false,
                right: false,
                bottom: false
              }
            },
            y: {
              type: 'linear',
              beginAtZero: true,
              clip: {
                left: false,
                top: false,
                right: false,
                bottom: false
              },
              ticks: {
                callback: function(value) {
                  return '₹' + value.toLocaleString('en-IN');
                }
              }
            }
          }
        });

        this.charts.revenue = new ChartJS(ctx, config);
      } catch (err) {
        console.error("Error rendering revenue chart:", err);
        this.renderRevenueChartFallback();
      }
    },

    renderRevenueChartFallback() {
      try {
        const canvas = this.$refs.revenueChart;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        if (this.charts.revenue) this.charts.revenue.destroy();

        const fallbackData = [
          { date: 'Mon', revenue: 2500 },
          { date: 'Tue', revenue: 3200 },
          { date: 'Wed', revenue: 2800 },
          { date: 'Thu', revenue: 4100 },
          { date: 'Fri', revenue: 3600 },
          { date: 'Sat', revenue: 4800 },
          { date: 'Sun', revenue: 5200 }
        ];

        const labels = fallbackData.map(d => d.date);
        const config = createChartConfig('line', labels, [{
          label: 'Revenue (₹)',
          data: fallbackData.map(d => d.revenue),
          borderColor: '#2ecc71',
          backgroundColor: 'rgba(46, 204, 113, 0.1)',
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#2ecc71',
          pointBorderColor: '#27ae60',
          pointBorderWidth: 2,
          pointRadius: 5,
          pointHoverRadius: 7,
          clip: false
        }], {
          layout: {
            padding: 0
          },
          plugins: {
            legend: {
              labels: {
                font: { size: 12, weight: '600' },
                padding: 15,
                usePointStyle: true
              }
            },
            tooltip: {
              backgroundColor: 'rgba(0,0,0,0.8)',
              padding: 12,
              titleFont: { size: 14 },
              bodyFont: { size: 12 }
            }
          },
          scales: {
            x: {
              type: 'category',
              clip: {
                left: false,
                top: false,
                right: false,
                bottom: false
              }
            },
            y: {
              type: 'linear',
              beginAtZero: true,
              clip: {
                left: false,
                top: false,
                right: false,
                bottom: false
              },
              ticks: {
                callback: function(value) {
                  return '₹' + value;
                }
              }
            }
          }
        });

        this.charts.revenue = new ChartJS(ctx, config);
      } catch (err) {
        console.error("Error rendering revenue chart fallback:", err);
      }
    },

    async fetchParkingLots() {
      try {
        const response = await axios.get("http://127.0.0.1:5000/api/admin/parking-lots", {
          headers: {
            "Authorization": `Bearer ${localStorage.getItem('accessToken')}`
          }
        });
        console.log("Parking lots response:", response.data);
        if (response.data.ok) {
          this.parkingLots = response.data.data;
          console.log("Parking lots fetched:", this.parkingLots);
          this.$nextTick(() => {
            this.renderLotsComparisonChart();
          });
        } else {
          this.fetchParkingLotsAlternative();
        }
      } catch (err) {
        console.error("Error fetching parking lots:", err);
        this.fetchParkingLotsAlternative();
      }
    },

    async fetchParkingLotsAlternative() {
      try {
        const response = await axios.get("http://127.0.0.1:5000/api/parking-lots", {
          headers: {
            "Authorization": `Bearer ${localStorage.getItem('accessToken')}`
          }
        });
        console.log("Alternative parking lots response:", response.data);
        if (response.data.ok || Array.isArray(response.data)) {
          this.parkingLots = Array.isArray(response.data) ? response.data : response.data.data || [];
          console.log("Parking lots fetched (alternative):", this.parkingLots);
          this.$nextTick(() => {
            this.renderLotsComparisonChart();
          });
        }
      } catch (err) {
        console.error("Error fetching parking lots (alternative):", err);
      }
    },

    renderLotsComparisonChart() {
      try {
        console.log("renderLotsComparisonChart called, parkingLots:", this.parkingLots);
        
        const canvas = this.$refs.lotsComparisonChart;
        console.log("Canvas ref:", canvas);
        
        if (!canvas) {
          console.warn("Canvas element not found");
          return;
        }
        let lotsData = this.parkingLots && this.parkingLots.length > 0 
          ? this.parkingLots 
          : [
              { name: 'Lot A', total_revenue: 15000 },
              { name: 'Lot B', total_revenue: 22000 },
              { name: 'Lot C', total_revenue: 18500 },
              { name: 'Lot D', total_revenue: 31000 }
            ];

        const ctx = canvas.getContext('2d');
        if (!ctx) {
          console.warn("Could not get 2D context");
          return;
        }

        if (this.charts.lotsComparison) this.charts.lotsComparison.destroy();
        const labels = lotsData.map(lot => lot.name || lot.lot_name || 'Unknown');
        const revenues = lotsData.map(lot => {
          const revenue = lot.revenueGenerated || lot.total_revenue || 0;
          return typeof revenue === 'number' ? revenue : 0;
        });
        
        console.log("Chart labels:", labels, "revenues:", revenues);

        if (revenues.length === 0) {
          console.warn("No revenue data available");
          return;
        }

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
          fill: false,
          clip: false
        }], {
          layout: {
            padding: 0
          },
          plugins: {
            legend: {
              display: true,
              labels: {
                font: { size: 12, weight: '600' },
                padding: 15,
                usePointStyle: true,
                color: 'white'
              }
            },
            tooltip: {
              backgroundColor: 'rgba(0,0,0,0.8)',
              padding: 12,
              titleFont: { size: 14 },
              bodyFont: { size: 12 },
              callbacks: {
                label: function(context) {
                  return '₹' + context.parsed.y.toLocaleString('en-IN');
                }
              }
            }
          },
          scales: {
            x: {
              type: 'category',
              clip: {
                left: false,
                top: false,
                right: false,
                bottom: false
              },
              ticks: {
                color: 'rgba(255,255,255,0.9)',
                font: { size: 11 }
              },
              grid: {
                display: false
              }
            },
            y: {
              type: 'linear',
              beginAtZero: true,
              clip: {
                left: false,
                top: false,
                right: false,
                bottom: false
              },
              ticks: {
                color: 'rgba(255,255,255,0.8)',
                font: { size: 11 },
                callback: function(value) {
                  return '₹' + value.toLocaleString('en-IN');
                }
              },
              grid: {
                color: 'rgba(255,255,255,0.1)'
              }
            }
          }
        });

        this.charts.lotsComparison = new ChartJS(ctx, config);
        console.log("Chart created successfully");
      } catch (err) {
        console.error("Error rendering lots comparison chart:", err);
      }
    },

    refreshMetrics() {
      this.fetchMetrics();
      this.renderCharts();
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
.admin-dashboard {
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
.metrics-section {
  margin-bottom: 40px;
}

.metrics-grid-top {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 22px;
  margin-bottom: 18px;
}
.metrics-grid-secondary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.metric-card-secondary {
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  padding: 18px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  color: white;
}

.metric-card-secondary:hover {
  transform: translateY(-6px);
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
}

.secondary-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.75);
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.secondary-header i {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
}

.secondary-value {
  font-size: 1.6rem;
  font-weight: 800;
  color: white;
  line-height: 1;
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

.metric-card-large.orange-card {
  border-left: 4px solid #e67e22;
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
}

.metric-large-value {
  font-size: 2.4rem;
  font-weight: 800;
  margin-bottom: 8px;
  line-height: 1;
}

.metric-subtext {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}
.content-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 40px;
}

.chart-container {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 0;
  transition: all 0.3s ease;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.chart-container.full-width {
  grid-column: 1 / -1;
}

.chart-container:hover {
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

.badge-info {
  background: rgba(52, 152, 219, 0.3);
  color: #87ceeb;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.chart-inner {
  padding: 24px;
  position: relative;
  height: 300px;
}

.chart-inner.large-chart {
  height: 400px;
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

.table-container {
  overflow-x: auto;
}

.bookings-table {
  width: 100%;
  border-collapse: collapse;
  color: white;
}

.bookings-table thead {
  background: rgba(0, 0, 0, 0.3);
  border-bottom: 2px solid rgba(52, 152, 219, 0.3);
}

.bookings-table th {
  padding: 16px 20px;
  text-align: left;
  font-weight: 700;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: rgba(255, 255, 255, 0.9);
}

.bookings-table td {
  padding: 14px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 0.9rem;
}

.bookings-table tbody tr {
  transition: background 0.2s ease;
}

.bookings-table tbody tr:hover {
  background: rgba(52, 152, 219, 0.1);
}

.booking-id {
  background: rgba(52, 152, 219, 0.3);
  color: #87ceeb;
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.85rem;
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

.status-badge.completed {
  background: rgba(52, 152, 219, 0.3);
  color: #3498db;
}

.status-badge.pending {
  background: rgba(230, 126, 34, 0.3);
  color: #e67e22;
}

.text-center {
  text-align: center;
  padding: 40px 20px !important;
  color: rgba(255, 255, 255, 0.6);
  font-style: italic;
}
.content-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}
@media (max-width: 1200px) {
  .navbar-menu {
    gap: 25px;
    margin-left: 40px;
  }

  .content-section {
    grid-template-columns: 1fr;
  }

  .metrics-grid-top {
    grid-template-columns: repeat(2, 1fr);
  }

  .metrics-grid-secondary {
    grid-template-columns: repeat(3, 1fr);
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

  .metrics-grid-top {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }

  .metrics-grid-secondary {
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
    margin-top: 14px;
  }

  .metric-card-large {
    padding: 20px;
  }

  .metric-large-value {
    font-size: 1.8rem;
  }

  .chart-inner {
    height: 250px;
  }

  .bookings-table th,
  .bookings-table td {
    padding: 12px 12px;
    font-size: 0.8rem;
  }

  .stat-box {
    padding: 18px;
  }

  .stat-icon {
    width: 60px;
    height: 60px;
    font-size: 1.5rem;
  }

  .stat-value {
    font-size: 1.4rem;
  }
}

@media (max-width: 480px) {
  .navbar-brand {
    font-size: 1.2rem;
  }

  .navbar-menu {
    gap: 8px;
  }

  .nav-item {
    padding: 6px 8px;
    font-size: 0.7rem;
  }

  .dashboard-wrapper {
    padding: 20px 10px;
  }

  .welcome-title {
    font-size: 1.6rem;
  }

  .welcome-subtitle {
    font-size: 0.85rem;
  }

  .metrics-grid-top {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .metrics-grid-secondary {
    grid-template-columns: 1fr;
    gap: 12px;
    margin-top: 12px;
  }

  .metric-card-secondary {
    padding: 14px;
  }

  .secondary-value {
    font-size: 1.4rem;
  }

  .metric-card-large {
    padding: 16px;
  }

  .metric-header {
    font-size: 0.8rem;
  }

  .metric-large-value {
    font-size: 1.6rem;
  }

  .chart-inner {
    height: 200px;
    padding: 16px;
  }

  .card-header {
    padding: 16px;
  }

  .card-header h3 {
    font-size: 1rem;
  }

  .bookings-table th,
  .bookings-table td {
    padding: 10px 8px;
    font-size: 0.7rem;
  }

  .stats-footer {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .stat-box {
    padding: 16px;
  }

  .stat-icon {
    width: 50px;
    height: 50px;
    font-size: 1.3rem;
  }

  .stat-value {
    font-size: 1.2rem;
  }

  .stat-label {
    font-size: 0.75rem;
  }
}
</style>
