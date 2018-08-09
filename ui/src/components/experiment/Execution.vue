<template>
  <div class="container" v-if="experiment">
    <breadcrumb v-bind:experiment="experiment" pagename="Execution"/>
    <div class="columns">
      <div class="column col-12 col-mx-auto">
        <div class="panel">
            <single-run />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang='ts'>
  import Vue from 'vue'
  import axios from 'axios'
  import swal from 'sweetalert2'
  import Breadcrumb from './Breadcrumb.vue'
  import MetaInfo from './Experiment/MetaInfo.vue'
  import SingleRun from './Execution/SingleRun.vue'

  export default Vue.extend({
    components: {
      Breadcrumb,
      MetaInfo,
      SingleRun
    },
    data: function () {
      return {
        experiment: null
      }
    },
    created: function () {
      this.$nextTick(function () {
        this.getExperiment()
      })
    },
    methods: {
      getExperiment: function () {
        const self = this
        const org_name = this.$route.params.org
        const workspace_name = this.$route.params.workspace
        const experiment_id = this.$route.params.experiment
        return axios.get(
            '/'+org_name+'/'+workspace_name+'/experiment/'+experiment_id, {
            headers: {
              'Accept': 'application/json'
            }
          }
        ).then(response => {
          self.experiment = response.data as any
        }).catch(error => {
          swal({    
            title: `Failed to retrieve your experiment!`,
            text: error.message,
            buttonsStyling: false,
            confirmButtonClass: 'btn btn-primary'
          })
        })
      }
    }
  })
</script>
