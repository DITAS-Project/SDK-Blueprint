import json
import os
import copy
import yaml


TEMPLATE_PATH = 'blueprint_template.json'
VDC_CONFIG = 'bp_gen_vdc.cfg'
DAL_CONFIG = 'bp_gen_vdc.cfg'

# type of flows
NODERED = 'node-red'
SPARK = 'spark'

# const referred to blueprint template
INTERNAL_STRUCTURE_SECTION = 'INTERNAL_STRUCTURE'
IS_OVERVIEW = 'Overview'
IS_OW_TAGS = 'tags'
IS_OW_TAGS_METHODID = 'method_id'
IS_FLOW = 'Flow'
IS_FLOW_PLATFORM = 'platform'
IS_FLOW_PARAMS = 'parameters'
IS_FLOW_SOURCE = 'source'
DATA_MANAGEMENT_SECTION = 'DATA_MANAGEMENT'
ABSTRACT_PROPERTIES_SECTION = 'ABSTRACT_PROPERTIES'
COOKBOOK_APPENDIX_SECTION = 'COOKBOOK_APPENDIX'
EXPOSED_API_SECTION = 'EXPOSED_API'

# const referred to config files
BLUEPRINT = 'blueprint'
FLOW = 'flow'
FLOW_PLATFORM = 'platform'
FLOW_PATH = 'source'
SWAGGER = 'swagger'

# const referred to the swagger file
SWAGGER_PATHS = 'paths'


class Blueprint:
    def __init__(self, vdc_repo_path, dal_repo_paths, update=False):
        ''' 
        loading template and blueprint:
        -   template remains constant
        -   bp will be modified during the execution        
        '''
        self.bp = get_dict_from_file(TEMPLATE_PATH)
        self.template = copy.deepcopy(self.bp)

        # loading vdc_config_file
        self.vdc_config = ConfigFile(vdc_repo_path, VDC_CONFIG)

        # loading dal_config_file
        #self.dal_configs = []
        #for path in dal_repo_paths:
        #    self.dal_configs.append(ConfigFile(path, DAL_CONFIG))

        # if method update the bp file is loaded from the configuration file
        if update:
            self.bp = get_dict_from_file(self.__get_vdc_path(self.vdc_config_file[BLUEPRINT]))

    def add_exposed_api(self):
        self.bp[EXPOSED_API_SECTION] = get_dict_from_file(self.vdc_config.get_path_from_section(SWAGGER))

    def add_is_tags(self):
        swagger = get_dict_from_file(self.vdc_config.get_path_from_section(SWAGGER))
        tags = []
        for method in swagger[SWAGGER_PATHS].keys():
            tag_template = copy.deepcopy(self.template[INTERNAL_STRUCTURE_SECTION][IS_OVERVIEW][IS_OW_TAGS][0])
            tag_template[IS_OW_TAGS_METHODID] = method.replace('/', '')
            tags.append(tag_template)
        self.bp[INTERNAL_STRUCTURE_SECTION][IS_OVERVIEW][IS_OW_TAGS] = tags

    def add_is_flow(self):
        if self.vdc_config.get_nested_section(FLOW, FLOW_PLATFORM).lower() == NODERED:
            flow = {
                IS_FLOW_PLATFORM: self.vdc_config.get_nested_section(FLOW, FLOW_PLATFORM),
                IS_FLOW_SOURCE: get_dict_from_file(self.vdc_config.get_path_from_nested_section(FLOW, FLOW_PATH))
            }
            self.bp[INTERNAL_STRUCTURE_SECTION][IS_FLOW] = flow
        elif self.vdc_config.get_nested_section(FLOW, FLOW_PLATFORM).lower() == SPARK:
            flow = {
                IS_FLOW_PLATFORM: self.vdc_config.get_nested_section(FLOW, FLOW_PLATFORM),
                IS_FLOW_PARAMS: ''
            }
            self.bp[INTERNAL_STRUCTURE_SECTION][IS_FLOW] = flow

    def save(self):
        with open(self.vdc_config.get_path_from_section(BLUEPRINT), 'w') as outfile:
            json.dump(self.bp, outfile, indent=4)


class ConfigFile:
    def __init__(self, repo_path, file_conf_path):
        self.repo_path = repo_path
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


JSON_EXTENSION = '.json'
YAML_EXTENSION = '.yaml'


def get_dict_from_file(path):
    if JSON_EXTENSION in path.lower():
        with open(path) as file:
            return json.load(file)
    elif YAML_EXTENSION in path.lower():
        with open(path) as file:
            return yaml.safe_load(file)
    else:
        print('Format file not recognized. Use .json or .yaml for ' + path)
