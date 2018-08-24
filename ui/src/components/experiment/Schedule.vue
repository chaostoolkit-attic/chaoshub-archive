<template>
  <div class="container" v-if="experiment">
    <breadcrumb v-bind:experiment="experiment" pagename="Schedule" />
    <div class="columns">
      <div class="column col-12 col-mx-auto">
        <div class="card">
          <div class="card-header">
            <div class="card-title h5">Schedule an Execution</div>
            <div class="card-subtitle text-gray">Schedule an experiment's execution</div>
          </div>
          <form v-if="context">
            <div class="card-body" v-if="context.tokens.length===0">
              Before you can schedule an execution, you must create at least one
              <router-link :to="{name: 'account_tokens'}">token</router-link>.
            </div>
            <div class="card-body" v-else>
              <div class="columns">
                <div class="column col-12">
                  <div class="columns">
                    <div class="column col-4 col-mx-auto">
                      <div class="columns">
                        <div class="column col-12">
                          <div class="form-group">
                            <label class="form-label" for="scheduler">Scheduler</label>
                            <select v-model="schedule.scheduler" name="scheduler" class="form-select">
                              <option v-bind:value="scheduler.name" v-for="scheduler in context.schedulers" :key="scheduler.name">
                                {{scheduler.description}} ({{scheduler.version}})
                              </option>
                            </select>
                          </div>
                        </div>
                        <div class="column col-12">
                          <div class="form-group">
                            <label class="form-label" for="token">Token</label>
                            <select v-model="schedule.token" name="token" class="form-select">
                              <option v-bind:value="token.id" v-for="token in context.tokens" :key="token.id">
                                {{token.name}}
                              </option>
                            </select>
                          </div>
                        </div>
                        <div class="column col-12">
                          <div class="form-group">
                            <label class="form-label" for="date">Date</label>
                            <input type="date" id="day" placeholder="Date" class="form-input" v-model="schedule.date" />
                          </div>
                        </div>
                        <div class="column col-12">
                          <div class="form-group">
                            <label class="form-label" for="time">Time</label>
                            <input type="time" id="time" placeholder="Time" class="form-input" v-model="schedule.time" />
                          </div>
                        </div>
                        <div class="column col-12">
                          <div class="my-2" />
                          <div class="form-group">
                            <button class="btn btn-primary input-group-btn" @click.prevent="scheduleExecution">Schedule execution</button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="column col-12">
                  <div class="divider" />
                </div>
                <div class="column col-12">
                  <h5>Past Schedules</h5>
                  <p v-if="context.schedules.length===0">
                    You have not scheduled any execution of this experiment yet.
                  </p>
                  <div v-else class="timeline">
                    <div class="timeline-item" :id="schedule.id" v-for="schedule in context.schedules" :key="schedule.id">
                      <div class="timeline-left">
                        <a class="timeline-icon" :href="'#'+schedule.id"></a>
                      </div>
                      <div class="timeline-content">
                        {{getScheduleDate(schedule)}}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue'
  import axios from 'axios'
  import swal from 'sweetalert2'
  import * as moment from 'moment'
  import Breadcrumb from './Breadcrumb.vue'
  import MetaInfo from './Experiment/MetaInfo.vue'

  export default Vue.extend({
    components: {
      Breadcrumb,
      MetaInfo
    },
    data: function () {
      return {
        experiment: null,
        context: null,
        schedule: {
            date: moment().format('YYYY-MM-DD'),
            time: moment().format('HH:mm'),
            token: null,
            scheduler: null
        }
      }
    },
    created: function () {
      this.$nextTick(function () {
        this.getContext()
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
            '/'+org_name+'/'+workspace_name+'/experiment/'+experiment_id+'/context', {
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
      getContext: function () {
        const self = this
        const org_name = this.$route.params.org
        const workspace_name = this.$route.params.workspace
        const experiment_id = this.$route.params.experiment
        return axios.get(
            '/'+org_name+'/'+workspace_name+'/experiment/'+experiment_id+'/schedule/with/context', {
            headers: {
              'Accept': 'application/json'
            }
          }
        ).then(response => {
          self.context = response.data as any
        }).catch(error => {
          swal({    
            title: `Failed to retrieve your context!`,
            text: error.message,
            buttonsStyling: false,
            confirmButtonClass: 'btn btn-primary'
          })
        })
      },
      scheduleExecution: function () {
        const self = this
        const org_name = this.$route.params.org
        const workspace_name = this.$route.params.workspace
        const experiment_id = this.$route.params.experiment
        return axios.post(
            '/'+org_name+'/'+workspace_name+'/experiment/'+experiment_id+'/schedule',
            self.schedule,
            {headers: {'Accept': 'application/json'}}
        ).then(response => {
            self.context.schedules.push(response.data as any)
        }).catch(error => {
          swal({    
            title: `Failed to schedule an execution!`,
            text: error.message,
            buttonsStyling: false,
            confirmButtonClass: 'btn btn-primary'
          })
        })
      },
    getScheduleDate: function (schedule: any): string {
      if (!schedule.scheduled) {
        return '-'
      }
      return moment(schedule.scheduled, moment.HTML5_FMT.DATETIME_LOCAL_SECONDS + 'Z').calendar()
    },
    }
  })
</script>
