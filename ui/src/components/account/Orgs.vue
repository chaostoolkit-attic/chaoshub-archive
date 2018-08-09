<template>
  <div class="columns" v-if="orgs">
    <div class="column col-12">
      <h4>Organizations</h4>
    </div>
    <div class="column col-12">
      <div class="divider" />
    </div>
    <div class="column col-12">
      <div class="p-2" />
      <div class="p-2" />
      <div class="p-2" />
    </div>
    <div class="column col-12">
      <div class="columns">
        <div class="column col-11">
          <h5>Your Organizations</h5>
          <div class="divider" />
        </div>
        <div class="column col-9">
          <table class="table table-hover">
            <tbody>
              <tr v-for="org in orgs.orgs" :key="org.id">
                <td>
                  <div class="columns">
                    <div class="column col-12">
                      <strong><a :href="'/'+org.name">{{org.name}}</a></strong>
                    </div>
                  </div>
                </td>
                <td>
                    <span>{{org.type}}</span>
                </td>
                <td>
                    <span v-if="org.owner">Owner</span>
                    <span v-else>Member</span>
                </td>
                <td>
                    <a :href="'/'+org.name+'/settings'" v-if="org.owner">
                        <i class="icon icon-edit"></i>
                    </a>
                </td>
              </tr>
            </tbody>
          </table>
          <ul class="pagination">
            <li class="page-item page-prev">
              <div class="page-item-subtitle" v-if="orgs.paging.prev"><a href="#" @click.prevent="loadOrgs(orgs.paging.prev)">Previous</a></div>
              <div class="page-item-subtitle disabled" v-else>Previous</div>
            </li>
            <li class="page-item page-next">
              <div class="page-item-subtitle" v-if="orgs.paging.next"><a href="#" @click.prevent="loadOrgs(orgs.paging.next)">Next</a></div>
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
      <h5>New Organization</h5>
      <div class="divider col-11" />
      <form>
        <div class="columns">
          <div class="column col-9">
            <h6>Required Information</h6>
            <div class="form-group">
              <label class="form-label" for="name">Name</label>
              <input v-bind:class="nameClass" type="text" id="name" placeholder="Name" required v-model.trim="new_org.name" />
              <p class="form-input-hint" v-if="hasError('name')">{{getErrorMessage('name')}}</p>
            </div>
            <div class=" p-2" />
            <h6>Additional Optional Information</h6>
            <div class="form-group">
              <label class="form-label" for="desc">Description</label>
              <input class="form-input" type="text" id="desc" placeholder="Short description" v-model.trim="new_org.settings.description" />
            </div>
            <div class="form-group">
              <label class="form-label" for="url">URL</label>
              <input class="form-input" type="text" id="url" placeholder="URL" v-model.trim="new_org.settings.url" />
            </div>
            <div class="form-group">
              <label class="form-label" for="email">Contact</label>
              <input class="form-input" type="email" id="email" placeholder="Contact email" v-model.trim="new_org.settings.email" />
            </div>
            <div class="form-group">
              <div class="toast toast-success" v-if="org_created">
                <button @click.prevent="org_created=false" class="btn btn-clear float-right"></button>
                Your new organization has been created!
              </div>
              <div class="p-2"></div>
              <button class="btn btn-primary" @click.prevent="newOrg">Create organization</button>
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
          orgs: null,
          new_org_error: null,
          org_created: false,
          new_org: {
              name: null,
              settings: {
                description: null,
                url: null,
                logo: null,
                email: null
              }
          }
      }
  },
    created: function () {
      this.$nextTick(function () {
          this.loadOrgs()
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
        hasError: function(field: string): boolean {
          if (!this.new_org_error) {
              return false
          }

          for(const err of this.new_org_error.errors) {
            if(err.field == field) {
                return true
            }
          }

          return false
        },
        getErrorMessage: function(field: string): string {
          if (!this.new_org_error) {
              return null
          }

          for(const err of this.new_org_error.errors) {
            if(err.field == field) {
                return err.message
            }
          }

          return ""
        },
        newOrg: function() {
          const self = this
          this.new_org_error = null
          if ( (this.new_org.name == '') || (this.new_org.name === null)) {
            this.new_org_error = {
                errors: [
                    {"field": "name", "message": "Please provide a name"}
                ]
            }
            return
          }

          this.new_org_error = null
          axios.post('/account/orgs', self.new_org,
            {
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            }
            ).then(function (response) {
                const org: any = response.data as any
                self.orgs.orgs.push(org)
                self.org_created = true
            }).catch(function (error) {
               self.new_org_error = error.response.data
            })
        },
        loadOrgs: function (page: number = 0) {
            const self = this
            let url = '/account/orgs'
            if ((page !== null) && (page > 0)) {
                url += '?page='+page
            }
            axios.get(
                url,
                { headers: { 'Accept': 'application/json' } }
            ).then(function (response) {
                self.orgs = response.data
            }).catch(function (error) {
                swal({
                    title: `Failed to retrieve your organizations!`,
                    text: error.message,
                    buttonsStyling: false,
                    confirmButtonClass: 'btn btn-primary'
                })
            })
        }
    }
})
</script>
