<template>
  <div class="modal modal-lg active">
    <div class="modal-container">
      <div class="columns">
        <div class="column col-6">
          <div class="logo-big">
            <a href="/" class="logo-link">Chaos Hub</a>
          </div>
          <h5 class="text-gray">
            Collaborative Chaos Engineering For Everyone
          </h5>
        </div>
        <div class="column col-6">
          <div class="card">
            <div class="card-header">
              <div class="card-title h5">Sign Up</div>
            </div>
            <div class="card-body">
              <div class="columns col-8 col-mx-auto">
                <div class="column col-12">
                  <form action="#">
                      <div class="columns">
                        <div class="column col-12">
                          <div class="form-group">
                            <label class="form-label" for="username">Username</label>
                            <input v-bind:class="{ 'form-input': true, 'is-error': error.field=='username' }" type="text" name="username" placeholder="Username" v-model.trim="local.username">
                            <p class="form-input-hint" v-if="error.field=='username'">{{error.message}}</p>
                            <p v-else />
                          </div>
                        </div>
                        <div class="column col-12">
                          <div class="form-group">
                            <label class="form-label" for="password">Password</label>
                            <input v-bind:class="{ 'form-input': true, 'is-error': error.field=='password' }" type="password" name="password" placeholder="Password" v-model.trim="local.password">
                            <p class="form-input-hint" v-if="error.field=='password'">{{error.message}}</p>
                            <p v-else />
                          </div>
                        </div>
                        <div class="column col-12">
                        <div class="toast toast-error" v-if="error.message && !error.field">{{error.message}}</div>
                        <div class="my-2"></div>
                          <button @click.prevent="signup" class="btn btn-primary btn-block">Create Account</button>
                        </div>
                      </div>
                  </form>
                </div>
                <div class="column col-12">
                  <div class="my-2"></div>
                  <div class="divider text-center" data-content="OR"></div>
                </div>
                <div class="column col-12">
                  <form action="/auth/signup/with/github">
                    <button class="btn btn-block github-btn">
                      <div class="columns">
                        <div class="column col-1">
                          <svg aria-labelledby="simpleicons-gitlab-icon" fill="white" height="24" role="img" preserveAspectRatio="none" viewBox="0 0 24 24"
                            xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"
                            />
                          </svg>
                        </div>
                        <div class="column col-11">
                          <span class="text-large">GitHub</span>
                        </div>
                      </div>
                    </button>
                  </form>
                </div>
                <div class="column col-12">
                  <div class="my-2"></div>
                </div>
                <div class="column col-12">
                  <form action="/auth/signup/with/gitlab">
                    <button class="btn btn-block gitlab-btn">
                      <div class="columns">
                        <div class="column col-1">
                          <svg aria-labelledby="simpleicons-gitlab-icon" fill="white" height="24" role="img" preserveAspectRatio="none" viewBox="0 0 24 24"
                            xmlns="http://www.w3.org/2000/svg">
                            <path d="M23.955 13.587l-1.342-4.135-2.664-8.189c-.135-.423-.73-.423-.867 0L16.418 9.45H7.582L4.919 1.263C4.783.84 4.185.84 4.05 1.26L1.386 9.449.044 13.587c-.121.375.014.789.331 1.023L12 23.054l11.625-8.443c.318-.235.453-.647.33-1.024"
                            />
                          </svg>
                        </div>
                        <div class="column col-11">
                          <span class="text-large">GitLab</span>
                        </div>
                      </div>
                    </button>
                  </form>
                </div>
                <div class="column col-12">
                  <div class="my-2"></div>
                </div>
                <div class="column col-12">
                  <form action="/auth/signup/with/google">
                    <button class="btn btn-block google-btn">
                      <div class="columns">
                        <div class="column col-1">
                          <svg aria-labelledby="simpleicons-google-icon" fill="white" height="24" role="img" preserveAspectRatio="none" viewBox="0 0 24 24"
                            xmlns="http://www.w3.org/2000/svg">
                            <path d="M12.24 10.285V14.4h6.806c-.275 1.765-2.056 5.174-6.806 5.174-4.095 0-7.439-3.389-7.439-7.574s3.345-7.574 7.439-7.574c2.33 0 3.891.989 4.785 1.849l3.254-3.138C18.189 1.186 15.479 0 12.24 0c-6.635 0-12 5.365-12 12s5.365 12 12 12c6.926 0 11.52-4.869 11.52-11.726 0-.788-.085-1.39-.189-1.989H12.24z"
                            />
                          </svg>
                        </div>
                        <div class="column col-11">
                          <span class="text-large">Google</span>
                        </div>
                      </div>
                    </button>
                  </form>
                </div>
                <div class="column col-12">
                  <div class="my-2"></div>
                </div>
                <div class="column col-12">
                  <form action="/auth/signup/with/bitbucket">
                    <button class="btn btn-block bitbucket-btn">
                      <div class="columns">
                        <div class="column col-1">
                          <svg aria-labelledby="simpleicons-bitbucket-icon" fill="white" height="24" role="img" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M.778 1.211c-.424-.006-.772.334-.778.758 0 .045.002.09.01.134l3.263 19.811c.084.499.515.867 1.022.872H19.95c.382.004.708-.271.77-.646l3.27-20.03c.068-.418-.216-.813-.635-.881-.045-.008-.089-.011-.133-.01L.778 1.211zM14.52 15.528H9.522L8.17 8.464h7.561l-1.211 7.064z"
                            />
                          </svg>
                        </div>
                        <div class="column col-11">
                          <span class="text-large">BitBucket</span>
                        </div>
                      </div>
                    </button>
                  </form>
                </div>
              </div>
            </div>
            <div class="card-footer">
              <div class="card-subtitle text-gray">If are already a member of ChaosHub, please
                <a href="/signin">sign-in</a> now!</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue'
  import axios from 'axios'
import swal from 'sweetalert2'

  export default Vue.extend({
      data: function () {
          return {
              local: {
                  username: null,
                  password: null
              },
              error: {
                  message: null,
                  field: null
              }
          }
      },
      methods: {
          signup: function() {
            const self = this
            if ( (this.local.username == '') || (this.local.username === null)) {
                this.error = {"field": "username", "message": "Please specify your username"}
                return
            }

            if ( (this.local.password == '') || (this.local.password === null)) {
                this.error = {"field": "password", "message": "Please specify your password"}
                return
            }

            axios.post(
                '/auth/signup/local', this.local,
                { headers: { 'Accept': 'application/json' } }
            ).then(function (response) {
              window.location.href = "/"
            }).catch(function (error) {
                self.error = error.response.data
            })

          }
      }
  })

</script>
