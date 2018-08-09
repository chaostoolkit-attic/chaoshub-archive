<template>
  <div class="container">
    <breadcrumb pagename="Settings" />
    <div class="columns">
      <div class="column col-3">
        <ul class="menu">
          <li class="menu-item"><router-link :to="{name: 'workspace_settings_general'}" active-class="active">General</router-link></li>
          <li class="menu-item"><router-link :to="{name: 'workspace_settings_collaborators'}" active-class="active">Collaborators</router-link></li>
        </ul>
      </div>
      <div class="column col-8">
        <div class="card">
          <div class="card-body">
            <router-view name="workspace_settings_view" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import General from './Settings/General.vue'
import Collaborators from './Settings/Collaborators.vue'

import Vue from 'vue'
export default Vue.extend({
    components: {
        General,
        Collaborators
    }
})
</script>
