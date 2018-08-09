<template>
  <div class="columns" v-if="provider">
    <div class="column col-12">
      <div class="columns">
        <div class="column col-1">
          <small>
            <strong>Provider:</strong>
          </small>
        </div>
        <div class="column col-auto-mx">
          <small>HTTP</small>
        </div>
      </div>
    </div>
    <div class="column col-12">
      <div class="columns">
        <div class="column col-1">
          <small>
            <strong>URL:</strong>
          </small>
        </div>
        <div class="column col-auto-mx">
          <small>{{provider.url}}</small>
        </div>
      </div>
    </div>
    <div class="column col-12" v-if="provider.method">
      <div class="columns">
        <div class="column col-1">
          <small>
            <strong>Method:</strong>
          </small>
        </div>
        <div class="column col-auto-mx">
          <small>{{provider.method}}</small>
        </div>
      </div>
    </div>
    <div class="column col-12" v-if="provider.timeout">
      <div class="columns">
        <div class="column col-1">
          <small>
            <strong>Timeout:</strong>
          </small>
        </div>
        <div class="column col-auto-mx">
          <small><span class="var">{{provider.timeout}}</span>s</small>
        </div>
      </div>
    </div>
    <div class="column col-12" v-if="provider.verify_tls">
      <div class="columns">
        <div class="column col-1">
          <small>
            <strong>Verify TLS:</strong>
          </small>
        </div>
        <div class="column col-auto-mx">
          <small>{{provider.verify_tls}}</small>
        </div>
      </div>
    </div>
    <div class="column col-12" v-if="provider.secrets">
      <div class="columns">
        <div class="column col-1">
          <small>
            <strong>Secrets:</strong>
          </small>
        </div>
        <div class="column col-auto-mx">
          <small v-for="(secret, index) in provider.secrets" :key="index">{{secret}}</small>
        </div>
      </div>
    </div>
    <div class="column col-8" v-if="provider.headers">
      <div class="columns">
        <div class="column col-1">
          <small>
            <strong>Headers:</strong>
          </small>
        </div>
        <div class="column col-12">
          <table class="table table-hover">
              <tbody>
                  <tr v-for="(value, key, index) in provider.headers" :key="index">
                      <td><small>{{key}}</small></td>
                      <td><small>{{value}}</small></td>
                  </tr>
              </tbody>
          </table>
        </div>
      </div>
    </div>
    <div class="column col-8" v-if="provider.arguments">
      <div class="columns">
        <div class="column col-1">
          <small>
            <strong>Arguments:</strong>
          </small>
        </div>
        <div class="column col-12">
          <table class="table table-hover">
              <tbody>
                  <tr v-for="(value, key, index) in provider.arguments" :key="index">
                      <td><small>{{key}}</small></td>
                      <td><small>{{value}}</small></td>
                  </tr>
              </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
export default Vue.extend({
    props: {
      provider: {
          type: Object,
          default: null
      }
    }
})
</script>
