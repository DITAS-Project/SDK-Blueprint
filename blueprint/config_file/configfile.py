import os
import json
import ntpath
from abc import ABC

# const referred to all config files
COOKBOOK = 'cookbook'


class ConfigFile(ABC):
    def __init__(self, repo_path, file_conf_path):
        self.repo_path = repo_path
        self.repo_name = ntpath.basename(self.repo_path)
        with open(self.get_path(file_conf_path, None)) as config:
            self.config_file = json.load(config)

    def get_path(self, filepath, section):
        if filepath == '':
            raise MissingReferenceException(section)
        return os.path.join(self.repo_path, filepath)

    def get_section(self, section):
        return self.config_file[section]

    def get_path_from_section(self, section):
        return self.get_path(self.get_section(section), section)

    def get_cookbook_path(self):
        return self.get_path(self.get_section(COOKBOOK), COOKBOOK)


class MissingReferenceException(Exception):
    def __init__(self, section):
        self.section = section

    def print(self, config_file):
        print('Missing ' + self.section + ' path in file ' + config_file)


