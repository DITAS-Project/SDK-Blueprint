import git
import json
import os
import requests

GH_ACCESS_FILE='github_access.json'
GH_ORG_DITAS = 'DITAS-Project'


# Clone repository at https_url into path folder
def clone_repo(https_url, path, new_repo=False):

    # Initialize local repo folder
    empty_repo = git.Repo.init(path=path, mkdir=True)

    origin = empty_repo.create_remote('origin', https_url)
    assert origin.exists()
    assert origin == empty_repo.remotes.origin == empty_repo.remotes['origin']

    # Download repo meta-data from remote
    origin.fetch()
    # Setup a local tracking branch of a remote branch
    if not new_repo:
        empty_repo.create_head('master', origin.refs.master)  # create local branch "master" from remote "master"
        empty_repo.heads.master.set_tracking_branch(origin.refs.master)  # set local "master" to track remote "master
        empty_repo.heads.master.checkout()  # checkout local "master" to working tree

        # Pull repository
        origin.pull()

    return empty_repo


def commit_and_push_all_changes(repo):
    repo.git.add(A=True)
    repo.index.commit('VDC template commit')
    repo.git.execute(["git", "push", "-u", "origin", "master"])

def load_gh_access_token():
    gh_access_file_path = os.path.join(os.getcwd(), GH_ACCESS_FILE)
    with open(gh_access_file_path) as gh_access_file:
        access_token = json.load(gh_access_file)['access_token']
    return access_token


def create_personal_repo(repo_name):
    access_token=load_gh_access_token()
    headers = {'Authorization': 'token ' + access_token}
    url = 'https://api.github.com/user/repos'
    body = {
        "name": repo_name,
        "private": False,
    }
    response = requests.post(url, json=body, headers=headers)
    return response.json()


def create_ditas_repo(repo_name):
    access_token = load_gh_access_token()
    headers = {'Authorization': 'token ' + access_token}
    url = 'https://api.github.com/orgs/' + GH_ORG_DITAS + '/repos'
    body = {
        "name": repo_name,
        "private": False,
    }
    response = requests.post(url, json=body, headers=headers)
    return response.json()
