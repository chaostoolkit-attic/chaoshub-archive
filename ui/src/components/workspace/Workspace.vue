<template>
  <div class="container">
    <div class="columns" v-if="details">
      <div class="column col-4">
        <div class="columns">
          <div class="column col-12">
            <div class="card">
              <div class="card-header">
                <div class="card-title h5">
                  Experiments
                  <a v-if="isWorkspaceMember()" href="/experiment/new" class="float-right btn btn-primary btn-action">
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
                        <a :href="'/'+details.workspace.org.name+'/'+details.workspace.name+'/experiment/'+experiment.id">{{experiment.title}}</a>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="column col-12">
            <p/>
          </div>
          <div class="column col-12" v-if="details.workspace.type!='personal'">
            <div class="card">
              <div class="card-header">
                <div class="card-title h5">
                  Collaborators
                  <a v-if="isWorkspaceOwner()" :href="'/'+details.workspace.org.name+'/'+details.workspace.name+'/settings/collaborators'"
                    class="float-right btn btn-primary btn-action">
                    <i class="icon icon-plus" />
                  </a>
                </div>
              </div>
              <div class="card-body">
                <div class="tile tile-centered">
                  <div class="tile-content">
                    <div class="has-icon-right">
                      <input v-model.trim="searched_collaborator" class="form-input" type="text" @keyup.enter="findCollaborator" placeholder="Find a collaborator...">
                      <i class="form-icon icon icon-search c-hand" @click.prevent="findCollaborator"></i>
                    </div>
                  </div>
                </div>
                <div class="tile tile-centered">
                  <div class="tile-content">
                    <ul class="menu" v-if="collaborators">
                      <li class="menu-item" v-for="collaborator in collaborators" :key="collaborator.id">
                        <a :href="'/'+collaborator.org.name">
                          <template v-if="collaborator.profile.username">
                            {{collaborator.profile.username}}
                          </template>
                          <template v-else-if="collaborator.profile.name">
                            {{collaborator.profile.name}}
                          </template>
                        </a>
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
            <div class="card-title h5">Workspace Activity</div>
          </div>
          <div class="card-body">
            <activities v-bind:details="details" />
          </div>
        </div>
        <div v-else>
            <div class="empty">
                <div class="empty-icon">
                    <i class="icon icon-3x icon-message"></i>
                </div>
                <p class="empty-title h5">
                    This workspace has no activities yet!
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
    data: function() {
      return {
          details: null,
          searched_collaborator: null,
          collaborators: null
      }
  },
  components: {
    Activities
  },
    created: function () {
      this.$nextTick(function () {
          this.getWorkspaceDashboard()
      })
    },
      methods: {
        isSignedIn: function (): boolean {
            return this.details && this.details.requested_by
        },
        isWorkspaceMember: function (): boolean {
            return this.isSignedIn() && (
                this.details.requested_by.workspace_collaborator ||
                this.isWorkspaceOwner() ||
                this.isOrgOwner()
            )
        },
        isWorkspaceOwner: function (): boolean {
            return this.isSignedIn() && this.details.requested_by.workspace_owner
        },
        isOrgOwner: function (): boolean {
            return this.isSignedIn() && this.details.requested_by.org_owner
        },
        hasActivities: function () {
            return this.details.activities &&
                this.details.activities.length > 0
        },
        findCollaborator: function () {
            if(!this.searched_collaborator) {
                this.collaborators = this.details.collaborators
                return
            }

            const self = this
            const org_name = this.$route.params.org
            const workspace_name = this.$route.params.workspace
            axios.get(
                '/'+org_name+'/'+workspace_name+'/lookup/collaborator?q='+self.searched_collaborator,
                { headers: { 'Accept': 'application/json' } }
            ).then(function (response) {
                self.collaborators = response.data
            }).catch(function (error) {
                swal({
                    title: `Failed to lookup collaborators!`,
                    text: error.message,
                    buttonsStyling: false,
                    confirmButtonClass: 'btn btn-primary'
                })
            })
        },
        getWorkspaceDashboard: function () {
            const self = this
            const org_name = this.$route.params.org
            const workspace_name = this.$route.params.workspace
            axios.get(
                '/'+org_name+'/'+workspace_name+'/dashboard',
                { headers: { 'Accept': 'application/json' } }
            ).then(function (response) {
                self.details = response.data
                self.collaborators  = self.details.collaborators
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