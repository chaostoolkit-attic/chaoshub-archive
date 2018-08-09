import Vue from 'vue'
import VueRouter, {
  Location,
  Route,
  RouteConfig
} from 'vue-router'

Vue.use(VueRouter)

const userComponent = () =>
  import('./components/user/User.vue').then((User) => User)

const orgComponent = () =>
  import('./components/org/Org.vue').then((Org) => Org)

const orgSettingsComponent = () =>
  import('./components/org/Settings.vue').then((Settings) => Settings)

const orgSettingsMembersComponent = () =>
  import('./components/org/Settings/Members.vue').then((Members) => Members)

const orgSettingsGeneralComponent = () =>
  import('./components/org/Settings/General.vue').then((General) => General)

const workspaceComponent = () =>
  import('./components/workspace/Workspace.vue').then((Workspace) => Workspace)

const workspaceSettingsComponent = () =>
  import('./components/workspace/Settings.vue').then((Settings) => Settings)

const workspaceSettingsGeneralComponent = () =>
  import('./components/workspace/Settings/General.vue').then((General) => General)

const workspaceSettingsCollaboratorsComponent = () =>
  import('./components/workspace/Settings/Collaborators.vue').then((Collaborators) => Collaborators)

const experimentMainComponent = () =>
  import('./components/experiment/Main.vue').then((Main) => Main)

const newExperimentComponent = () =>
  import('./components/experiment/New.vue').then((New) => New)

const newWorkspaceComponent = () =>
  import('./components/workspace/New.vue').then((New) => New)

const experimentSettingsComponent = () =>
  import('./components/experiment/Settings.vue').then((Settings) => Settings)

const experimentCollaboratorSettingsComponent = () =>
  import('./components/experiment/Settings/Collaborators.vue').then((Collaborators) => Collaborators)

const experimentGeneralSettingsComponent = () =>
  import('./components/experiment/Settings/General.vue').then((General) => General)

const experimentExecutionComponent = () =>
  import('./components/experiment/Execution.vue').then((Execution) => Execution)

const experimentExecutionsComponent = () =>
  import('./components/experiment/Executions.vue').then((Executions) => Executions)

const experimentScheduleComponent = () =>
  import('./components/experiment/Schedule.vue').then((Schedule) => Schedule)

const signinComponent = () =>
  import('./components/SignIn.vue').then((SignIn) => SignIn)

const signupComponent = () =>
  import('./components/SignUp.vue').then((SignUp) => SignUp)

const accountComponent = () =>
  import('./components/account/Account.vue').then((Account) => Account)

const allUserExperimentComponent = () =>
  import('./components/experiment/List.vue').then((List) => List)

const notFoundComponent = () =>
  import('./components/NotFound.vue').then((NotFound) => NotFound)

export const createRoutes: () => RouteConfig[] = () => [
  {
    path: '/',
    name: 'user_home',
    component: userComponent
  },
  {
    path: '/signin',
    component: signinComponent
  },
  {
    path: '/signup',
    component: signupComponent
  },
  {
    path: '/account',
    component: accountComponent,
    children: [
      {
        path: '/account/profile',
        name: 'account_profile',
        component: accountComponent
      },
      {
        path: '/account/tokens',
        name: 'account_tokens',
        component: accountComponent
      },
      {
        path: '/account/privacy',
        name: 'account_privacy',
        component: accountComponent
      },
      {
        path: '/account/orgs',
        name: 'account_orgs',
        component: accountComponent
      },
      {
        path: '/account/workspaces',
        name: 'account_workspaces',
        component: accountComponent
      }
    ]
  },
  {
    path: '/experiment',
    component: allUserExperimentComponent
  },
  {
    path: '/experiment/new',
    component: newExperimentComponent
  },
  {
    path: '/:org/:workspace/experiment/:experiment',
    component: experimentMainComponent,
    name: 'experiment_default'
  },
  {
    path: '/:org',
    component: orgComponent,
    name: 'org_default'
  },
  {
    path: '/:org/settings',
    name: 'org_settings',
    redirect: '/:org/settings/general',
    components: {
      default: orgSettingsComponent,
      org_settings_view: orgSettingsGeneralComponent
    },
    children: [
      {
        path: 'general',
        name: 'org_settings_general',
        props: {
          org_settings_view: true
        },
        components: {
          org_settings_view: orgSettingsGeneralComponent
        }
      },
      {
        path: 'members',
        name: 'org_settings_members',
        props: {
          org_settings_view: true
        },
        components: {
          org_settings_view: orgSettingsMembersComponent
        }
      }]
  },
  {
    path: '/:org/:workspace',
    component: workspaceComponent,
    name: 'workspace_default'
  },
  {
    path: '/:org/:workspace/settings',
    name: 'workspace_settings',
    redirect: '/:org/:workspace/settings/general',
    components: {
      default: workspaceSettingsComponent,
      workspace_settings_view: workspaceSettingsCollaboratorsComponent
    },
    children: [
      {
        path: 'general',
        name: 'workspace_settings_general',
        props: {
          workspace_settings_view: true
        },
        components: {
          workspace_settings_view: workspaceSettingsGeneralComponent
        }
      },
      {
        path: 'collaborators',
        name: 'workspace_settings_collaborators',
        props: {
          workspace_settings_view: true
        },
        components: {
          workspace_settings_view: workspaceSettingsCollaboratorsComponent
        }
      }]
  },
  {
    path: '/:org/:workspace/experiment/:experiment/execution',
    name: 'experiment_runs',
    component: experimentExecutionsComponent
  },
  {
    path: '/:org/:workspace/experiment/:experiment/schedule',
    name: 'experiment_schedule',
    component: experimentScheduleComponent
  },
  {
    path: '/:org/:workspace/experiment/:experiment/execution/:execution',
    name: 'experiment_execution',
    component: experimentExecutionComponent
  },
  {
    path: '/workspace/new',
    component: newWorkspaceComponent
  },
  {
    path: '/:org/:workspace/experiment/:experiment/settings',
    name: 'settings',
    components: {
      default: experimentSettingsComponent,
      settings_view: experimentGeneralSettingsComponent
    },
    children: [
      {
        path: 'general',
        name: 'settings_general',
        props: {
          settings_view: true
        },
        components: {
          settings_view: experimentGeneralSettingsComponent
        }
      },
      {
        path: 'collaborators',
        name: 'settings_collaborators',
        props: {
          settings_view: true
        },
        components: {
          settings_view: experimentCollaboratorSettingsComponent
        }
      }
    ]
  },
  {
    path: '*',
    component: notFoundComponent
  }
]

export const createRouter = () =>
  new VueRouter({
    mode: 'history',
    linkActiveClass: 'active',
    routes: createRoutes()
  })
