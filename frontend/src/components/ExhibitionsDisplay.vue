<script setup lang="ts">
import { ref, watch, onMounted, computed } from "vue";
import { NSelect } from 'naive-ui'

const cityOptions = ["上海", "杭州", "苏州", "北京", "丽水", "广州", "合肥", "南宁", "江西"].map((city) => {
  return { label: city, value: city };
});
const typeOptions = ref([] as { label: string; value: number }[]);

const citySelect = ref(localStorage.getItem("selectedCity") || "上海");
const typeSelect = ref(0);
const jsonDisplay = ref({} as Record<string, Exhibition[]>);

watch(citySelect, (newValue) => {
  localStorage.setItem("selectedCity", newValue);
  updateJson();
});

interface Exhibition {
  名称: string;
  Cover: string;
  Link: string;
  开始时间: string;
  具体时间范围: string;
  地点: string;
  最低票价: string;
}

const updateJson = () => {
  jsonDisplay.value = {};
  const selectedCity = citySelect.value;
  const jsonFilePath = `${selectedCity}-漫展信息.json`;
  fetch(jsonFilePath)
    .then((response) => response.json())
    .then((data) => {
      jsonDisplay.value = data;
    })
    .catch((error) => {
      alert(`加载 ${jsonFilePath} 失败，错误信息：${error}`);
    });
};

const nonEmptyKindsExhibitions = computed(() => {
  const nonEmptyKindsExhibitions = [] as Record<string, Exhibition[]>[];
  for (const exhibitionKind in jsonDisplay.value) {
    const exhibitions = jsonDisplay.value[exhibitionKind];
    if (exhibitions.length > 0) {
      nonEmptyKindsExhibitions.push({ [exhibitionKind]: exhibitions });
    }
  }
  return nonEmptyKindsExhibitions;
});

const exhibitions = computed(() => {
  const current = nonEmptyKindsExhibitions.value[typeSelect.value];
  return current ? Object.values(current)[0] : [];
});

watch(nonEmptyKindsExhibitions, () => {
  typeOptions.value = nonEmptyKindsExhibitions.value.map((item, index) => {
    return { label: Object.keys(item)[0], value: index };
  });
  typeSelect.value = typeOptions.value.length - 1;
});

onMounted(updateJson);

const getCoverUrl = (url: string) => {
  return "https://api.liuly.moe/image/" + url + "@350w_466h.jpeg";
};

const redirect = (item: Exhibition) => {
  window.open(item.Link);
};
</script>

<template>
  <div>
    <div id="select-div">
      <n-select v-model:value="citySelect" :options="cityOptions" />
      <n-select v-model:value="typeSelect" :options="typeOptions" />
    </div>
    <div id="json-display">
      <div id="project-list">
        <div v-for="item in exhibitions" :key="item.Link" class="project-list-item" @click="redirect(item)">
          <img class="project-list-item-img" v-lazy="getCoverUrl(item.Cover)" />
          <div class="project-list-item-detail">
            <div class="project-list-item-title">{{ item.名称 }}</div>
            <div class="project-list-item-time">📅 {{ item.开始时间 }}</div>
            <div class="project-list-item-time-detail">
              🕒 {{ item.具体时间范围 }}
            </div>
            <div class="project-list-item-address">📍 {{ item.地点 }}</div>
            <div class="project-list-item-price">
              <span class="price-symbol">¥</span>
              <span class="price">{{ item.最低票价 }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>