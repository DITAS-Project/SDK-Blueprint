import git


# Clone repository at https_url into path folder
def clone_repo(https_url, path):

    # Initialize local repo folder
    empty_repo = git.Repo.init(path=path, mkdir=True)

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
