<template>
  <div class="timeline" v-if="hasActivities()">
    <div class="timeline-item" :key="activity.id" :id="activity.id" v-for="activity in details.activities">
      <div class="timeline-left">
        <template v-if="activity.type=='execution'">
          <a v-if="activity.info && activity.info==='failed'" class="timeline-icon icon-lg timeline-status-fail" :href="'#'+activity.id"
          />
          <a v-else-if="activity.info && activity.info==='completed'" class="timeline-icon icon-lg timeline-status-success" :href="'#'+activity.id"
          />
          <a v-else class="timeline-icon icon-lg timeline-status-other" :href="'#'+activity.id" />
        </template>
        <template v-else>
          <a class="timeline-icon icon-lg" :href="'#'+activity.id" />
        </template>
      </div>
      <div class="timeline-content">
        <div class="tile">
          <div class="tile-content">
            <div class="tile-subtitle">
              <a v-if="activity.org && activity.workspace" :href="activityUrl(activity)">{{activity.title}}</a>
              <a v-else-if="activity.org" :href="activityUrl(activity)">{{activity.title}}</a>
              <span v-else>{{activity.title}}</span>
            </div>
            <div>
              <small class="text-gray">
                <span class="text-capitalize">
                  {{activity.type}}
                </span>
                <span>
                  {{activity.info}}
                </span>
                - {{formatActivityDate(activity)}}
                <span v-if="activity.workspace"> in
                <a :href="'/'+activity.org.name+'/'+activity.workspace.name">{{activity.workspace.name}}</a>
                </span>
                <span v-else-if="activity.org"> in
                <a :href="'/'+activity.org.name">{{activity.org.name}}</a>
                </span>
              </small>
            </div>
            <div>
              <small class="text-capitalize label mr-1" v-for="tag in activity.tags" :key="tag">
                {{tag}}
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang = "ts">
  import Vue from 'vue'
import axios from 'axios'
import swal from 'sweetalert2'
import * as moment from 'moment'

export default Vue.extend({
  props: {
    details: {
        type: Object,
        default: null
    }
  },
  methods: {
    hasActivities: function () {
      return this.details &&
        this.details.activities &&
        this.details.activities.length > 0
    },
    formatActivityDate: function (activity: any): string {
      if (!activity.timestamp) {
        return '-'
      }
      return moment(activity.timestamp).calendar()
    },
    activityUrl: function (activity: any): string {
      const org_name = activity.org.name

      let url = '/' + org_name
      if (activity.workspace) {
        const workspace_name = activity.workspace.name
        url = url + '/' + workspace_name + '/experiment/'

        if (activity.type === 'execution') {
            url += activity.experiment_id + '/execution/' + activity.timestamp
        } else {
            url += activity.experiment_id
        }
      }
      return url
    }
  }
})
</script>
