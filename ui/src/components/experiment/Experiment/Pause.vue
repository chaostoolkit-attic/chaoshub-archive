<template>
  <div v-if="pause" class="timeline-item activity-header">
    <div class="timeline-left">
      <span class="timeline-icon"></span>
    </div>
    <div class="timeline-content">
      <div class="tile">
        <div class="tile-content">
          <div class="columns">
            <div class="column col-11">
              <span v-if="type=='before'" class="tile-subtitle">Pause before next for <span class="var">{{pause}}</span> seconds</span>
              <span v-else-if="type=='after'" class="tile-subtitle">Pause after previous for <span class="var">{{pause}}</span> seconds</span>
            </div>
            <div class="column col-1">
              <span class="label label-primary">pause</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
export default Vue.extend({
    props: {
      pause: {
          type: Number,
          default: null
      },
      type: {
          type: String,
          default: null
      }
    }
})
</script>
