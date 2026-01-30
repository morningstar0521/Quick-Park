<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark py-2 shadow-sm">
    <div class="container-fluid">
      <a class="navbar-brand fs-4 fw-bold" href="#" @click.prevent="$emit('switchView','Home')">
        Quick Park
      </a>
      <div class="d-flex">
        <button class="btn btn-outline-light me-2 px-3 py-1" @click="$emit('switchView','Register')">
          Register
        </button>
        <button class="btn btn-outline-light px-3 py-1" @click="$emit('switchView','Login')">
          Login
        </button>
      </div>
    </div>
  </nav>
</template>
