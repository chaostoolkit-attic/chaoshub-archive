<template>
  <div class="panel-header">
    <div class="panel-title h5 mt-10">
      {{experiment.payload.title}}
    </div>
    <div class="columns">
      <div class="column col-12">
        <p>{{experiment.payload.description}}</p>
      </div>
    </div>
    <div class="columns">
      <div class="column col-8">
        <div class="label mx-1" v-for="tag in experiment.payload.tags" :key="tag">{{tag}}</div>
      </div>
      <template v-if="this.$route.name==='experiment_default'">
        <div class="column col-4">
          <div class="columns">
            <div class="column col-4">
              <template v-if="hasPermissions()">
                <router-link :to="{name: 'experiment_runs'}" tag="button" class="btn btn-secondary btn-lg">
                  Executions
                  <i class="icon icon-arrow-right" />
                </router-link>
              </template>
            </div>
            <div class="column col-4">
              <template v-if="hasPermissions()">
                <router-link :to="{name: 'experiment_schedule'}" tag="button" class="btn btn-secondary btn-lg">
                  Schedule
                  <i class="icon icon-time" />
                </router-link>
              </template>
            </div>
            <div class="column col-4">
              <li class="dropdown">
                <button class="btn btn-lg btn-primary dropdown-toggle" tabindex="0">Download
                  <i class="icon icon-download" />
                </button>
                <ul class="menu download-exp">
                  <li>
                    <label class="form-label" for="cli">Using the
                      <a href="https://chaostoolkit.org">chaos</a> command:</label>
                    <div class="input-group">
                      <button class="input-group-addon btn btn-action">
                        <i class="icon icon-edit"></i>
                      </button>
                      <input class="form-input" type="text" id="cli" readonly :value="getCLIValue()" />
                    </div>
                  </li>
                  <li class="divider text-center" data-content="OR"></li>
                  <li>
                    <div class="columns">
                      <div class="column col-6">
                        <a class="btn btn-block btn-primary" download :href="'/'+experiment.workspace.org.name+'/'+experiment.workspace.name+'/experiment/'+experiment.id+'/download/json'">Download as JSON</a>
                      </div>
                      <div class="column col-6">
                        <a class="btn btn-block btn-primary" download :href="'/'+experiment.workspace.org.name+'/'+experiment.workspace.name+'/experiment/'+experiment.id+'/download/yaml'">Download as YAML</a>
                      </div>
                    </div>
                  </li>
                </ul>
              </li>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
<script lang="ts">
  import Vue from 'vue'
  export default Vue.extend({
    props: {
      experiment: {
        type: Object,
        default: null
      }
    },
    methods: {
      getCLIValue: function (): string {
        return 'chaos run --org ' + this.experiment.workspace.org.name + ' --workspace ' + this.experiment.workspace.name +
          ' ' + this.experiment.url
      },
      hasPermissions: function (): boolean {
          return this.experiment && this.experiment.requested_by &&
            (this.experiment.requested_by.org_owner ||
             this.experiment.requested_by.org_member ||
             this.experiment.requested_by.workspace_owner ||
             this.experiment.requested_by.workspace_collaborator)
      }
    }
  })

</script>
