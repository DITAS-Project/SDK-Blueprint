import os
import json
import ntpath


class ConfigFile:
    def __init__(self, repo_path, file_conf_path):
        self.repo_path = repo_path
        self.repo_name = ntpath.basename(self.repo_path)
        with open(self.__get_path(file_conf_path)) as config:
            self.config_file = json.load(config)

    def __get_path(self, filepath):
        return os.path.join(self.repo_path, filepath)

    def get_section(self, section):
        return self.config_file[section]

    def get_nested_section(self, upper_section, lower_section):
        return self.config_file[upper_section][lower_section]

    def get_path_from_section(self, section):
        return self.__get_path(self.get_section(section))

    def get_path_from_nested_section(self, upper_section, lower_section):
        return self.__get_path(self.get_nested_section(upper_section, lower_section))