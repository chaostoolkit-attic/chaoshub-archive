<template>
  <div class="panel-body" v-if="executions">
    <div class="divider" />
    <div class="timeline">
      <div :id="execution.id" class="timeline-item" v-for="execution in executions" :key="execution.id">
        <div class="timeline-left">
          <a class="timeline-icon icon-lg" :href="'#'+execution.id">
            <i class="icon" />
          </a>
        </div>
        <div class="timeline-content">
          <div class="accordion">
            <input :id="'run-'+execution.id" type="checkbox" name="accordion-checkbox" hidden checked>
            <label class="accordion-header c-hand" :for="'run-'+execution.id">
              <div class="columns">
                <div class="column col-xs-1 col-2">{{formatExecutionDate(execution)}}</div>
                <div class="column col-xs-1 col-1" v-if="execution.result">{{execution.result.duration}}</div>
                <div class="column col-xs-3 col-3" v-if="execution.status">{{execution.status}}</div>
              </div>
            </label>
            <div class="accordion-body">
              <div class="columns">
                <div class="column col-12">
                  <div class="py-2" />
                  <div class="divider" data-content="Details" />
                  <div class="container">
                    <div class="columns">
                      <div class="column col-3"><strong>Start Time</strong></div>
                      <div class="column col-9">2018-05-22T13:39:49.012259</div>
                      <div class="column col-3"><strong>Completion Time</strong></div>
                      <div class="column col-9">2018-05-22T13:42:49.012259</div>
                      <div class="column col-3"><strong>Run on Node</strong></div>
                      <div class="column col-9">sylvain-laptop</div>
                      <div class="column col-3"><strong>Platform</strong></div>
                      <div class="column col-9">Linux-4.15.0-20-generic-x86_64-with-Ubuntu-18.04-bionic</div>
                    </div>
                  </div>
                </div>
                <div class="column col-12">
                  <div class="py-2" />
                  <div class="divider" data-content="Configuration" />
                  <div class="container">
                    <div class="columns">
                      <div class="column col-3"><strong>gce_cluster_name</strong></div>
                      <div class="column col-9">blahbl</div>
                      <div class="column col-3"><strong>gce_project_id</strong></div>
                      <div class="column col-9">wdfgdf</div>
                    </div>
                  </div>
                </div>
                <div class="column col-12">
                  <div class="py-2" />
                  <div class="divider" data-content="Secrets" />
                  <div class="container">
                    <div class="columns">
                      <div class="column col-3"><strong>gce_cluster_name</strong></div>
                      <div class="column col-9">blahbl</div>
                      <div class="column col-3"><strong>gce_project_id</strong></div>
                      <div class="column col-9">wdfgdf</div>
                    </div>
                  </div>
                </div>
                <div class="column col-12">
                  <div class="py-2" />
                  <div class="divider" data-content="Steady State Before System Perturbation" />
                  <div class="container">
                    <div class="columns">
                      <div class="column col-12">
                        <div class="accordion">
                          <input id="accordion-1" type="checkbox" name="accordion-checkbox" hidden>
                          <div class="toast">
                            <label class="accordion-header c-hand" for="accordion-1">
                              <i class="icon icon-caret float-right" /> function-must-exist
                            </label>
                          </div>
                          <div class="accordion-body">
                            <div class="columns">
                              <div class="column col-12">
                                <div class="columns">
                                  <div class="column col-1">
                                    <strong>Type</strong>
                                  </div>
                                  <div class="column col-11">HTTP</div>
                                  <div class="column col-1">
                                    <strong>URL</strong>
                                  </div>
                                  <div class="column col-11">
                                    <div class="text-ellipsis">http://demo.foo.bar/system/function/astre</div>
                                  </div>
                                  <div class="column col-12">
                                    <strong>Headers</strong>
                                  </div>
                                  <div class="column col-12">
                                    <div class="columns">
                                      <div class="column col-2">Authorization: </div>
                                      <div class="column col-10">
                                        <code>${auth}</code>
                                      </div>
                                    </div>
                                  </div>
                                  <div class="column col-12">
                                    <br>
                                  </div>
                                  <div class="column col-1">
                                    <strong>Secrets</strong>
                                  </div>
                                  <div class="column col-11">
                                    <span class="label">global</span>
                                    <span class="label">faas</span>
                                  </div>
                                  <div class="column col-1">
                                    <strong>Timeouts</strong>
                                  </div>
                                  <div class="column col-11">Connection: 3s - Receive: 3s</div>
                                  <div class="column col-1">
                                    <strong>Tolerance</strong>
                                  </div>
                                  <div class="column col-11">200</div>
                                </div>
                              </div>
                              <div class="column col-12">
                                <div class="columns">
                                  <div class="column col-12">
                                    <strong>Output</strong>
                                  </div>
                                  <div class="column col-12">
                                    <pre v-highlightjs>
                                  <code class="JSON"/>
                                </pre>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div class="column col-12">
                        <div class="accordion">
                          <input id="accordion-2" type="checkbox" name="accordion-checkbox" hidden>
                          <div class="toast">
                            <label class="accordion-header c-hand" for="accordion-2">
                              <i class="icon icon-caret float-right" /> function-must-exist
                            </label>
                          </div>
                          <div class="accordion-body">
                            <div class="columns">
                              <div class="column col-12">
                                <div class="columns">
                                  <div class="column col-1">
                                    <strong>Type</strong>
                                  </div>
                                  <div class="column col-11">HTTP</div>
                                  <div class="column col-1">
                                    <strong>URL</strong>
                                  </div>
                                  <div class="column col-11">
                                    <div class="text-ellipsis">http://demo.foo.bar/system/function/astre</div>
                                  </div>
                                  <div class="column col-12">
                                    <strong>Headers</strong>
                                  </div>
                                  <div class="column col-12">
                                    <div class="columns">
                                      <div class="column col-2">Authorization: </div>
                                      <div class="column col-10">
                                        <code>${auth}</code>
                                      </div>
                                    </div>
                                  </div>
                                  <div class="column col-12">
                                    <br>
                                  </div>
                                  <div class="column col-1">
                                    <strong>Secrets</strong>
                                  </div>
                                  <div class="column col-11">
                                    <span class="label">global</span>
                                    <span class="label">faas</span>
                                  </div>
                                  <div class="column col-1">
                                    <strong>Timeouts</strong>
                                  </div>
                                  <div class="column col-11">Connection: 3s - Receive: 3s</div>
                                  <div class="column col-1">
                                    <strong>Tolerance</strong>
                                  </div>
                                  <div class="column col-11">200</div>
                                </div>
                              </div>
                              <div class="column col-12">
                                <div class="columns">
                                  <div class="column col-12">
                                    <strong>Output</strong>
                                  </div>
                                  <div class="column col-12">
                                    <pre v-highlightjs><code class="JSON"/></pre>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="column col-12">
                  <div class="py-2" />
                  <div class="divider" data-content="Experimental Method" />
                  <div class="container">
                    <div class="columns">
                      <div class="column col-12">
                        <div class="accordion">
                          <input id="accordion-3" type="checkbox" name="accordion-checkbox" hidden>
                          <div class="toast">
                            <label class="accordion-header c-hand" for="accordion-3">
                              <i class="icon icon-caret float-right" /> function-must-exist
                            </label>
                          </div>
                          <div class="accordion-body">
                            <div class="columns">
                              <div class="column col-12">
                                <div class="columns">
                                  <div class="column col-1">
                                    <strong>Type</strong>
                                  </div>
                                  <div class="column col-11">HTTP</div>
                                  <div class="column col-1">
                                    <strong>URL</strong>
                                  </div>
                                  <div class="column col-11">
                                    <div class="text-ellipsis">http://demo.foo.bar/system/function/astre</div>
                                  </div>
                                  <div class="column col-12">
                                    <strong>Headers</strong>
                                  </div>
                                  <div class="column col-12">
                                    <div class="columns">
                                      <div class="column col-2">Authorization: </div>
                                      <div class="column col-10">
                                        <code>${auth}</code>
                                      </div>
                                    </div>
                                  </div>
                                  <div class="column col-12">
                                    <br>
                                  </div>
                                  <div class="column col-1">
                                    <strong>Secrets</strong>
                                  </div>
                                  <div class="column col-11">
                                    <span class="label">global</span>
                                    <span class="label">faas</span>
                                  </div>
                                  <div class="column col-1">
                                    <strong>Timeouts</strong>
                                  </div>
                                  <div class="column col-11">Connection: 3s - Receive: 3s</div>
                                  <div class="column col-1">
                                    <strong>Tolerance</strong>
                                  </div>
                                  <div class="column col-11">200</div>
                                </div>
                              </div>
                              <div class="column col-12">
                                <div class="columns">
                                  <div class="column col-12">
                                    <strong>Output</strong>
                                  </div>
                                  <div class="column col-12">
                                    <pre v-highlightjs><code class="JSON" /></pre>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script lang="ts">
  import Vue from 'vue'
  import VueHighlightJS from 'vue-highlightjs'
    import * as moment from 'moment'

  Vue.use(VueHighlightJS)

  export default Vue.extend({
    props: {
        executions: {
            type: Object,
            default: null
        }
    },
    methods: {
      formatExecutionDate: function (activity: any): string {
        if (!activity.timestamp) {
            return '-'
        }
        return moment(activity.timestamp, 'X').calendar()
      }
    }
  })

</script>
