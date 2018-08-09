<template>
  <div class="column col-9">
    <h4>General</h4>
    <div class="divider" />
    <div class="columns">
      <div class="column col-8">
          <form class="form-horizontal">
            <div class="form-group">
              <div class="col-3 col-sm-12">
                <label class="form-label" for="input-example-1">Experiment name</label>
              </div>
              <div class="col-7 col-sm-12">
                <input id="input-example-1" class="form-input" type="text" placeholder="Name">
              </div>
              <div class="col-2 col-sm-12">
                <button class="btn btn-primary">Rename</button>
              </div>
            </div>
            <p class="form-input-hint">Note that changing the name of your experiment will
              break its URL. Be considerate for your users!
            </p>
          </form>
      </div>
    </div>
    <div class="panel">
      <div class="panel-header">
        <div class="panel-title"><h5>Administration</h5></div>
      </div>
      <div class="panel-body">
        <div class="columns">
          <div class="column col-12">
            <div class="divider" />
          </div>
          <div class="column col-12">
            <div class="tile">
              <div class="tile-content">
                <p class="tile-title"><strong>Make private</strong></p>
                <p class="tile-subtitle text-gray">Make this experiment private so only allowed collaborators can view and edit it.</p>
              </div>
              <div class="tile-action"><button class="btn btn-error btn-primary">Make private</button></div>
            </div>
          </div>
          <div class="column col-12">
            <div class="divider" />
          </div>
          <div class="column col-12">
            <div class="tile">
              <div class="tile-content">
                <p class="tile-title"><strong>Move workspace</strong></p>
                <p class="tile-subtitle text-gray">Move to a different workspace. This will impact the URL of this experiment.</p>
              </div>
              <div class="tile-action"><button class="btn btn-error btn-primary">Transfer</button></div>
            </div>
          </div>
          <div class="column col-12">
            <div class="divider" />
          </div>
          <div class="column col-12">
            <div class="tile">
              <div class="tile-content">
                <p class="tile-title"><strong>Delete this experiment</strong></p>
                <p class="tile-subtitle text-gray">Deleting an experiment cannot be reversed.</p>
              </div>
              <div class="tile-action"><button class="btn btn-error btn-primary">Delete</button></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
