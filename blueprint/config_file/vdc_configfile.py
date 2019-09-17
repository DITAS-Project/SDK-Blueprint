from blueprint.config_file.configfile import ConfigFile

# const referred to VDC config file
BLUEPRINT = 'blueprint'
DATA_MANAGEMENT = 'data-management'
FLOW = 'flow'
FLOW_PLATFORM = 'platform'
FLOW_PATH = 'source'
API = 'api'
COOKBOOK = 'cookbook'


class VDCConfigFile(ConfigFile):
    def __init__(self, repo_path, file_conf_path):
        super().__init__(repo_path, file_conf_path)

    def get_api_path(self):
        return super().get_path_from_section(API)

    def get_blueprint_path(self):
        return super().get_path_from_section(BLUEPRINT)

    def get_flow_platform(self):
        return self.config_file[FLOW][FLOW_PLATFORM]

    def get_flow_source_path(self):
        return super().get_path(self.config_file[FLOW][FLOW_PATH], FLOW + '//' + FLOW_PATH)

    def get_data_management(self):
        return super().get_section(DATA_MANAGEMENT)

    def get_data_management_path(self):
        return super().get_path_from_section(DATA_MANAGEMENT)

    def get_cookbook_path(self):
        return super().get_path(super().get_section(COOKBOOK), COOKBOOK)