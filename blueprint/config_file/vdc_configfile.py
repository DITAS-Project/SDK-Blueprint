from blueprint.config_file.configfile import ConfigFile

# const referred to VDC config file
BLUEPRINT = 'blueprint'
FLOW = 'flow'
FLOW_PLATFORM = 'platform'
FLOW_PATH = 'source'
ZIP_DIR = 'zip_directory'
API = 'api'


class VDCConfigFile(ConfigFile):
    def __init__(self, repo_path, file_conf_path):
        super().__init__(repo_path, file_conf_path)

    def get_zip_path(self):
        return super().get_path_from_section(ZIP_DIR)

    def get_zip(self):
        return super().get_section(ZIP_DIR)

    def get_api_path(self):
        return super().get_path_from_section(API)

    def get_blueprint_path(self):
        return super().get_path_from_section(BLUEPRINT)

    def get_flow_platform(self):
        return self.config_file[FLOW][FLOW_PLATFORM]

    def get_flow_source_path(self):
        return super().get_path(self.config_file[FLOW][FLOW_PATH])