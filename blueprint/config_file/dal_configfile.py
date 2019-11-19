from blueprint.config_file.configfile import ConfigFile

# const referred to DAL config file
DATA_SOURCES = 'data_sources'
MAIN_PROTO = 'main_proto'
DATA_SOURCE = 'data_source'


class DALConfigFile(ConfigFile):
    def __init__(self, repo_path, file_conf_path):
        super().__init__(repo_path, file_conf_path)

    def get_path_from_main_proto(self, index):
        return super().get_path(super().get_section(DATA_SOURCES)[index][MAIN_PROTO], MAIN_PROTO)

    def get_main_proto(self, index):
        return super().get_section(DATA_SOURCES)[index][MAIN_PROTO]

    def get_path_from_source(self, index):
        return super().get_path(super().get_section(DATA_SOURCES)[index][DATA_SOURCE], DATA_SOURCE)

    def count_sources(self):
        return len(super().get_section(DATA_SOURCES))
