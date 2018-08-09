<template>
  <div class="columns">
    <div class="column col-12">
      <div class="divider" data-content="Details" />
      <div class="container">
        <div class="columns">
          <div class="column col-3">
            <strong>Status</strong>
          </div>
          <div class="column col-9">
              <span class="text-danger">Failed</span>
           </div>
          <div class="column col-3">
            <strong>Start Time</strong>
          </div>
          <div class="column col-9">2018-07-22T13:39:49.012259</div>
          <div class="column col-3">
            <strong>Completion Time</strong>
          </div>
          <div class="column col-9">2018-07-22T13:42:49.012259</div>
          <div class="column col-3">
            <strong>Run on Node</strong>
          </div>
          <div class="column col-9">sylvain-laptop</div>
          <div class="column col-3">
            <strong>Platform</strong>
          </div>
          <div class="column col-9">Linux-4.15.0-20-generic-x86_64-with-Ubuntu-18.04-bionic</div>
        </div>
      </div>
    </div>
    <div class="column col-12">
      <div class="py-2" />
      <div class="divider" data-content="Configuration" />
      <div class="container">
        <div class="columns">
          <div class="column col-3">
            <strong>gce_cluster_name</strong>
          </div>
          <div class="column col-9">demos-cluster</div>
          <div class="column col-3">
            <strong>gce_project_id</strong>
          </div>
          <div class="column col-9">chaosiqdemos</div>
          <div class="column col-3">
            <strong>gce_region</strong>
          </div>
          <div class="column col-9">us-west1</div>
          <div class="column col-3">
            <strong>gce_zone</strong>
          </div>
          <div class="column col-9">us-west1-a</div>
          <div class="column col-3">
            <strong>prometheus_base_url</strong>
          </div>
          <div class="column col-9">http://demo.foo.bar</div>
        </div>
      </div>
    </div>
    <div class="column col-12">
      <div class="py-2" />
      <div class="divider" data-content="Secrets" />
      <div class="container">
        <div class="columns">
          <div class="column col-3">
            <strong>gce</strong>
          </div>
          <div class="column col-3">service_account_file</div>
          <div class="column col-6">~/my-gce-sa-credentials.json</div>
          <div class="column col-3">
            <strong>global</strong>
          </div>
          <div class="column col-3">auth</div>
          <div class="column col-7">Basic amFuZTpkZW1v</div>
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
                  <i class="icon icon-caret float-right" /> function-must-respond
                </label>
              </div>
              <div class="accordion-body">
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
                  <i class="icon icon-caret float-right" /> simulate-user-traffic-under-moderate-load
                </label>
              </div>
              <div class="accordion-body">
              </div>
            </div>
          </div>
          <div class="column col-12">
            <div class="accordion">
              <input id="accordion-3" type="checkbox" name="accordion-checkbox" hidden>
              <div class="toast">
                <label class="accordion-header c-hand" for="accordion-3">
                  <i class="icon icon-caret float-right" /> create-a-new-nodepool-and-swap-to-it
                </label>
              </div>
              <div class="accordion-body">
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="column col-12">
      <div class="py-2" />
      <div class="divider" data-content="Rollbacks" />
      <div class="container">
        <div class="columns">
          <div class="column col-12">
            <div class="accordion">
              <input id="accordion-3" type="checkbox" name="accordion-checkbox" hidden>
              <div class="toast">
                <label class="accordion-header c-hand" for="accordion-3">
                  <i class="icon icon-caret float-right" /> uncordon-old-nodepool
                </label>
              </div>
              <div class="accordion-body">
              </div>
            </div>
          </div>
          <div class="column col-12">
            <div class="accordion">
              <input id="accordion-3" type="checkbox" name="accordion-checkbox" hidden>
              <div class="toast">
                <label class="accordion-header c-hand" for="accordion-3">
                  <i class="icon icon-caret float-right" /> delete-new-nodepool
                </label>
              </div>
              <div class="accordion-body">
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

  Vue.use(VueHighlightJS)

  export default Vue.extend({

  })

</script>
