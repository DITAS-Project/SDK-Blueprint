import argparse
import os
import shutil
from repo import repo
from blueprint.blueprint import Blueprint
from blueprint import blueprint as bp
from distutils.dir_util import copy_tree

__author__ = "Cataldo Calò, Mirco Manzoni"
__credits__ = ["Cataldo Calò", "Mirco Manzoni"]
__status__ = "Development"


'''
due_vdc_url = 'https://github.com/DITAS-Project/DUE-VDC'
git_url = 'git@github.com:DITAS-Project/DUE-VDC.git'

repo.clone_repo(due_vdc_url, git_url)
'''

TMP_DIR = 'tmp'
VDC_TEMPLATE = 'vdc_template'
DAL_TEMPLATE = 'dal_template'
VDC = 'VDC'
DAL = 'DAL'
VDC_TEMPLATE_COMMIT = 'VDC template commit'
DAL_TEMPLATE_COMMIT = 'DAL template commit'
BLUEPRINT_COMMIT = 'Blueprint commit'


def generate_blueprint(vdc_repo, vdc_path, dal_paths, update, push):
    # Do something
    print('Creating blueprint...')
    blueprint = Blueprint(vdc_path, dal_paths, update)
    blueprint.add_is_tags()
    blueprint.add_is_flow()
    blueprint.add_is_testing_output_data()
    blueprint.add_cookbook()
    blueprint.add_exposed_api()
    blueprint.add_is_data_sources()
    blueprint.add_data_management()
    blueprint.save()
    print('Blueprint created')
    if push:
        print('Pushing blueprint into VDC repository...')
        repo.commit_and_push_all_changes(vdc_repo, BLUEPRINT_COMMIT)
        print('Push complete')


def extract_repo_name(url):
    # Extract the name of the repository from URL
    return os.path.basename(os.path.normpath(url))


def prepare_repo_folder(repo_name):
    # Create a subfolder in TMP_DIR with the name of the repo
    repo_path = os.path.join(os.getcwd(), TMP_DIR, repo_name)

    # If the subfolder already exists, delete it
    if os.path.exists(repo_path) and os.path.isdir(repo_path):
        shutil.rmtree(repo_path)

    return repo_path


def clone_repos(vdc_url, dal_urls):
    print('Cloning VDC repository at ' + vdc_url + '...')
    # Clone VDC repo and extract info to generate Blueprint
    repo_name = extract_repo_name(vdc_url)
    vdc_repo_path = prepare_repo_folder(repo_name)
    vdc_repo = repo.clone_repo(vdc_url, vdc_repo_path)

    # If DAL URLs list is empty, then just extract DAL info from already cloned VDC repo
    dal_repo_paths = []
    if not dal_urls:
        dal_repo_paths.append(vdc_repo_path)
    else:
        # Clone each DAL repo and merge information to blueprint
        # TODO: if the DAL URL is the same as VDC, prepare_repo_folder could cause some troubles
        # TODO: create a subversion of the repo folder or just skip this step
        for dal_url in dal_urls:
            print('Cloning DAL repository at ' + dal_url + '...')
            repo_name = extract_repo_name(dal_url)
            dal_repo_path = prepare_repo_folder(repo_name)
            repo.clone_repo(dal_url, dal_repo_path)
            dal_repo_paths.append(dal_repo_path)

    return vdc_repo, vdc_repo_path, dal_repo_paths


def handler_create(args):
    vdc_repo, vdc_repo_path, dal_repo_paths = clone_repos(args.VDC_URL, args.DAL_URL)
    generate_blueprint(vdc_repo, vdc_repo_path, dal_repo_paths, False, args.push)


def handler_update(args):
    vdc_repo, vdc_repo_path, dal_repo_paths = clone_repos(args.VDC_URL, args.DAL_URL)
    generate_blueprint(vdc_repo, vdc_repo_path, dal_repo_paths, True, args.push)


def handler_repo_init(args):
    if args.name:
        repo_name = args.name

        # This will create a repo in the org DITAS-Project. DO NOT SPAM
        resp = repo.create_ditas_repo(repo_name)
        # TODO: delete next line when testing is complete and uncomment the previous one
        #resp = repo.create_personal_repo(repo_name)
        print(resp['html_url'])
        repo_url = resp['html_url']


        # Setup a local folder to track the remote repository
        repo_path = prepare_repo_folder(repo_name)
        remote_repo = repo.clone_repo(https_url=repo_url, path=repo_path, new_repo=True)

        # Use the default VDC template for the new repository
        if args.type == VDC:
            from_directory = os.path.join(os.getcwd(), VDC_TEMPLATE)
            commit_msg = VDC_TEMPLATE_COMMIT
        elif args.type == DAL:
            from_directory = os.path.join(os.getcwd(), DAL_TEMPLATE)
            commit_msg = DAL_TEMPLATE_COMMIT
        copy_tree(from_directory, repo_path)

        # Commit and push the new structure
        repo.commit_and_push_all_changes(remote_repo, commit_msg)


def handler_std_metrics(args):
    if not args.local:
        vdc_repo, vdc_repo_path, dal_repo_paths = clone_repos(args.VDC, args.VDC)
    else:
        vdc_repo_path = os.path.join(os.getcwd(), TMP_DIR, args.VDC)

    bp.generate_api_metrics_files(vdc_repo_path)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='''DITAS SDK-Blueprint Generator.''')

    subparsers = parser.add_subparsers(help='Sub-command to create or update a blueprint, or to setup a new repository')

    # Create the parser for the "create" command
    parser_create = subparsers.add_parser('create', help='Generate a new blueprint. An already existing blueprint '
                                                         'is overwritten.')
    parser_create.add_argument('VDC_URL', type=str, help='VDC repository URL')
    parser_create.add_argument('DAL_URL', type=str, nargs='*', help='List of DAL repositories URLs. Assumed same URL '
                                                                    'as VDC repository if not provided')
    parser_create.add_argument('-p', dest='push', action='store_true', required=False, help='Push new generated blueprint'
                                                                                            ' into VDC repository')
    #parser_create.add_argument('-e', type=str, default='bla', help='Use this option to automatically set two URLs as '
    #                                                               'example')
    parser_create.set_defaults(func=handler_create)

    # Create the parser for the "update" command
    parser_update = subparsers.add_parser('update', help='Update an existing blueprint. Only the parts specified in the '
                                                         'configuration files of the repositories will be overwritten.')
    parser_update.add_argument('VDC_URL', type=str, help='VDC repository URL')
    parser_update.add_argument('DAL_URL', type=str, nargs='*', help='List of DAL repositories URLs. Assumed same URL '
                                                                    'as VDC repository if not provided')
    parser_update.add_argument('-p', dest='push', action='store_true', required=False,
                               help='Push new generated blueprint into VDC repository')
    parser_update.set_defaults(func=handler_update)

    # Create the parser for the "repo-init" command
    parser_repo_init = subparsers.add_parser('repo-init', help='Create a new GitHub repository with the default '
                                                               'structure.')
    parser_repo_init.add_argument('type', choices=[VDC, DAL], help="Type of repository to create")
    parser_repo_init.add_argument('name', type=str, help='Repository name')
    parser_repo_init.set_defaults(func=handler_repo_init)

    # Create the parser for the "std-metrics" command
    parser_std_metrics = subparsers.add_parser('std-metrics', help='Create a json file for each API method with the '
                                                                   'default data metrics. The path is specified by '
                                                                   'the attribute "data-management" of the VDC '
                                                                   'configuration file.')
    parser_std_metrics.add_argument('VDC', type=str, help='VDC repository URL or directory name if already downloaded.')
    parser_std_metrics.add_argument('-l', dest='local', action='store_true', required=False,
                                    help='Specifies if the VDC repository has been already downloaded, i.e. the '
                                         'provided argument is the name of repository')
    parser_std_metrics.set_defaults(func=handler_std_metrics)

    args = parser.parse_args()
    args.func(args)

    #print(args)
