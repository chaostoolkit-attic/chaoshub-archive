# Status of the Chaos Hub Project

This page does not replace the list of issues tracked in the project but
should offer a quick overview of the main axes of improvements, in no
particular order.

## General Status

Currently, the project is in early stages. It does run and can get you some
way but is not be production-ready yet. It is meant to be used as-is for
exploring its use case and please send the project your feedback on its missing bits.

## Features Matrix

* Allow experiment editing from the UI [TODO]
  As of now, you still need to edit your experiment manually and the Hub only
  renders it. We will obviously make it so you can create and edit them from
  the UI.
* Complete the local launcher of Chaos Toolkit instances [WIP]
  Currently, the local launcher built into the Chaos Hub is working but is
  rough around the edges. It needs to be more battle tested.
* Implement the CRON launcher [TODO]
  The CRON launcher is not yet implemented properly and cannot be used at this
  stage.
* Respect the Schedule [TODO]
  Right now, when you Schedule, the execution starts immediatly. Obviously,
  we want to abide by the date and time set by the user
* Finish the execution view [WIP]
  The view of your past executions is not completed yet and will likely break
  to render properly.
* Improve the past scheduling view [TODO]
* Write end-user documentation [TODO]
* Ensure user profile can be edited [TODO]
* Create a Privacy editing page [TODO]

## Code Status

The current status of the code is an honorable "meh". This means that we had
to take a few shortcuts in keeping it elegant and well tested.

* Re-work the unit tests [WIP]
* Cleanup the Vue.js templates [TODO]
* Fix docstrings [TODO]
* Write contributor guidelines [TODO]
