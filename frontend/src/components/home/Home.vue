<!-- GanpatiBappa Morya -->
<template>
  <div class="home text-center d-flex flex-column justify-content-start align-items-center">
    <div class="overlay"></div>
    <img src="@/assets/logo.png" alt="Quick Park Logo" class="logo mt-5 mb-3" />
    <h1 class="display-3 fw-bold title">Welcome to Quick Park</h1>
    <p class="lead mt-2 subtitle">
      Smart 4-wheeler parking made simple & hassle-free 🚗
    </p>
    <p><b>Find, reserve, and park in seconds not circles.</b></p>
    <h5 class="mt-2 fst-italic">"Where your car rests, and your stress disappears. 🚘✨"</h5>
    <p>- Quick Park Team</p>

    <div class="mt-4">
      <button class="btn-modern btn btn-primary btn-lg m-2 px-4" @click="$emit('switchView','Login')">
        Login
      </button>
      <button class="btn-modern btn btn-success btn-lg m-2 px-4" @click="$emit('switchView','Register')">
        Register
      </button>
    </div>
  </div>
</template>

<style scoped>
.home {
  position: relative;
  height: calc(100vh - 56px);
  width: 100%;
  background: url("@/assets/car-bg.jpg") no-repeat center center/cover;
  color: white;
  text-shadow: 1px 1px 5px rgba(0, 0, 0, 0.9);
  padding-top: 40px;
}

.overlay {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(20,20,20,0.6);
  z-index: 1;
}

.logo, .title, .subtitle, h5, p, button {
  position: relative;
  z-index: 2;
}

.logo {
  max-width: 260px;
  filter: drop-shadow(0 0 12px rgba(255, 255, 255, 0.9));
  transition: transform 0.3s ease;
}
.logo:hover {
  transform: scale(1.05);
}

.btn-modern {
  transition: all 0.3s ease;
  border-radius: 30px;
}
.btn-modern:hover {
  transform: translateY(-3px);
  box-shadow: 0px 4px 12px rgba(0,0,0,0.4);
}
</style>
