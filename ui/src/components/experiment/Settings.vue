<template>
  <div class="container">
    <breadcrumb pagename="Settings" />
    <div class="columns">
      <div class="column col-3">
        <ul class="menu">
          <li class="menu-item"><router-link :to="{name: 'settings_general'}" active-class="active">General</router-link></li>
          <li class="menu-item"><router-link :to="{name: 'settings_collaborators'}" active-class="active">Collaborators</router-link></li>
        </ul>
      </div>
      <router-view name="settings_view" />
    </div>
  </div>
</template>

<script lang='ts'>
  import Vue from 'vue'
  import Collaborators from './Settings/Collaborators.vue'
  import General from './Settings/General.vue'
  import Breadcrumb from './Breadcrumb.vue'

  export default Vue.extend({
    components: {
      'breadcrumb': Breadcrumb,
      'collaborators': Collaborators,
      'general': General
    }
  })
</script>
