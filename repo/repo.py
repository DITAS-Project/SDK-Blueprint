import git
import os
import shutil

TMP_DIR = 'tmp'


def clone_repo(https_url, git_url):
    # Extract the name of the repository from URL
    repo_name = os.path.basename(os.path.normpath(https_url))
    # Create a subfolder in TMP_DIR with the name of the repo
    repo_path = os.path.join(os.getcwd(), TMP_DIR, repo_name)
    # If the subfolder already exists, delete it
    if os.path.exists(repo_path) and os.path.isdir(repo_path):
        shutil.rmtree(repo_path)

    # Initialize local repo folder
    empty_repo = git.Repo.init(path=repo_path, mkdir=True)

    # origin = empty_repo.create_remote('origin', https_url)
    origin = empty_repo.create_remote('origin', https_url)
    assert origin.exists()
    assert origin == empty_repo.remotes.origin == empty_repo.remotes['origin']

    # Download repo meta-data from remote
    origin.fetch()
    # Setup a local tracking branch of a remote branch
    empty_repo.create_head('master', origin.refs.master)  # create local branch "master" from remote "master"
    empty_repo.heads.master.set_tracking_branch(origin.refs.master)  # set local "master" to track remote "master
    empty_repo.heads.master.checkout()  # checkout local "master" to working tree

    # Pull repository
    origin.pull()
