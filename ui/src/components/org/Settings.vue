<template>
  <div class="container">
    <breadcrumb pagename="Settings" />
    <div class="columns">
      <div class="column col-3">
        <ul class="menu">
          <li class="menu-item"><router-link :to="{name: 'org_settings_general'}" active-class="active">General</router-link></li>
          <li class="menu-item"><router-link :to="{name: 'org_settings_members'}" active-class="active">Members</router-link></li>
        </ul>
      </div>
      <div class="column col-8">
        <div class="card">
          <div class="card-body">
            <router-view name="org_settings_view" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import General from './Settings/General.vue'
import Members from './Settings/Members.vue'

import Vue from 'vue'
export default Vue.extend({
    components: {
        General,
        Members
    }
})
</script>
