from blueprint.config_file.configfile import ConfigFile

# const referred to DAL config file
MAIN_PROTO = 'main_proto'


class DALConfigFile(ConfigFile):
    def __init__(self, repo_path, file_conf_path):
        super().__init__(repo_path, file_conf_path)

    def get_path_from_main_proto(self):
        return super().get_path_from_section(MAIN_PROTO)

    def get_main_proto(self):
        return super().get_section(MAIN_PROTO)

