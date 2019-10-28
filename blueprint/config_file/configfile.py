import os
import json
import ntpath
from abc import ABC


class ConfigFile(ABC):
    def __init__(self, repo_path, file_conf_path):
        self.repo_path = repo_path
        self.repo_name = ntpath.basename(self.repo_path)
        with open(self.get_path(file_conf_path, None)) as config:
            self.config_file = json.load(config)

    def get_path(self, relative_path, section):
        if relative_path == '' or relative_path == '/':
            raise InvalidRootDirectory(section, relative_path)
        abs_path = os.path.abspath(os.path.join(self.repo_path, relative_path))
        if not os.path.isdir(abs_path) and not os.path.isfile(abs_path):
            raise MissingReferenceException(section)
        return os.path.normpath(abs_path)

    def get_section(self, section):
        return self.config_file[section]

    def get_path_from_section(self, section):
        return self.get_path(self.get_section(section), section)


class MissingReferenceException(Exception):
    def __init__(self, section):
        self.section = section

    def print(self, config_file):
        print('ERROR: Missing ' + self.section + ' path in file ' + config_file)


class InvalidRootDirectory(Exception):
    def __init__(self, attribute, illegal_path):
        self.attribute = attribute
        self.illegal_path = illegal_path

    def print(self, config_file):
        description = 'ERROR: "' + self.illegal_path + '" invalid root directory value for attribute "' + \
                      self.attribute + '" in "' + config_file + '". Use "./" instead.'
        print(description)
