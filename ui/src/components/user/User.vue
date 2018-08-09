<template>
  <div class="container">
    <div class="columns">
      <div class="column col-4">
        <div class="columns">
          <div class="column col-12">
            <div class="card">
              <div class="card-header">
                <div class="card-title h5">
                  Experiments
                  <a href="/experiment/new" class="float-right btn btn-primary btn-action">
                    <i class="icon icon-plus" />
                  </a>
                </div>
              </div>
              <div class="card-body">
                <div class="tile tile-centered">
                  <div class="tile-content">
                    <div class="form-autocomplete">
                      <input class="form-input" type="text" placeholder="Find an experiment...">
                    </div>
                  </div>
                </div>
                <div class="tile tile-centered">
                  <div class="tile-content">
                    <ul class="menu" v-if="details && details.experiments">
                      <li class="menu-item" v-for="experiment in details.experiments" :key="experiment.id">
                        <a :href="'/'+experiment.workspace.org.name+'/'+experiment.workspace.name+'/experiment/'+experiment.id">{{experiment.title}}</a>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="column col-12"><p/></div>
          <div class="column col-12">
            <div class="card">
              <div class="card-header">
                <div class="card-title h5">
                    Organizations
                    <a href="/account/orgs" class="float-right btn btn-primary btn-action">
                        <i class="icon icon-plus" />
                    </a>
                </div>
              </div>
              <div class="card-body">
                <div class="tile tile-centered">
                  <div class="tile-content">
                    <div class="form-autocomplete">
                      <input class="form-input" type="text" placeholder="Find an organization...">
                    </div>
                  </div>
                </div>
                <div class="tile tile-centered">
                  <div class="tile-content">
                    <ul class="menu" v-if="details && details.orgs">
                      <li class="menu-item" v-for="org in details.orgs" :key="org.id">
                        <a :href="'/'+org.name">{{org.name}}</a>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="column col-12"><p/></div>
          <div class="column col-12">
            <div class="card">
              <div class="card-header">
                <div class="card-title h5">
                    Workspaces
                    <a href="/account/workspaces" class="float-right btn btn-primary btn-action">
                        <i class="icon icon-plus" />
                    </a>
                </div>
              </div>
              <div class="card-body">
                <div class="tile tile-centered">
                  <div class="tile-content">
                    <div class="form-autocomplete">
                      <input class="form-input" type="text" placeholder="Find a workspace...">
                    </div>
                  </div>
                </div>
                <div class="tile tile-centered">
                  <div class="tile-content">
                    <ul class="menu" v-if="details && details.workspaces">
                      <li class="menu-item" v-for="workspace in details.workspaces" :key="workspace.id">
                        <a :href="'/'+workspace.org.name+'/'+workspace.name">{{workspace.org.name+'/'+workspace.name}}</a>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="column col-8">
        <div class="card" v-if="hasActivities()">
          <div class="card-header">
            <div class="card-title h5">Your Activity</div>
          </div>
          <div class="card-body">
            <activities v-if="details" v-bind:details="details" />
          </div>
        </div>
        <div v-else>
            <div class="empty">
                <div class="empty-icon">
                    <i class="icon icon-3x icon-message"></i>
                </div>
                <p class="empty-title h5" v-if="details">
                    Hello {{getUserName()}}, you have no recorded activities yet!
                </p>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script lang='ts'>
import Vue from 'vue'
import axios from 'axios'
import swal from 'sweetalert2'
import * as moment from 'moment'
import Activities from '../Activities.vue'

export default Vue.extend({
  data: function () {
    return {
      details: null
    }
  },
  components: {
    Activities
  },
  created: function () {
    this.$nextTick(function () {
      this.getUserDashboard()
    })
  },
  methods: {
        hasActivities: function () {
            return this.details && this.details.activities &&
                this.details.activities.length > 0
        },
    getUserName: function () {
      if (this.details && this.details.requested_by.profile.username) {
        return this.details.requested_by.profile.username
      }
      return this.details.requested_by.profile.name
    },
    getUserDashboard: function () {
      const self = this
      axios.get(
        '/dashboard', {
          headers: {
            'Accept': 'application/json'
          }
        }
      ).then(function (response) {
        self.details = response.data
      }).catch(function (error) {
        swal({
          title: `Failed to retrieve your dashboard details!`,
          text: error.message,
          buttonsStyling: false,
          confirmButtonClass: 'btn btn-primary'
        })
      })
    }
  }
})
</script>