<template>
  <div class="columns">
    <div class="column col-12">
      <h5>Public Profile</h5>
    </div>
    <div class="column col-12">
      <div class="divider" />
    </div>
    <div class="column col-12">
      <div class="p-2" />
    </div>
    <div class="column col-12">
      <form>
        <div class="columns">
          <div class="column col-9">
            <div class="form-group">
              <label class="form-label" for="name">Username</label>
              <input class="form-input" type="text" id="username" placeholder="Username" v-model.lazy="profile.username">
            </div>
            <div class="form-group">
              <label class="form-label" for="name">Name</label>
              <input class="form-input" type="text" id="name" placeholder="Name" v-model.lazy="profile.name">
            </div>
            <div class="form-group">
              <label class="form-label" for="email">Email</label>
              <input class="form-input" type="email" id="email" placeholder="Email" v-model.lazy="profile.email">
            </div>
            <div class="form-group">
              <label class="form-label" for="bio">Bio</label>
              <textarea class="form-input" id="text" rows="3" placeholder="Bio" v-model.lazy="profile.bio"/>
            </div>
            <div class="form-group">
              <label class="form-label" for="company">Company</label>
              <input class="form-input" type="text" id="company" placeholder="Company Name" v-model.lazy="profile.company"/>
            </div>
            <div class="form-group">
              <div class="p-2"></div>
              <button class="btn btn-primary" @click.prevent="updateProfile">Update your Profile</button>
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
            profile: {
                id: '',
                name: '',
                email: '',
                bio: '',
                company: '',
                username: ''
            }
        }
    },
    created: function () {
      this.$nextTick(function () {
          this.getUserProfile()
      })
    },
    methods: {
        updateProfile () {
          const self = this
          axios.post('/account/profile', self.profile,
            {
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            }
            ).then(function (response) {
                swal({
                    title: `Profile Updated`,
                    buttonsStyling: false,
                    confirmButtonClass: 'btn btn-primary'
                })
            }).catch(function (error) {
                swal({
                    title: `Failed to update your profile`,
                    text: error.message,
                    buttonsStyling: false,
                    confirmButtonClass: 'btn btn-primary'
                })
          })
        },
        getUserProfile: function () {
            const self = this
            axios.get(
                '/account/profile',
                { headers: { 'Accept': 'application/json' } }
            ).then(function (response) {
                self.profile = response.data
            }).catch(function (error) {
                swal({
                    title: `Failed to retrieve your profile!`,
                    text: error.message,
                    buttonsStyling: false,
                    confirmButtonClass: 'btn btn-primary'
                })
            })
        }
    }
})
</script>
