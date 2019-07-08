import argparse
import os
import shutil
from repo import repo
from blueprint.blueprint import Blueprint
from distutils.dir_util import copy_tree



'''
due_vdc_url = 'https://github.com/DITAS-Project/DUE-VDC'
git_url = 'git@github.com:DITAS-Project/DUE-VDC.git'

repo.clone_repo(due_vdc_url, git_url)
'''

TMP_DIR = 'tmp'
VDC_TEMPLATE = 'vdc_template'

def generate_blueprint(vdc_path, dal_paths, update):
    # Do something
    print("Creating blueprint...")
    blueprint = Blueprint(vdc_path, dal_paths, update)
    blueprint.add_is_tags()
    blueprint.add_is_flow()
    blueprint.add_is_testing_output_data()
    blueprint.add_cookbook()
    blueprint.add_exposed_api()
    blueprint.add_is_data_sources()
    blueprint.save()


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


def handler_create(args):
    vdc_url = args.VDC_URL
    dal_urls = args.DAL_URL

    # Feeling lazy, just put two URLs at random to test
    #if args.e:
    #    vdc_url = 'git@github.com:caloc/ideko-copy.git'
    #    dal_urls = ['git@github.com:caloc/ideko-copy.git']

    # Clone VDC repo and extract info to generate Blueprint
    repo_name = extract_repo_name(vdc_url)
    vdc_repo_path = prepare_repo_folder(repo_name)
    repo.clone_repo(vdc_url, vdc_repo_path)

    # If DAL URLs list is empty, then just extract DAL info from already cloned VDC repo
    dal_repo_paths = []
    if not dal_urls:
        dal_repo_paths.append(vdc_repo_path)
    else:
        # Clone each DAL repo and merge information to blueprint
        # TODO: if the DAL URL is the same as VDC, prepare_repo_folder could cause some troubles
        # TODO: create a subversion of the repo folder
        for dal_url in dal_urls:
            dal_repo_path = prepare_repo_folder(dal_url)
            repo.clone_repo(dal_url, dal_repo_path)
            dal_repo_paths.append(dal_repo_path)

    generate_blueprint(vdc_repo_path, dal_repo_paths, False)

    '''
    TODO al momento tutte le info richieste stanno all'interno del vdc file, quando sapremo cosa fare anche per i dal
    dovrà essere cambiata la definizione della classe blueprint e parte di questi metodi
    Dal mio punto di vista non credo sia corretto fare extract info from... dalle diverse DAL, penso in realtà che sia
    più corretto completare i campi che devono essere completati usando tutti i dal assieme nella classe blueprint, in 
    questo modo sarà più semplice appendere i creare i campi del dizionario 
    '''


def handler_update(args):
    print("Handler of update subcommand")


def handler_repo_init(args):
    if args.name:
        repo_name = args.name

        # This will create a repo in the org DITAS-Project. DO NOT SPAM
        #resp = repo.create_ditas_repo(repo_name)
        # TODO: delete next line when testing is complete and uncomment the previous one
        resp = repo.create_personal_repo(repo_name)
        print(resp['html_url'])
        repo_url = resp['html_url']


        # Setup a local folder to track the remote repository
        repo_path = prepare_repo_folder(repo_name)
        remote_repo = repo.clone_repo(https_url=repo_url, path=repo_path, new_repo=True)

        # Use the default VDC template for the new repository
        from_directory = os.path.join(os.getcwd(), VDC_TEMPLATE)
        copy_tree(from_directory, repo_path)

        # Commit and push the new structure
        repo.commit_and_push_all_changes(remote_repo)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='''DITAS SDK-Blueprint Generator.''')

    parser.add_argument('-u', action='store_true', required=False, help='Update an existing blueprint with info '
                                                                        'contained in the config files of the repos.')

    subparsers = parser.add_subparsers(help='Sub-command to create or update a blueprint, or to setup a new repository')

    # Create the parser for the "create" command
    parser_create = subparsers.add_parser('create', help='Generate a new blueprint. An already existing blueprint '
                                                         'is overwritten.')
    parser_create.add_argument('VDC_URL', type=str, help='VDC repository URL')
    parser_create.add_argument('DAL_URL', type=str, nargs='*', help='List of DAL repositories URLs. Assumed same URL '
                                                                    'as VDC repository if not provided')
    #parser_create.add_argument('-e', type=str, default='bla', help='Use this option to automatically set two URLs as '
    #                                                               'example')
    parser_create.set_defaults(func=handler_create)

    # Create the parser for the "update" command
    parser_update = subparsers.add_parser('update', help='Update an existing blueprint. Only the parts specified in the'
                                                         'configuration files of the repositories will overwritten.')
    parser_update.add_argument('VDC_URL', type=str, help='VDC repository URL')
    parser_update.add_argument('DAL_URL', type=str, nargs='*', help='List of DAL repositories URLs. Assumed same URL '
                                                                    'as VDC repository if not provided')
    parser_update.set_defaults(func=handler_update)

    # Create the parser for the "repo-init" command
    parser_repo_init = subparsers.add_parser('repo-init', help='Create a new GitHub repository with the default '
                                                               'structure.')
    parser_repo_init.add_argument('name', type=str, help='Repository name')
    parser_repo_init.set_defaults(func=handler_repo_init)

    args = parser.parse_args()
    args.func(args)

    #print(args)
