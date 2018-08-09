<template>
  <div class="container">
    <div class="columns" v-if="details">
      <div class="column col-12">
          <div class="columns">
              <div class="column col-12">
                <h2>{{details.org.name}}</h2>
              </div>
              <template v-if="details.org.settings.meta">
                <div class="column col-12">
                    <span class="text-gray" v-if="details.org.settings.meta.description">{{details.org.settings.meta.description}}</span>
                </div>
                <div class="column col-6">
                    <a class="text-gray" v-if="details.org.settings.meta.email" :href="'mailto:'+details.org.settings.meta.email"><small><i class="icon icon-mail" /> {{details.org.settings.meta.email}}</small></a>
                    <span class="px-2" />
                    <a class="text-gray" v-if="details.org.settings.meta.url" :href="details.org.settings.meta.url"><small><i class="icon icon-link" /> {{details.org.settings.meta.url}}</small></a>
                </div>
              </template>
          </div>
      </div>
      <div class="column col-12">
          <div class="py-2" />
      </div>
      <div class="column col-4">
        <div class="columns">
          <div class="column col-12">
            <div class="card">
              <div class="card-header">
                <div class="card-title h5">
                  Experiments
                  <a v-if="isMember()" href="/experiment/new" class="float-right btn btn-primary btn-action">
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
          <div class="column col-12"><p/></div>
          <div class="column col-12">
            <div class="card">
              <div class="card-header">
                <div class="card-title h5">
                  Workspaces
                  <a v-if="isOrgOwner()" :href="'/account/workspaces'" class="float-right btn btn-primary btn-action">
                    <i class="icon icon-plus" />
                  </a>
                </div>
              </div>
              <div class="card-body">
                <div class="tile tile-centered">
                  <div class="tile-content">
                    <div class="has-icon-right">
                      <input v-model.trim="searched_workspace" @keyup.enter="findWorkspace" class="form-input" type="text" placeholder="Find a workspace...">
                      <i class="form-icon icon icon-search c-hand" @click.prevent="findWorkspace"></i>
                    </div>
                  </div>
                </div>
                <div class="tile tile-centered">
                  <div class="tile-content">
                    <ul class="menu" v-if="workspaces">
                      <li class="menu-item" v-for="workspace in workspaces" :key="workspace.id">
                        <a :href="'/'+details.org.name+'/'+workspace.name">{{workspace.name}}</a>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="column col-12"><p/></div>
          <div class="column col-12" v-if="details.org.type!='personal'">
            <div class="card">
              <div class="card-header">
                <div class="card-title h5">
                  Members
                  <a v-if="isOrgOwner()" :href="'/'+details.org.name+'/settings/members'" class="float-right btn btn-primary btn-action">
                    <i class="icon icon-plus" />
                  </a>
                </div>
              </div>
              <div class="card-body">
                <div class="tile tile-centered">
                  <div class="tile-content">
                    <div class="has-icon-right">
                      <input v-model.trim="searched_member" @keyup.enter="findMember" class="form-input" type="text" placeholder="Find a member...">
                      <i class="form-icon icon icon-search c-hand" @click.prevent="findMember"></i>
                    </div>
                  </div>
                </div>
                <div class="tile tile-centered">
                  <div class="tile-content">
                    <ul class="menu" v-if="members">
                      <li class="menu-item" v-for="member in members" :key="member.id">
                        <a :href="'/'+member.org.name">
                            <template v-if="member.profile.username">
                                {{member.profile.username}}
                            </template>
                            <template v-else-if="member.profile.name">
                                {{member.profile.name}}
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
            <div class="card-title h5">Organization Activity</div>
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
                    This organization has no activities yet!
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
  components: {
    Activities
  },
    data: function() {
      return {
          details: null,
          searched_member: null,
          searched_workspace: null,
          members: null,
          workspaces: null
      }
  },
    created: function () {
      this.$nextTick(function () {
          this.getOrgDashboard()
      })
    },
      methods: {
        isSignedIn: function (): boolean {
            return this.details && this.details.requested_by
        },
        isMember: function (): boolean {
            return this.isSignedIn() && this.details.requested_by.org_member
        },
        isOrgOwner: function (): boolean {
            return this.isSignedIn() && this.details.requested_by.org_owner
        },
        hasActivities: function () {
            return this.details.activities &&
                this.details.activities.length > 0
        },
        findMember: function () {
            if(!this.searched_member) {
                this.members = this.details.members
                return
            }

            const self = this
            const org_name = this.$route.params.org
            axios.get(
                '/'+org_name+'/lookup/member?q='+self.searched_member,
                { headers: { 'Accept': 'application/json' } }
            ).then(function (response) {
                self.members = response.data
            }).catch(function (error) {
                swal({
                    title: `Failed to lookup members!`,
                    text: error.message,
                    buttonsStyling: false,
                    confirmButtonClass: 'btn btn-primary'
                })
            })
        },
        findWorkspace: function () {
            if(!this.searched_workspace) {
                this.workspaces = this.details.org.workspaces
                return
            }

            const self = this
            const org_name = this.$route.params.org
            axios.get(
                '/'+org_name+'/lookup/workspace?q='+self.searched_workspace,
                { headers: { 'Accept': 'application/json' } }
            ).then(function (response) {
                self.workspaces = response.data
            }).catch(function (error) {
                swal({
                    title: `Failed to lookup workspaces!`,
                    text: error.message,
                    buttonsStyling: false,
                    confirmButtonClass: 'btn btn-primary'
                })
            })
        },
        getOrgDashboard: function () {
            const self = this
            const org_name = this.$route.params.org
            axios.get(
                '/'+org_name+'/dashboard',
                { headers: { 'Accept': 'application/json' } }
            ).then(function (response) {
                self.details = response.data
                self.members = self.details.members
                self.workspaces = self.details.org.workspaces
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