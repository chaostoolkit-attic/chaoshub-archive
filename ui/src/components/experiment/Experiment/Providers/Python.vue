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
          <small>Python</small>
        </div>
      </div>
    </div>
    <div class="column col-12">
      <div class="columns">
        <div class="column col-1">
          <small>
            <strong>Module:</strong>
          </small>
        </div>
        <div class="column col-auto-mx">
          <small>{{provider.module}}</small>
        </div>
      </div>
    </div>
    <div class="column col-12">
      <div class="columns">
        <div class="column col-1">
          <small>
            <strong>Function:</strong>
          </small>
        </div>
        <div class="column col-auto-mx">
          <small>{{provider.func}}</small>
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
