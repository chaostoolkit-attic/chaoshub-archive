<template>
  <div class="container">
    <breadcrumb v-if="experiment" v-bind:experiment="experiment" pagename="Executions" />
    <div class="columns">
      <div class="column col-12 col-mx-auto">
        <div class="panel">
          <all-runs v-if="executions" v-bind:executions="executions" />
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
  import AllRuns from './Execution/AllRuns.vue'
  import NoRuns from './Execution/NoRuns.vue'
  import MetaInfo from './Experiment/MetaInfo.vue'

  export default Vue.extend({
    components: {
      Breadcrumb,
      MetaInfo,
      AllRuns
    },
    data: function () {
        return {
            executions: null,
            experiment: null
        }
    },
    created: function () {
      this.$nextTick(function () {
        this.getExperiment()
        this.getExecutions()
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
      },
      getExecutions: function () {
        const self = this
        const org_name = this.$route.params.org
        const workspace_name = this.$route.params.workspace
        const experiment_id = this.$route.params.experiment
        return axios.get(
            '/'+org_name+'/'+workspace_name+'/experiment/'+experiment_id+'/execution', {
            headers: {
              'Accept': 'application/json'
            }
          }
        ).then(response => {
          self.executions = response.data as any
        }).catch(error => {
          swal({    
            title: `Failed to retrieve your executions!`,
            text: error.message,
            buttonsStyling: false,
            confirmButtonClass: 'btn btn-primary'
          })
        })
      }
    }
  })
</script>
