<template>
  <div class="column col-9">
    <h4>Collaborators</h4>
    <div class="divider" />
    <div class="panel">
      <div class="panel-header">
        <div class="panel-title"><h5>Manage</h5></div>
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
