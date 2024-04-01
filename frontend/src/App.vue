<script setup lang="ts">
import ExhibitionsDisplay from './components/ExhibitionsDisplay.vue';
import { onMounted, ref } from 'vue';

const time = ref("")
onMounted(() => {
  fetch("timestamp.txt")
    .then((response) => response.text())
    .then((data) => {
      time.value = new Date(Number(data) * 1000).toLocaleString();
    })
    .catch(() => {
      time.value = "加载失败";
    });
})
</script>

<template>
  <header>
    <h1>漫展演出</h1>
    <span>{{ time }}
      <a style="padding-left: 1em"
        href="https://github.com/liuly0322/BilibiliAnimationExhibitionInformationCollection/actions/workflows/auto_update.yml">GitHub
        Actions</a>
    </span>
  </header>

  <main>
    <ExhibitionsDisplay />
  </main>
</template>

<style>
h1 {
  font-size: 1.2em;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background-color: #f0f0f0;
}

footer {
  padding: 20px;
  text-align: center;
  background-color: #f0f0f0;
}
</style>