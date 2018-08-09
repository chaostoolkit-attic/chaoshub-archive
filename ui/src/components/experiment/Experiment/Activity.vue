<template>
  <div :id="activity.name" v-if="activity" class="timeline-item activity-header">
    <div class="timeline-left">
      <a class="timeline-icon" :href="'#'+activity.name" />
    </div>
    <div class="timeline-content">
      <div class="tile">
        <div class="tile-content">
          <div class="columns">
            <div class="column col-10 c-hand" @click="expand=!expand">
              <span class="tile-subtitle">{{activity.name}}</span>
            </div>
            <div class="column col-1">
              <span class="label" v-if="activity.background">background</span>
            </div>
            <div class="column col-1">
              <span class="label label-warning" v-if="activity.type==='action'">action</span>
              <span class="label label-success" v-else-if="activity.type==='probe'">probe</span>
            </div>
          </div>
          <div class="columns">
            <div class="column col-12" v-show="expand">
              <python v-if="activity.provider && activity.provider.type=='python'" v-bind:provider="activity.provider" />
              <h-t-t-p v-else-if="activity.provider && activity.provider.type=='http'" v-bind:provider="activity.provider" />
              <process v-else-if="activity.provider && activity.provider.type=='process'" v-bind:provider="activity.provider" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
  import Python from './Providers/Python.vue'
  import HTTP from './Providers/HTTP.vue'
  import Process from './Providers/Process.vue'

export default Vue.extend({
    components: {
      Python,
      HTTP,
      Process
    },
    props: {
      activity: {
          type: Object,
          default: null
      }
    },
    data: function() {
        return {
            expand: false
        }
    }
})
</script>
