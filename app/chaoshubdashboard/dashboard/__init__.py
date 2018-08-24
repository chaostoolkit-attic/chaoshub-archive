# -*- coding: utf-8 -*-
from datetime import datetime
from functools import wraps
from operator import itemgetter
import random
from typing import Any, Dict, List, NoReturn, Optional, Tuple, Union

from flask import abort, current_app, redirect, url_for
import shortuuid
from sqlalchemy import or_
from sqlalchemy.dialects.postgresql.json import JSON
from sqlalchemy.sql.expression import cast

from chaoshubdashboard.model import db

from .model import WorkpacesMembers, OrgsMembers, UserPrivacy, Org, \
    OrgType, UserPrivacy, UserAccount, UserInfo, WorkspaceType, \
    ExecutionVisibility, Activity, ActivityVisibility, Workspace
from .types import ProfileInfo, UserClaim, Workspace as _Workspace

__all__ = ["fully_delete_user_info", "register_user", "create_user_account",
           "set_user_profile", "set_user_privacy", "get_workspace_by_id",
           "add_default_org_to_account", "add_public_workspace_to_account",
           "add_private_workspace_to_account", "is_visible_to_user",
           "is_org_viewable", "get_org_from_url", "get_workspace_from_url",
           "can_org_be_deleted", "load_org", "load_org_and_workspace",
           "lookup_users", "lookup_collaborators", "lookup_members",
           "lookup_workspaces", "get_account_activities", "get_caller_info"]

# we disallow some characters in organization names and we replace them
# with a much safer dash character
ORG_TRANSLATE = str.maketrans(" /\"'.%", "------")
GENERIC_NAMES = (
    'Urur',
    'Arin',
    'Susa',
    'Harri',
    'Marqash',
    'Archech',
    'Nisa',
    'Cutho',
    'Ashud',
    'Caleuc',
    'Satium',
    'Magius',
    'Londius',
    'Metia',
    'Caesius',
    'Apunus',
    'Salia',
    'Ontinum',
    'Lania',
    'Abratus'
)


def register_user(user_claim: UserClaim, profile: ProfileInfo):
    """
    Create a new account from a OpenID user description as well as a Client
    id/secret pair for that user.

    .. seealso:
        http://openid.net/specs/openid-connect-basic-1_0-28.html#userinfo
    """
    account = create_user_account(user_claim)
    set_user_profile(account, profile)
    set_user_privacy(account)

    org_name = profile.get("preferred_username")
    if not org_name:
        org_name = profile.get("name")
    if not org_name:
        org_name = random.choice(GENERIC_NAMES)

    org = add_default_org_to_account(account, org_name)
    add_private_workspace_to_account(account, org)
    add_public_workspace_to_account(account, org)

    db.session.commit()


def create_user_account(user_claim: UserClaim) -> UserAccount:
    """
    Create a user account from the given user claim that is generated by the
    Auth service.
    """
    account = UserAccount(id=user_claim["id"])
    db.session.add(account)
    return account


def get_caller_info(user_claim: UserClaim, org_id: str,
                    workspace_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch the calling user's context
    """
    account_id = user_claim["id"]
    account = UserAccount.query.filter(UserAccount.id==account_id).first()
    if not account:
        return None

    caller = account.to_short_dict()
    if org_id:
        org = Org.query.filter(Org.id==org_id).first()
        caller["org_member"] = org.is_member(account_id)
        caller["org_owner"] = org_owner = org.is_owner(account_id)

    if workspace_id:
        workspace = Workspace.query.filter(
            Workspace.id==workspace_id).first()
        caller["workspace_collaborator"] = workspace.is_collaborator(
            account_id)
        caller["workspace_owner"] = workspace.is_owner(account_id)
    return caller


def set_user_profile(account: UserAccount, profile: ProfileInfo) -> UserInfo:
    """
    Set the profile of the account from the OpenID user info.

    .. seealso:
        http://openid.net/specs/openid-connect-basic-1_0-28.html#userinfo
    """
    user_info = UserInfo(
        profile=profile, username=profile.get("preferred_username"),
        fullname=profile.get("name"))
    account.info = user_info
    db.session.add(user_info)
    return user_info


def set_user_privacy(account: UserAccount) -> UserPrivacy:
    """
    Set the default privacy settings for the account.
    """
    account.privacy = UserPrivacy()
    db.session.add(account.privacy)
    return account.privacy


def add_default_org_to_account(account: UserAccount, org_name: str) -> Org:
    """
    Create the account's default organization.

    If an org already exists with that name, add a random suffix to it.
    """
    org_name = org_name.translate(ORG_TRANSLATE)
    # we don't want to flush yet as some of the account's details are not yet
    # computed
    with db.session.no_autoflush:
        org_name = Org.get_next_available_name(org_name)

    personal_org = Org(
        name=org_name, name_lower=org_name.lower(), kind=OrgType.personal)
    org_assoc = OrgsMembers(
        organization=personal_org, account=account, is_owner=True)
    account.personal_org = personal_org
    db.session.add(org_assoc)
    db.session.add(personal_org)
    return personal_org


def add_private_workspace_to_account(account: UserAccount,
                                     org: Org) -> Workspace:
    """
    Create the account's personal workspace to the given organization.
    """
    workspace = Workspace(
        name="Personal", name_lower="personal", kind=WorkspaceType.personal)
    assoc = WorkpacesMembers(
        account=account, workspace=workspace, is_owner=True)
    org.workspaces.append(workspace)
    db.session.add(workspace)
    db.session.add(assoc)
    return workspace


def add_public_workspace_to_account(account: UserAccount,
                                    org: Org) -> Workspace:
    """
    Create a public workspace to the given organization.
    """
    workspace = Workspace(
        name="Public", name_lower="public", kind=WorkspaceType.public)
    assoc = WorkpacesMembers(
        account=account, workspace=workspace, is_owner=True)
    org.workspaces.append(workspace)
    db.session.add(workspace)
    db.session.add(assoc)
    return workspace


def fully_delete_user_info(user_claim: UserClaim):
    """
    Delete this user personal data for good.
    """
    account = UserAccount.query.filter(
        UserAccount.id==user_claim["id"]).first()
    account.is_closed = True
    account.closed_dt = datetime.utcnow()
    db.session.commit()

    assocs = WorkpacesMembers.query.filter(
        WorkpacesMembers.account.id==account.id).all()

    for assoc in assocs:
        if assoc.workspace.kind == WorkspaceType.personal:
            db.session.delete(assoc.workspace)
            break

    UserInfo.query.filter(UserInfo.account.id==account.id).delete()
    UserPrivacy.query.filter(UserPrivacy.account.id==account.id).delete()

    db.session.commit()


def lookup_users(q: str, count: int = 10) -> List[Dict[str, str]]:
    q = (q or "").strip()
    if not q or len(q) > 24:
        return []

    matches = UserInfo.query.filter(
        or_(
            UserInfo.username.ilike("%{}%".format(q)),
            UserInfo.fullname.ilike("%{}%".format(q))
        )
    ).limit(count)

    return [{
        "id": shortuuid.encode(m.account_id),
        "name": m.fullname,
        "username": m.username
    } for m in matches]


def lookup_members(o: Org, q: str, count: int = 10) -> List[Dict[str, str]]:
    q = (q or "").strip()
    if not q or len(q) > 24:
        return []

    matches = UserAccount.query.filter(UserAccount.id.in_(
        db.session.query(OrgsMembers.account_id)
        .filter(OrgsMembers.org_id==o.id)
        .filter(OrgsMembers.account_id.in_(
            db.session.query(UserInfo.account_id).filter(
                or_(
                    UserInfo.username.ilike("%{}%".format(q)),
                    UserInfo.fullname.ilike("%{}%".format(q))
                )
            )
        )).limit(count)))

    return [m.to_short_dict() for m in matches]


def lookup_collaborators(w: Workspace, q: str,
                         count: int = 10) -> List[Dict[str, str]]:
    q = (q or "").strip()
    if not q or len(q) > 24:
        return []

    matches = UserAccount.query.filter(UserAccount.id.in_(
        db.session.query(WorkpacesMembers.account_id)
        .filter(WorkpacesMembers.workspace_id==w.id)
        .filter(WorkpacesMembers.account_id.in_(
            db.session.query(UserInfo.account_id).filter(
                or_(
                    UserInfo.username.ilike("%{}%".format(q)),
                    UserInfo.fullname.ilike("%{}%".format(q))
                )
            )
        )).limit(count)))

    return [m.to_short_dict() for m in matches]


def lookup_workspaces(o: Org, q: str, account_id: str,
                      count: int = 10) -> List[Dict[str, str]]:
    q = (q or "").strip()
    if not q or len(q) > 24:
        return []

    sub = db.session.query(Workspace.id)\
        .filter(Workspace.org_id==o.id)
    if o.kind == OrgType.personal and \
        (account_id and not o.is_owner(account_id)):
        sub = sub.filter(Workspace.kind==WorkspaceType.public)
    sub = sub.filter(Workspace.name.ilike("%{}%".format(q)))

    matches = WorkpacesMembers.query\
        .filter(WorkpacesMembers.workspace_id.in_(sub))\
        .distinct(WorkpacesMembers.workspace_id)\
        .limit(count)
    return [m.workspace.to_short_dict() for m in matches]


def get_workspaces(user_claim: UserClaim) -> List[_Workspace]:
    account_id = user_claim["id"]
    account = UserAccount.query.filter(UserAccount.id==account_id).first()
    workspaces = []
    for w in account.workspaces:
        workspace = w.to_dict()
        workspace["context"] = {
            "account": account_id,
            "acls": compute_workspace_acls(account_id, w.org, w)
        }
        workspaces.append(workspace)
    return workspaces


def get_workspace_by_id(user_claim: UserClaim,
                        workspace_id: str) -> Optional[_Workspace]:
    w = Workspace.get_by_id(workspace_id)
    if not w:
        return None

    account_id = user_claim["id"]
    workspace = w.to_dict()
    workspace["context"] = {
        "account": account_id,
        "acls": compute_workspace_acls(account_id, w.org, w)
    }
    return workspace


def get_workspace(user_claim: UserClaim, org_name: str,
                  workspace_name: str) -> Optional[_Workspace]:
    o = Org.find_by_name(org_name)
    if not o:
        return None

    w = o.find_workspace_by_name(workspace_name)
    if not w:
        return None

    account_id = user_claim["id"] if user_claim else None
    workspace = w.to_dict()
    workspace["context"] = {
        "account": account_id,
        "acls": compute_workspace_acls(account_id, o, w)
    }
    return workspace


def compute_workspace_acls(account_id: str, org: Org,
                           workspace: Workspace) -> List[str]:
    acls: List[str] = []

    if is_workspace_owner(account_id, org, workspace):
        acls.append("owner")

    if is_workspace_viewable(account_id, org, workspace):
        acls.append("view")

    if is_workspace_writable(account_id, org, workspace):
        acls.append("write")

    return acls


def is_workspace_viewable(account_id: Union[str, None], o: Org,
                          w: Workspace) -> bool:
    """
    Decide if a workspace of a given organization is viewable by a particular
    account.

    Here are the conditions:

    * a personal workspace in a personal organization is only viewed by its
      owner
    * a personal workspace in a public organization is only viewed by its
      owner
    * a protected workspace in a personal organization is only viewed by its
      owner
    * a protected workspace in a public organization can be viewed by the
      org members and workspace collaborators
    * a public workspace in a personal organization can be viewed by anyone
    * a public workspace in a public organization can be viewed by anyone
    """
    if not o:
        return False

    if not w:
        return False

    # public workspace => allowed
    if w.kind == WorkspaceType.public:
        return True

    if account_id:
        w_membership = WorkpacesMembers.query.filter(
            WorkpacesMembers.account_id==account_id,
            WorkpacesMembers.workspace_id==w.id).first()

        # personal workspace/not owner? => not allowed
        if w.kind == WorkspaceType.personal and \
            not (w_membership and w_membership.is_owner):
            return False

        o_membership = OrgsMembers.query.filter(
            OrgsMembers.account_id==account_id,
            OrgsMembers.org_id==o.id).first()

        if w.kind == WorkspaceType.personal:
            if o_membership and o_membership.is_owner:
                return True

    # be conservative by default
    return False


def is_workspace_writable(account_id: str, o: Org, w: Workspace) -> bool:
    if not o:
        return False

    if not w:
        return False

    assoc = WorkpacesMembers.query.filter(
        WorkpacesMembers.account_id==account_id,
        WorkpacesMembers.workspace_id==w.id).first()

    if not (assoc and assoc.is_owner):
        return False

    assoc = OrgsMembers.query.filter(
        OrgsMembers.account_id==account_id,
        OrgsMembers.org_id==o.id).first()

    if not (assoc and assoc.is_owner):
        return False

    return True


def is_workspace_owner(account_id: str, o: Org, w: Workspace) -> bool:
    if not o:
        return False

    if not w:
        return False

    assoc = WorkpacesMembers.query.filter(
        WorkpacesMembers.is_owner is True,
        WorkpacesMembers.account_id==account_id,
        WorkpacesMembers.workspace_id==w.id).first()

    return assoc is not None


def is_workspace_anonymously_viewable(o: Org, w: Workspace) -> bool:
    """
    Decide is an organization is viewable anonumously.
    """
    return w and w.kind == WorkspaceType.public


def is_org_viewable(account_id: str, o: Org) -> bool:
    """
    Decide if an organization is viewable by a particular account.

    Here are the conditions:

    * a personal organization is only viewed by its owner
    * a public organization is viewed by anyone
    """
    if not o:
        return False

    if o.kind == OrgType.collaborative:
        return True

    assoc = OrgsMembers.query.filter(
        OrgsMembers.account_id==account_id,
        OrgsMembers.org_id==o.id).first()

    if assoc and assoc.is_owner:
        return True

    # be conservative by default
    return False


def can_org_be_deleted(account_id: str, o: Org) -> bool:
    if not o:
        return False

    assoc = OrgsMembers.query.filter(
        OrgsMembers.is_owner is True,
        OrgsMembers.account_id==account_id,
        OrgsMembers.org_id==o.id).first()

    if not assoc:
        return False

    if o.kind == OrgType.personal:
        return False

    return True


def get_org_from_url(org: str, redirect_to: str) -> Org:
    """
    Load the organization object from the request's URL path info. If it
    cannot be found returns a 404.

    If the path info has the wrong case, redirects to the appropriate one.
    """
    org_name = org.strip()
    if not org_name:
        raise abort(404)

    org_name = org_name.lower()
    organization = Org.query.filter(Org.name_lower==org_name).first()

    if not organization:
        raise abort(404)

    if organization.name != org:
        # the user likely called with a different case in the url
        # we prefer to redirect to the correct url for better visibility
        url = "/{}/{}".format(organization.name, redirect_to)
        response = redirect(url.replace("//", "/").rstrip("/"), code=308)
        raise abort(response)

    return organization


def load_org(redirect_to: str, allow_anonymous: bool = False):
    def wrapper(f):
        @wraps(f)
        def inner(*args, **kwargs) -> Any:
            # necessary to access the argument above
            nonlocal redirect_to, allow_anonymous

            user_claim = kwargs.get("user_claim")
            account_id = None
            if user_claim is not None:
                account_id = user_claim["id"]

            org = kwargs.get("org")
            if not org:
                return abort(404)

            redirect_args_filler = {k: "" for k in kwargs}
            redirect_args_filler.pop("user_claim", None)
            redirect_to_url = url_for(redirect_to, **redirect_args_filler)
            o = get_org_from_url(org, redirect_to=redirect_to_url)

            if account_id and not is_org_viewable(account_id, o):
                raise abort(404)
            elif not account_id and not allow_anonymous:
                raise abort(404)

            kwargs["org"] = o
            return f(*args, **kwargs)
        return inner
    return wrapper


def get_workspace_from_url(org: Org, workspace: str,
                           redirect_to: str) -> Workspace:
    """
    Load the workspace object from the request's URL path info. If it
    cannot be found returns a 404.

    If the path info has the wrong case, redirects to the appropriate one.
    """
    workspace_name = workspace.strip()
    if not workspace_name:
        raise abort(404)

    workspace_name = workspace_name.lower()
    w = Workspace.query.filter(
        Workspace.org_id==org.id,
        Workspace.name_lower==workspace_name).first()

    if not w:
        raise abort(404)

    if w.name != workspace:
        # the user likely called with a different case in the url
        # we prefer to redirect to the correct url for better visibility
        url = "/{}/{}/{}".format(org.name, w.name, redirect_to)
        raise abort(redirect(url.replace("//", "/")))

    return w


def load_org_and_workspace(redirect_to: str, allow_anonymous: bool = False):
    def wrapper(f):
        @wraps(f)
        def inner(*args, **kwargs):
            nonlocal redirect_to

            org = kwargs.get("org")
            if not org:
                return abort(404)

            user_claim = kwargs.get("user_claim")
            account_id = None
            if user_claim is not None:
                account_id = user_claim["id"]

            redirect_args_filler = {k: "" for k in kwargs}
            redirect_args_filler.pop("user_claim", None)
            redirect_to_url = url_for(redirect_to, **redirect_args_filler)
            o = get_org_from_url(org, redirect_to=redirect_to_url)

            workspace = kwargs.get("workspace")
            if not workspace:
                return abort(404)

            redirect_args_filler = {k: "" for k in kwargs}
            redirect_args_filler.pop("user_claim", None)
            redirect_to_url = url_for(redirect_to, **redirect_args_filler)
            w = get_workspace_from_url(
                org=o, workspace=workspace, redirect_to=redirect_to_url)

            if account_id and not is_workspace_viewable(account_id, o, w):
                raise abort(404)
            elif allow_anonymous and not account_id and \
                not is_workspace_anonymously_viewable(o, w):
                raise abort(404)
            elif not account_id and not allow_anonymous:
                raise abort(404)

            kwargs["org"] = o
            kwargs["workspace"] = w

            return f(*args, **kwargs)
        return inner
    return wrapper


def record_activity(activity: Dict[str, Any]) -> Activity:
    """
    Record an activity
    """
    act = Activity.from_dict(activity)
    db.session.add(act)
    db.session.commit()

    return act


def get_caller_org_activities(org: Org, caller: Dict[str, Any]) \
                              -> List[Dict[str, Any]]:
    org_owner = caller.get("org_owner") if caller else False
    org_member = caller.get("org_member") if caller else False

    if not caller:
        visibility = ActivityVisibility.anonymous
    elif org_owner:
        visibility = ActivityVisibility.owner
    elif org_member:
        visibility = ActivityVisibility.collaborator
    else:
        visibility = ActivityVisibility.authenticated

    activities = Activity.get_recents_for_org(org.id, visibility)
    result = []
    for activity in activities:
        d = activity.to_dict()
        if org:
            d["org"] = {
                "name": org.name
            }

        if activity.workspace_id:
            w = Workspace.get_by_id(activity.workspace_id)
            if w:
                d["workspace"] = {
                    "name": w.name
                }
        result.append(d)

    return result


def get_caller_workspace_activities(workspace: Workspace,
                                    caller: Dict[str, Any]) \
                                    -> List[Dict[str, Any]]:
    org_owner = caller.get("org_owner") if caller else False
    org_member = caller.get("org_member") if caller else False
    workspace_owner = caller.get("workspace_owner") if caller else False
    workspace_collaborator = caller.get("workspace_collaborator") if caller \
        else False

    if not caller:
        visibility = ActivityVisibility.anonymous
    elif workspace_owner or org_owner:
        visibility = ActivityVisibility.owner
    elif workspace_collaborator or org_member:
        visibility = ActivityVisibility.collaborator
    else:
        visibility = ActivityVisibility.authenticated

    activities = Activity.get_recents_for_workspace(workspace.id, visibility)
    result = []
    for activity in activities:
        d = activity.to_dict()
        if workspace:
            d["org"] = {
                "name": workspace.org.name
            }

            d["workspace"] = {
                "name": workspace.name
            }
        result.append(d)

    return result


def get_account_activities(account_id: str,
                           caller: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not caller:
        visibility = ActivityVisibility.anonymous
    else:
        visibility = ActivityVisibility.owner

    activities = Activity.get_recents_for_account(account_id, visibility)
    result = []
    for activity in activities:
        d = activity.to_dict()

        if activity.org_id:
            org = Org.get_by_id(activity.org_id)
            if org:
                d["org"] = {
                    "name": org.name if org else None
                }

        if activity.org_id:
            workspace = Workspace.get_by_id(activity.workspace_id)
            if workspace:
                d["workspace"] = {
                    "name": workspace.name if workspace else None
                }

        result.append(d)

    return result
