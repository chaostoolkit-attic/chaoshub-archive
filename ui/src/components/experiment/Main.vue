<template>
  <div class="container" v-if="experiment">
    <breadcrumb v-bind:experiment="experiment" />
    <div class="columns">
      <div class="column col-12 col-mx-auto">
        <div class="panel">
          <meta-info v-bind:experiment="experiment" />
          <div class="panel-body">
            <div class="column col-12 my-2">
              <div class="divider" />
            </div>
            <div class="column col-12">
              <div class="columns">
                <div class="column">
                  <h5>Configuration</h5>
                  <p class="text-gray">Configuration are public data injected into your experiment when it is executed.</p>

                  <div v-if="experiment.payload.configuration">
                    <table class="table table-hover">
                      <thead>
                        <tr>
                          <th>Key</th>
                          <th>Value</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(value, key) in experiment.payload.configuration" :key="key">
                          <td>
                            <small>
                              <samp>{{key}}</samp>
                            </small>
                          </td>
                          <td>
                            <small>
                              <samp>{{value}}</samp>
                            </small>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <div v-else>
                    <p>This experiment has no configuration.</p>
                  </div>
                </div>
                <div class="divider-vert"></div>
                <div class="column">
                  <h5>Secrets</h5>
                  <p class="text-gray">Secrets are sensitive data injected into your experiment when it is executed. Most of the time, data is
                    read from the runtime environment but you may also set secrets directly into the experiment declaration.</p>

                  <div v-if="experiment.payload.secrets">
                    <table class="table table-hover">
                      <thead>
                        <tr>
                          <th>Scope</th>
                          <th>Key</th>
                          <th>Value</th>
                          <th>Source</th>
                        </tr>
                      </thead>
                      <tbody>
                        <template v-for="(value, key) in experiment.payload.secrets">
                          <tr v-for="(secret_value, secret_key) in value" :key="secret_key">
                            <td>
                              <small>
                                <strong>{{key}}</strong>
                              </small>
                            </td>
                            <template v-if="isStringValue(secret_value)">
                              <td>
                                <small>
                                  <samp>{{secret_key}}</samp>
                                </small>
                              </td>
                              <td>
                                <small>
                                  <samp>{{secret_value}}</samp>
                                </small>
                              </td>
                              <td>
                                <small>inline string</small>
                              </td>
                            </template>
                            <template v-else>
                              <td>
                                <small>
                                  <samp>{{secret_key}}</samp>
                                </small>
                              </td>
                              <td>
                                <small>
                                  <samp>{{secret_value.key}}</samp>
                                </small>
                              </td>
                              <td>
                                <small>{{secret_value.type}}</small>
                              </td>
                            </template>
                          </tr>
                        </template>
                      </tbody>
                    </table>

                  </div>
                  <div v-else>
                    <p>This experiment has no secrets.</p>
                  </div>
                </div>
                <div class="column col-12">
                  <div class="my-2" />
                </div>
              </div>
            </div>
            <div class="column col-12">
              <div class="divider my-2" />
            </div>
            <div class="column col-12">
              <h5>Steady-steate Hypothesis</h5>
              <p class="text-gray">The steady-state hypothesis defines the normal state of your system when viewed from the angle of this experiment.
                It is applied twice. Before the experimental method to validate the system is indeed in its normal state.
                After the experimental method to determine if the system has deviated from that normal state.</p>
              <div class="timeline">
                <activity v-bind:activity="activity" v-for="activity in experiment.payload['steady-state-hypothesis'].probes" :key="activity.name"
                />
              </div>
            </div>
            <div class="column col-12">
              <h5>Experimental Method</h5>
              <p class="text-gray">The experimental method is a set of activities that are applied to your system to create perturbations that
                can might help you discover weaknesses. The method may contain probes to collect system data while the experiment
                takes place, they will support your analysis.
              </p>

              <div class="timeline">
                <template v-for="activity in experiment.payload.method">
                  <pause v-bind:type="'before'" v-bind:pause="activity.pauses.before" v-if="activity.pauses && activity.pauses.before" :key="activity.name"
                  />
                  <activity v-bind:activity="activity" :key="activity.name" />
                  <pause v-bind:type="'after'" v-bind:pause="activity.pauses.after" v-if="activity.pauses && activity.pauses.after" :key="activity.name"
                  />
                </template>
              </div>
            </div>
            <div class="column col-12">
              <h5>Rollbacks</h5>
              <p class="text-gray">Rollbacks are remediation actions to try to set your system as close to its normal state as possible. It is
                essential to acknowledge that automated rollbacks is not always achievable and you should probably not rely
                fully on these operations.</p>

              <div class="timeline" v-if="experiment.payload.rollbacks && experiment.payload.rollbacks.length>0">
                <template v-for="activity in experiment.payload.rollbacks">
                  <pause v-bind:type="'before'" v-bind:pause="activity.pauses.before" v-if="activity.pauses && activity.pauses.before" :key="activity.name"
                  />
                  <activity v-bind:activity="activity" :key="activity.name" />
                  <pause v-bind:type="'after'" v-bind:pause="activity.pauses.after" v-if="activity.pauses && activity.pauses.after" :key="activity.name"
                  />
                </template>
              </div>
              <div v-else>
                <p>This experiment declares no rollbacks.</p>
              </div>
            </div>
          </div>
          <div class="panel-footer">
          </div>
        </div>
      </div>
      <div class="column col-12 col-mx-auto">
        <div class="my-2" />
        <div class="my-2" />
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
  import Activity from './Experiment/Activity.vue'
  import Pause from './Experiment/Pause.vue'

  export default Vue.extend({
    components: {
      Breadcrumb,
      MetaInfo,
      Activity,
      Pause
    },
    data: function () {
      return {
        experiment: null
      }
    },
    created: function () {
      this.getExperiment()
    },
    methods: {
      getExperiment: function () {
        const self = this
        const org_name = this.$route.params.org
        const workspace_name = this.$route.params.workspace
        const experiment_id = this.$route.params.experiment
        return axios.get(
            '/'+org_name+'/'+workspace_name+'/experiment/'+experiment_id+'/context', {
            headers: {
              'Accept': 'application/json'
            }
          }
        ).then(response => {
          self.experiment = response.data as any
          self.experiment.payload['steady-state-hypothesis'].probes = response.data.payload['steady-state-hypothesis'].probes.slice()
        }).catch(error => {
          swal({    
            title: `Failed to retrieve your experiment!`,
            text: error.message,
            buttonsStyling: false,
            confirmButtonClass: 'btn btn-primary'
          })
        })
      },
      isStringValue: function(val: any): boolean {
          return typeof(val) === "string"
      }
    }
  })
</script>