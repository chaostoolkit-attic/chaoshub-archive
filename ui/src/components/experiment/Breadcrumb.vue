<template>
  <div v-if="experiment" class="columns">
    <div class="column col-12 col-mx-auto">
      <div class="columns">
        <div class="column col-9">
          <ul class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link :to="{name: 'org_default'}" tag="a">{{experiment.workspace.org.name}}</router-link>
            </li>
            <li class="breadcrumb-item">
              <router-link :to="{name: 'workspace_default'}" tag="a">{{experiment.workspace.name}}</router-link>
            </li>
            <li class="breadcrumb-item">
              <router-link :to="{name: 'experiment_default'}" tag="a" class="text-ellipsis">{{experiment.payload.title}}</router-link>
            </li>
            <li class="breadcrumb-item">
              {{ pagename }}
            </li>
          </ul>
        </div>
        <!--
        <div class="column col-3">
          <div class="columns">
            <div v-if="canEdit()" class="column col-1 col-mx-auto"></div>
            <div v-else class="column col-4 col-mx-auto"></div>

            <div class="column col-3 mr-1">
              <div class="input-group input-sm">
                <button class="btn btn-sm tooltip" data-tooltip="Bookmark this experiment"><i class="icon icon-bookmark" /></button>
                <input type="text" class="form-input input-sm" value="11">
              </div>
            </div>
            <div class="column col-3">
              <div class="input-group">
                <button class="btn btn-sm tooltip" data-tooltip="Copy and edit this experiment"><i class="icon icon-share" /></button>
                <input type="text" class="form-input input-sm" value="5">
              </div>
            </div>
            <template v-if="canEdit()">
            <div class="column col-1 ml-1">
              <a href="/workspace/mine/experiment/blah/edit" class="btn btn-action btn-secondary btn-sm tooltip" data-tooltip="Edit the experiment">
                <i class="icon icon-edit" />
              </a>
            </div>
            <div class="column col-1"></div>
            <div class="column col-1">
              <a href="/workspace/mine/experiment/blah/settings" class="btn btn-action btn-secondary btn-sm float-right tooltip" data-tooltip="Set the experiment settings">
                <i class="icon icon-more-horiz" />
              </a>
            </div>
            </template>
          </div>
        </div>
        -->
      </div>
    </div>
  </div>
</template>

<script lang='ts'>
  import Vue from 'vue'

  export default Vue.extend({
    props: {
      experiment: {
          type: Object
      },
      pagename: {
          type: String,
          default: "Details"
      }
    },
    methods: {
        canEdit: function () {
            return this.experiment.workspace.context.acls.indexOf('write') > 0
        }
    }
  })
</script>

