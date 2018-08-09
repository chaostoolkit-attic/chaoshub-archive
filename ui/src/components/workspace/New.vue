<template>
  <div class="container">
    <div class="columns">
        <div class="column col-9 col-mx-auto">
          <div class="card">
            <div class="card-header">
              <div class="card-title h5">Create a new Workspace</div>
              <div class="card-subtitle text-gray">Group related experiments together</div>
            </div>
            <div class="card-body">
              <form class="form-horizontal">
                <div class="form-group">
                  <label class="form-label" for="title">Title</label>
                  <input id="name" class="form-input" type="text" placeholder="Name your workspace">
                </div>
                <div class="form-group">
                  <label class="form-label" for="visibility">Visibility</label>
                  <div class="columns">
                    <div class="col-12 col-xs-12">
                      <label class="form-radio">
                        <input type="radio" name="visibility" checked>
                        <i class="form-icon"/> Public
                        <p class="form-input-hint">Everyone, even non members, will be able to view public experiments in this workspace</p>
                      </label>
                    </div>
                    <div class="col-12 col-xs-12">
                      <label class="form-radio">
                        <input type="radio" name="visibility">
                        <i class="form-icon"/> Private
                          <p class="form-input-hint">Only allowed members can collaborate on private experiments of this workspace</p>
                      </label>
                    </div>
                  </div>
                </div>
              </form>
            </div>
            <div class="card-footer">
              <div class="form-group">
                <button class="btn btn-primary input-group-btn">Create workspace</button>
                <button class="btn btn-secondary input-group-btn float-right">Cancel</button>
              </div>
            </div>
          </div>
        </div>
    </div>
  </div>
</template>
<script lang='ts'>
import Vue from "vue"

export default Vue.extend({
})
</script>