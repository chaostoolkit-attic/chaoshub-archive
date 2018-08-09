<template>
  <div class="columns" v-if="context">
    <div class="column col-12">
      <h5>General Settings</h5>
    </div>
    <div class="column col-12">
      <div class="divider" />
    </div>
    <div class="column col-12">
      <div class="p-2" />
    </div>
    <template v-if="isOwner()"> 
      <div class="column col-12">
        <div class="p-2" />
      </div>
      <div class="column col-12">
        <h6 class="text-error">Danger Zone</h6>
        <div class="divider col-11" />
        <form id="nameForm">
          <div class="columns">
            <div class="column col-9">
              <p>
                You may rename your workspace but this has strong impacts since all existing links to it will be broken. So, be conservative
                and considerate for your community.
              </p>
              <div class="form-group">
                <label class="form-label" for="name">Name</label>
                <input v-bind:class="nameClass" type="text" id="name" placeholder="Name" v-model.trim="context.workspace.name" />
                <p class="form-input-hint" v-if="hasError('name')">{{getErrorMessage('name')}}</p>
              </div>
              <div class="form-group">
                <div class="p-2"></div>
                <button class="btn btn-error" @click.prevent="renameWorkspace">Rename Workspace</button>
              </div>
            </div>
          </div>
        </form>
        <div class="p-2" />
        <div class="p-2" />
        <div class="p-2" />
        <form>
          <div class="columns">
            <div class="column col-9" v-if="canDeleteWorkspace()">
              <p>
                You may delete your workspace and all its data will be then made unavailable to anyone. Be considerate and warn your community
                before doing so.
              </p>
              <p>
                This process cannot be reversed.
              </p>
              <div class="form-group">
                <div class="p-2"></div>
                <button class="btn btn-error" @click.prevent="deleteWorkspace">Delete Workspace</button>
              </div>
            </div>
            <div class="column col-9" v-else>
              <p>
                Personal workspaces cannot be deleted and live as long as their organization lives.
              </p>
            </div>
          </div>
        </form>
      </div>
    </template>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import axios from 'axios'
import swal from 'sweetalert2'
import * as moment from 'moment'

export default Vue.extend({
    data: function() {
      return {
          context: null,
          workspace_error: null
      }
  },
    created: function () {
      this.$nextTick(function () {
          this.loadWorkspace()
      })
    },
    computed: {
        nameClass: function() {
          return {
            'form-input': true,
            'is-error': this.hasError('name')
          }
        }
    },
    methods: {
        renderDate (d: any) {
            if (d == null) {
                return '-'
            }
            const date = moment(d).calendar()
            return date.charAt(0).toLowerCase() + date.slice(1)
        },
        hasError: function(field: string): boolean {
          if (!this.workspace_error) {
              return false
          }

          for(const err of this.workspace_error.errors) {
            if(err.field == field) {
                return true
            }
          }

          return false
        },
        getErrorMessage: function(field: string): string {
          if (!this.workspace_error) {
              return null
          }

          for(const err of this.workspace_error.errors) {
            if(err.field == field) {
                return err.message
            }
          }

          return ""
        },
        renameWorkspace: function() {
          const self = this
          const org_name = this.$route.params.org
          const workspace_name = this.$route.params.workspace

          this.workspace_error = null
          if ( (this.context.workspace.name == '') || (this.context.workspace.name === null)) {
            this.workspace_error = {
                errors: [
                    {"field": "name", "message": "Please provide a name"}
                ]
            }
            return
          }

          this.workspace_error = null
          const payload = {
              name: self.context.workspace.name
          }
          axios.patch('/'+org_name+'/'+workspace_name+'/settings/general/name', payload,
            {
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            }
            ).then(function (response) {
                self.$router.push({
                    name: 'workspace_settings_general',
                    params: {
                        org: self.context.org.name,
                        workspace: self.context.workspace.name
                    }
                })
            }).catch(function (error) {
               self.workspace_error = error.response.data
            })
        },
        loadWorkspace: function () {
            const self = this
            const org_name = this.$route.params.org
            const workspace_name = this.$route.params.workspace
            axios.get(
                '/'+org_name+'/'+workspace_name+'/settings/general',
                { headers: { 'Accept': 'application/json' } }
            ).then(function (response) {
                self.context = response.data
            }).catch(function (error) {
                swal({
                    title: `Failed to retrieve your workspace!`,
                    text: error.message,
                    buttonsStyling: false,
                    confirmButtonClass: 'btn btn-primary'
                })
            })
        },
        deleteWorkspace: function () {
            const self = this
            const org_name = this.$route.params.org
            const workspace_name = this.$route.params.workspace
            swal({
                title: "Are you sure you want to delete this workspace?",
                text: "Please enter the name of the workspace to acknowledge its deletion",
                input: 'text',
                buttonsStyling: false,
                confirmButtonClass: 'btn btn-error'
            })
            .then(result => {
                if (result.value) {
                    return axios.delete(
                        '/'+org_name+'/'+workspace_name,
                        { headers: { 'Accept': 'application/json' } }
                    ).then(function (response) {
                        self.$router.push({
                            name: 'user_home'
                        })
                    }).catch(function (error) {
                        swal({
                            title: `Failed to delete your workspace!`,
                            text: error.message,
                            buttonsStyling: false,
                            confirmButtonClass: 'btn btn-primary'
                        })
                    })
                }

                return null
            })
        },
        canDeleteWorkspace: function () {
          return (this.isOwner() && !this.isWorkspacePersonal())
        },
        isWorkspacePersonal: function () {
            return this.context.workspace.type === "personal"
        },
        isOwner: function () {
          return this.context.requested_by.workspace_owner
        }
    }
})
</script>

