import argparse
import os
import shutil
from repo import repo

'''
due_vdc_url = 'https://github.com/DITAS-Project/DUE-VDC'
git_url = 'git@github.com:DITAS-Project/DUE-VDC.git'

repo.clone_repo(due_vdc_url, git_url)
'''

TMP_DIR = 'tmp'


def extract_info_from_vdc(path):
    # Do something
    print("Doing some processing on VDC local repo...")


def extract_info_from_dal(path):
    # Do something
    print("Doing some processing on DAL local repo...")


def prepare_repo_folder(url):
    # Extract the name of the repository from URL
    repo_name = os.path.basename(os.path.normpath(url))

    # Create a subfolder in TMP_DIR with the name of the repo
    repo_path = os.path.join(os.getcwd(), TMP_DIR, repo_name)

    # If the subfolder already exists, delete it
    if os.path.exists(repo_path) and os.path.isdir(repo_path):
        shutil.rmtree(repo_path)

    return repo_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='''SDK-Blueprint generator CLI.''')

    parser.add_argument('VDC_URL', type=str, help='VDC repository URL')
    parser.add_argument('DAL_URL', type=str, nargs='*', help='List of DAL repositories URLs. '
                                                             'Assumed same URL as VDC repository if not provided')
    parser.add_argument('-e', type=str, default='bla', help='Use this option to automatically set two URLs as example')

    args = parser.parse_args()

    vdc_url = args.VDC_URL
    dal_urls = args.DAL_URL

    # Feeling lazy, just put two URLs at random to test
    if args.e:
        vdc_url = 'https://github.com/DITAS-Project/DUE-VDC'
        dal_urls = ['https://github.com/DITAS-Project/SDK-Blueprint']

    # Clone VDC repo and extract info to generate Blueprint
    vdc_repo_path = prepare_repo_folder(vdc_url)
    repo.clone_repo(vdc_url, vdc_repo_path)
    extract_info_from_vdc(vdc_repo_path)

    # If DAL URLs list is empty, then just extract DAL info from already cloned VDC repo
    if not dal_urls:
        extract_info_from_dal(vdc_repo_path)
    else:
        # Clone each DAL repo and merge information to blueprint
        for dal_url in dal_urls:
            dal_repo_path = prepare_repo_folder(dal_url)
            repo.clone_repo(dal_url, dal_repo_path)
            extract_info_from_dal(dal_repo_path)