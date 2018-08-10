<template>

  <body>
    <header v-if="showNavBar()" class="navbar navbar-primary">
      <div class="container">
        <div class="columns">
          <div class="column col-8 col-mx-auto">
            <div class="container">
              <div class="float-left navbar-section">
                <div class="logo">
                  <a href="/" class="logo-link">Chaos Hub</a>
                </div>
              </div>
              <div v-if="signed" class="navbar-section float-right">
                <div class="dropdown">
                  <div class="btn-group">
                    <button class="btn btn-secondary btn-action dropdown-toggle">
                      <i class="icon icon-menu" />
                    </button>

                    <ul class="menu">
                      <li class="menu-item">
                        <div class="tile tile-centered">
                          <div v-if="account" class="tile-content">{{account.profile.name}}</div>
                        </div>
                      </li>
                      <li class="divider" />
                      <li class="menu-item">
                        <a href="/account">
                          <i class="icon icon-edit" /> Account Settings
                        </a>
                      </li>
                      <li class="divider" />
                      <li class="menu-item">
                        <a href="/signout">
                          <i class="icon icon-shutdown" /> Sign Out
                        </a>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
              <div v-else class="navbar-section float-right">
                <a href="/signup" class="register-link">
                  <button class="btn btn-block register-btn">
                    Sign-Up for a Free Account
                  </button>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
    <main>
      <div class="container">
        <div class="columns">
          <div class="column col-8 col-mx-auto">
            <router-view>loading...</router-view>
          </div>
        </div>
      </div>
    </main>
    <footer>

      <div class="columns">
        <div class="column col-8 col-mx-auto">
            <div class="my-2"></div>
            <div class="d-block"><a href="https://chaoshub.org">ChaosHub</a> is an Open Source product under the
                <a href="https://github.com/chaostoolkit/chaoshub/blob/master/LICENSE.txt">AGPLv3+</a> license</div>
            <div class="d-block">&copy; 2018 - <a href="https://www.chaosiq.io">ChaosIQ</a></div>
        </div>
      </div>
      </footer>
  </body>
</template>

<style lang="scss">


</style>

<script lang="ts">
  import Vue from 'vue'
  import axios from 'axios'
  import swal from 'sweetalert2'

  export default Vue.extend({
    data: function () {
      return {
        account: null,
        signed: false,
        showMenu: false
      }
    },
    created: function () {
      const self = this
      this.$nextTick(function () {
        self.isSigned()
      })
    },
    methods: {
      isSigned: function () {
        const self = this
        axios.get(
          '/signed', {
            headers: {
              'Accept': 'application/json'
            }
          }
        ).then(function (response) {
          self.signed = response.data
          if (self.signed) {
            self.getUserProfile()
          }
        }).catch(function (error) {
          throw error
        })
      },
      showNavBar: function () {
          return !((this.$route.path=='/signin') || (this.$route.path=='/signup'))
      },
      getUserProfile: function () {
        const self = this
        axios.get(
          '/account/profile', {
            headers: {
              'Accept': 'application/json'
            }
          }
        ).then(function (response) {
          self.account = response.data
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
  });

</script>
