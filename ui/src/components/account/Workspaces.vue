<template>
  <div class="columns" v-if="workspaces">
    <div class="column col-12">
      <h5>Workspaces</h5>
    </div>
    <div class="column col-12">
      <div class="divider" />
    </div>
    <div class="column col-12 text-justify">
      <p>
        Workspaces allow you to share your experiments as well as collaborating on them with members of that workspace.
      </p>
      <p>
        You have a personal workspace by default. All experiments, and their executions, belonging to that personal workspace are
        private to you only.
      </p>
      <p>
        When you want to share with other users, you need to copy, or move, an experiment into a non-personal workspace. Experiments
        are then publicly viewable by everyone, even non members. You can make their executions private and viewable only
        by members of the workspace. Or, you can make executions publicly viewable as well.
      </p>
    </div>
    <div class="column col-12">
      <div class="p-2" />
      <div class="p-2" />
      <div class="p-2" />
    </div>
    <div class="column col-12">
      <div class="columns">
        <div class="column col-11">
          <h6>Your Workspaces</h6>
          <div class="divider" />
        </div>
        <div class="column col-9">
        <table class="table table-hover">
          <tbody>
            <tr v-for="w in workspaces.workspaces" :key="w.id">
              <td>
                    <strong><a :href="'/'+w.org.name+'/'+w.name">{{w.org.name}}/{{w.name}}</a></strong>
              </td>
              <td>
                    <span>{{w.type}}</span>
              </td>
              <td>
                    <span v-if="w.owner">Owner</span>
                    <span v-else>Member</span>
              </td>
                <td>
                    <a :href="'/'+w.org.name+'/'+w.name+'/settings'" v-if="w.owner">
                        <i class="icon icon-edit"></i>
                    </a>
                </td>
            </tr>
          </tbody>
        </table>
          <ul class="pagination">
            <li class="page-item page-prev">
              <div class="page-item-subtitle" v-if="workspaces.paging.prev"><a href="#" @click.prevent="loadWorkspaces(workspaces.paging.prev)">Previous</a></div>
              <div class="page-item-subtitle disabled" v-else>Previous</div>
            </li>
            <li class="page-item page-next">
              <div class="page-item-subtitle" v-if="workspaces.paging.next"><a href="#" @click.prevent="loadWorkspaces(workspaces.paging.next)">Next</a></div>
              <div class="page-item-subtitle disabled" v-else>Next</div>
            </li>
          </ul>
        </div>
      </div>
    </div>
    <div class="column col-12">
      <div class="p-2" />
      <div class="p-2" />
      <div class="p-2" />
    </div>
    <div class="column col-12">
      <h6>New Workspace</h6>
      <div class="divider col-11" />
      <form>
        <div class="columns">
          <div class="column col-9">
            <div class="form-group">
              <label class="form-label" for="name">Name</label>
              <input v-bind:class="nameClass" type="text" id="name" placeholder="Name" v-model.trim="new_workspace.name" />
              <p class="form-input-hint" v-if="hasError('name')">{{getErrorMessage('name')}}</p>
            </div>
            <div class="form-group">
              <label class="form-label" for="org">Organization</label>
              <select v-bind:class="orgClass" v-model="new_workspace.org">
                <option v-for="org in workspaces.orgs" :key="org.id" v-bind:value="org.id">{{org.name}}</option>
              </select>
              <p class="form-input-hint" v-if="hasError('org')">{{getErrorMessage('org')}}</p>
            </div>
            <div class="form-group">
              <label class="form-label">Experiment's visibility</label>
                <label class="form-radio">
                    <input type="radio" name="experiment_visibility" v-model="new_workspace.visibility.experiment" value="private"><i class="form-icon"></i> Private <small class="d-block text-gray">Only collaborators and organization members will access it</small>
                </label>
                <label class="form-radio">
                    <input type="radio" name="experiment_visibility" checked="" v-model="new_workspace.visibility.experiment" value="public"><i class="form-icon"></i> Public <small class="d-block text-gray">Everyone will be able to view the experiment</small>
                </label>
            </div>
            <div class="form-group">
              <label class="form-label">Run results visibility to non-collaborators</label>
              <div class="columns">
                  <div class="column col-12">
                        <label class="form-radio">
                        <input type="radio" name="execution_visibility" v-model="new_workspace.visibility.execution" value="none"><i class="form-icon"></i>
                        None <small class="d-block text-gray">Runs will remain visible only to collaborators and owners</small>
                    </label>
                  </div>
                  <div class="column col-12">
                    <label class="form-radio">
                        <input type="radio" name="execution_visibility" checked="" v-model="new_workspace.visibility.execution" value="status"><i class="form-icon"></i>
                        Status <small class="d-block text-gray">Only the run's status will be visible</small>
                    </label>
                  </div>
                  <div class="column col-12">
                    <label class="form-radio">
                        <input type="radio" name="execution_visibility" v-model="new_workspace.visibility.execution" value="full"><i class="form-icon"></i>
                        Full <small class="d-block text-gray">The full run's log will be shown</small>
                    </label>
                </div>
              </div>
            <div class="form-group">
              <div class="toast toast-success" v-if="workspace_created">
                <button @click.prevent="workspace_created=false" class="btn btn-clear float-right"></button>
                Your new workspace has been created!
              </div>
              <div class="p-2"></div>
              <button class="btn btn-primary" @click.prevent="newWorkspace">Create workspace</button>
            </div>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import axios from 'axios'
import swal from 'sweetalert2'

export default Vue.extend({
    data: function() {
      return {
          workspaces: null,
          new_workspace_error: null,
          workspace_created: false,
          new_workspace: {
              name: null,
              visibility: {
                  experiment: "public",
                  execution: "status"
              },
              org: null
          }
      }
  },
    created: function () {
      this.$nextTick(function () {
          this.loadWorkspaces()
      })
    },
    computed: {
        nameClass: function() {
          return {
            'form-input': true,
            'is-error': this.hasError('name')
          }
        },
        orgClass: function() {
          return {
            'form-select': true,
            'is-error': this.hasError('org')
          }
        }
    },
    methods: {
        hasError: function(field: string): boolean {
          if (!this.new_workspace_error) {
              return false
          }

          for(const err of this.new_workspace_error.errors) {
            if(err.field == field) {
                return true
            }
          }

          return false
        },
        getErrorMessage: function(field: string): string {
          if (!this.new_workspace_error) {
              return null
          }

          for(const err of this.new_workspace_error.errors) {
            if(err.field == field) {
                return err.message
            }
          }

          return ""
        },
        setExecutionVisibility (e: any) {
            if (e.target.checked) {
                this.new_workspace.visibility.execution = "private"
            } else {
                this.new_workspace.visibility.execution = "public"
            }
        },
        newWorkspace () {
          const self = this
          if ( (this.new_workspace.name == '') || (this.new_workspace.name === null)) {
            this.new_workspace_error = {
                errors: [
                    {"field": "name", "message": "Please provide a name"}
                ]
            }
            return
          }

          this.new_workspace_error = null
          axios.post('/account/workspaces', self.new_workspace,
            {
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            }
            ).then(function (response) {
                const workspace: any = response.data as any
                self.workspaces.workspaces.push(workspace)
                self.workspace_created = true
            }).catch(function (error) {
               self.new_workspace_error = error.response.data
          })
        },
        loadWorkspaces: function (page: number = 0) {
            const self = this
            let url = '/account/workspaces'
            if ((page !== null) && (page > 0)) {
                url += '?page='+page
            }
            axios.get(
                url,
                { headers: { 'Accept': 'application/json' } }
            ).then(function (response) {
                self.workspaces = response.data
            }).catch(function (error) {
                swal({
                    title: `Failed to retrieve your workspaces!`,
                    text: error.message,
                    buttonsStyling: false,
                    confirmButtonClass: 'btn btn-primary'
                })
            })
        }
    }
})
</script>
