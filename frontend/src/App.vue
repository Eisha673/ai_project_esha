<script setup>
const links = [
  ['/', 'dashboard', 'Dashboard'],
  ['/jobs', 'work', 'Jobs'],
  ['/pipeline', 'hub', 'Pipeline'],
  ['/candidates', 'group', 'Candidates'],
  ['/offers', 'description', 'Offers'],
]
</script>

<template>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark"><span class="material-symbols-outlined">neurology</span></div>
        <div>
          <strong style="color:#3525cd;font-size:20px">RecruitAI</strong>
          <div class="muted" style="font-size:11px;font-weight:800;text-transform:uppercase">Enterprise Pipeline</div>
        </div>
      </div>
      <nav>
        <RouterLink v-for="[to, icon, label] in links" :key="to" class="nav-link" :to="to">
          <span class="material-symbols-outlined">{{ icon }}</span>
          <span>{{ label }}</span>
        </RouterLink>
      </nav>
    </aside>
    <main class="main">
      <header class="topbar">
        <input class="input" style="max-width:520px" placeholder="Search pipeline, candidates, or agents..." />
        <div style="display:flex;align-items:center;gap:8px;font-size:12px;font-weight:800;color:#64748b">
          <span style="width:8px;height:8px;border-radius:999px;background:#10b981"></span>
          NIM LIVE ENGINE
        </div>
      </header>
      <RouterView />
    </main>
  </div>
</template>
