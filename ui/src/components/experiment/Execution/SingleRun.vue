<template>
  <div class="columns">
    <div class="column col-12">
      <div class="divider" data-content="Details" />
      <div class="columns">
        <div class="column col-3">
          <strong>Status</strong>
        </div>
        <div class="column col-9">
          <span class="text-danger">{{execution.result.status}}</span>
        </div>
        <div class="column col-3">
          <strong>Start Time</strong>
        </div>
        <div class="column col-9">{{execution.result.start}}</div>
        <div class="column col-3">
          <strong>Completion Time</strong>
        </div>
        <div class="column col-9">{{execution.result.end}}</div>
        <div class="column col-3">
          <strong>Run on Node</strong>
        </div>
        <div class="column col-9">{{execution.result.node}}</div>
        <div class="column col-3">
          <strong>Platform</strong>
        </div>
        <div class="column col-9">{{execution.result.platform}}</div>
      </div>
    </div>
    <div class="column col-12">
      <div class="columns">
        <div class="column col-6">
          <div class="py-2" />
          <div class="divider" data-content="Steady State Before System Perturbation" />
          <div class="columns">
            <div class="column col-12" v-if="execution.result.steady_states.before">
              <div class="accordion">
                <template v-for="before in execution.result.steady_states.before.probes">
                  <input :key="before.activity.name+'-before'" :id="before.activity.name+'-before'" type="checkbox" name="accordion-checkbox"
                    hidden>
                  <div :key="before.activity.name+'-before'" v-bind:class="{ toast: true, 'toast-success': before.tolerance_met, 'toast-error': !before.tolerance_met }">
                    <label class="accordion-header c-hand" :for="before.activity.name+'-before'">
                      <i class="icon icon-caret float-right" /> {{before.activity.name}}
                    </label>
                  </div>
                  <div :key="before.activity.name+'-before'" class="accordion-body">
                    <div class="columns">
                      <div class="column col-4">
                        <strong>Run to Completion</strong>
                      </div>
                      <div class="column col-8">
                        <span class="text-danger">{{before.status}}</span>
                      </div>
                      <div class="column col-4">
                        <strong>Start Time</strong>
                      </div>
                      <div class="column col-8">{{before.start}}</div>
                      <div class="column col-4">
                        <strong>Completion Time</strong>
                      </div>
                      <div class="column col-8">{{before.end}}</div>
                      <div class="column col-4">
                        <strong>Tolerance Checked</strong>
                      </div>
                      <div class="column col-8">
                        <span class="text-danger">{{before.tolerance_met}}</span>
                      </div>
                      <div class="column col-4">
                        <strong>Output</strong>
                      </div>
                      <div class="column col-8">
                        <small>
                          <samp>{{before.output}}</samp>
                        </small>
                      </div>
                    </div>
                  </div>
                </template>
              </div>
            </div>
            <div v-else class="column col-12">
              Steady state before the method was not executed.
            </div>
          </div>
        </div>
        <div class="column col-6">
          <div class="py-2" />
          <div class="divider" data-content="Steady State After System Perturbation" />
          <div class="columns">
            <div class="column col-12" v-if="execution.result.steady_states.after">
              <div class="accordion">
                <template v-for="after in execution.result.steady_states.after.probes">
                  <input :key="after.activity.name+'-after'" :id="after.activity.name+'-after'" type="checkbox" name="accordion-checkbox" hidden>
                  <div :key="after.activity.name+'-after'" v-bind:class="{ toast: true, 'toast-success': after.tolerance_met, 'toast-error': !after.tolerance_met }">
                    <label class="accordion-header c-hand" :for="after.activity.name+'-after'">
                      <i class="icon icon-caret float-right" /> {{after.activity.name}}
                    </label>
                  </div>
                  <div :key="after.activity.name+'-after'" class="accordion-body">
                    <div class="columns">
                      <div class="column col-4">
                        <strong>Run to Completion</strong>
                      </div>
                      <div class="column col-8">
                        <span class="text-danger">{{after.status}}</span>
                      </div>
                      <div class="column col-4">
                        <strong>Start Time</strong>
                      </div>
                      <div class="column col-8">{{after.start}}</div>
                      <div class="column col-4">
                        <strong>Completion Time</strong>
                      </div>
                      <div class="column col-8">{{after.end}}</div>
                      <div class="column col-4">
                        <strong>Tolerance Checked</strong>
                      </div>
                      <div class="column col-8">
                        <span class="text-danger">{{after.tolerance_met}}</span>
                      </div>
                      <div class="column col-3">
                        <strong>Output</strong>
                      </div>
                      <div class="column col-9">
                        <small>
                          <samp>{{after.output}}</samp>
                        </small>
                      </div>
                    </div>
                  </div>
                </template>
              </div>
            </div>
            <div v-else class="column col-12">
              Steady state after the method was not executed.
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="column col-12">
      <div class="py-2" />
      <div class="divider" data-content="Method" />
      <div class="columns">
        <div class="column col-12" v-if="execution.result.run.length>0">
          <div class="accordion">
            <template v-for="method in execution.result.run">
              <input :key="method.activity.name+'-method'" :id="method.activity.name+'-method'" type="checkbox" name="accordion-checkbox"
                hidden>
              <div :key="method.activity.name+'-method'" class="toast">
                <label class="accordion-header c-hand" :for="method.activity.name+'-method'">
                  <i class="icon icon-caret float-right" /> {{method.activity.name}}
                </label>
              </div>
              <div :key="method.activity.name+'-method'" class="accordion-body">
                <div class="columns">
                  <div class="column col-4">
                    <strong>Run to Completion</strong>
                  </div>
                  <div class="column col-8">
                    <span class="text-danger">{{method.status}}</span>
                  </div>
                  <div class="column col-4">
                    <strong>Start Time</strong>
                  </div>
                  <div class="column col-8">{{method.start}}</div>
                  <div class="column col-4">
                    <strong>Completion Time</strong>
                  </div>
                  <div class="column col-8">{{method.end}}</div>
                  <div class="column col-4">
                    <strong>Output</strong>
                  </div>
                  <div class="column col-8">
                    <small>
                      <samp>{{method.output}}</samp>
                    </small>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </div>
        <div v-else class="column col-12">
            Method was not executed.
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue'
  import VueHighlightJS from 'vue-highlightjs'

  Vue.use(VueHighlightJS)

  export default Vue.extend({
    props: {
      execution: {
          type: Object
      }
    }
  })

</script>
