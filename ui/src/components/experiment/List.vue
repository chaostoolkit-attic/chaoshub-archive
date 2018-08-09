<template>
  <div class="container">
    <div class="columns">
      <div class="column col-12 col-mx-auto">
        <div class="timeline">
          <div :id="x.id" class="timeline-item" v-for="x in experiments" :key="x.id">
            <div class="timeline-left">
              <a class="timeline-icon icon-lg" :href="'#'+x.id" />
            </div>
            <div class="timeline-content">
              <div class="tile">
                <div class="tile-content">
                  <div class="columns">
                    <div class="column col-12">
                      <span class="tile-title h6">{{x.title}}</span>
                    </div>
                    <div class="column col-12">
                      <span class="label">{{x.workspace.name}}</span>
                    </div>
                    <div class="column col-12">
                      <p>{{x.description}}</p>
                    </div>
                  </div>
                </div>
                <div class="tile-action">
                  <a class="btn" :href="'/experiment/'+x.id">View</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script lang='ts'>
  import Vue from "vue"
  import axios from 'axios'
  import swal from 'sweetalert2'

  export default Vue.extend({
    data: function () {
      return {
        experiments: []
      }
    },
    created: function () {
      this.$nextTick(function () {
        this.getExperiments()
      })
    },
    methods: {
      getExperiments: function () {
        const self = this
        axios.get(
          '/experiment/', {
            headers: {
              'Accept': 'application/json'
            }
          }
        ).then(function (response) {
          self.experiments = response.data
        }).catch(function (error) {
          swal({
            title: `Failed to retrieve your experiments!`,
            text: error.message,
            buttonsStyling: false,
            confirmButtonClass: 'btn btn-primary'
          })
        })
      }
    }
  })
</script>