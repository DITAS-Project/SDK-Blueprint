import json
import os
import copy
import yaml
from blueprint.configfile import ConfigFile


TEMPLATE_PATH = 'blueprint_template.json'
VDC_SECTION = 'VDC'
DAL_SECTION = 'DAL'
VDC_CONFIG = 'bp_gen_vdc.cfg'
DAL_CONFIG = 'bp_gen_dal.cfg'

ZIP_FORMAT = '.zip'

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
IS_TESTING_OUTPUT_DATA = 'Testing_Output_Data'
IS_TOD_METHODID = 'method_id'
IS_TOD_ZIP = 'zip_data'
DATA_MANAGEMENT_SECTION = 'DATA_MANAGEMENT'
ABSTRACT_PROPERTIES_SECTION = 'ABSTRACT_PROPERTIES'
COOKBOOK_APPENDIX_SECTION = 'COOKBOOK_APPENDIX'
EXPOSED_API_SECTION = 'EXPOSED_API'

# const referred to config files
BLUEPRINT = 'blueprint'
FLOW = 'flow'
FLOW_PLATFORM = 'platform'
FLOW_PATH = 'source'
COOKBOOK = 'cookbook'
ZIP_DIR = 'zip_directory'
API = 'api'

# const referred to the api file
API_PATHS = 'paths'


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
        self.dal_configs = []
        for path in dal_repo_paths:
            self.dal_configs.append(ConfigFile(path, DAL_CONFIG))

        # if method update the bp file is loaded from the configuration file
        if update:
            self.bp = get_dict_from_file(self.__get_vdc_path(self.vdc_config_file[BLUEPRINT]))

    def add_exposed_api(self):
        self.bp[EXPOSED_API_SECTION] = get_dict_from_file(self.vdc_config.get_path_from_section(API))

    def add_is_tags(self):
        api = get_dict_from_file(self.vdc_config.get_path_from_section(API))
        tags = []
        for method in api[API_PATHS].keys():
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

    def add_cookbook(self):
        cookbook = {
            VDC_SECTION: {},
            DAL_SECTION: {}
        }
        with open(self.vdc_config.get_path_from_section(COOKBOOK), 'r') as vdc_cookbook:
            cookbook[VDC_SECTION][self.vdc_config.repo_name] = vdc_cookbook.read()
        for dal_config in self.dal_configs:
            with open(dal_config.get_path_from_section(COOKBOOK), 'r') as dal_cookbook:
                cookbook[DAL_SECTION][dal_config.repo_name] = dal_cookbook.read()
        self.bp[COOKBOOK_APPENDIX_SECTION] = cookbook

    def add_is_testing_output_data(self):
        api = get_dict_from_file(self.vdc_config.get_path_from_section(API))
        outdata = []
        for method in api[API_PATHS].keys():
            outdata_template = copy.deepcopy(self.template[INTERNAL_STRUCTURE_SECTION][IS_TESTING_OUTPUT_DATA][0])
            method = method.replace('/', '')
            outdata_template[IS_TOD_METHODID] = method
            zip_file = os.path.join(self.vdc_config.get_path_from_section(ZIP_DIR), method + ZIP_FORMAT)
            if os.path.exists(zip_file):
                outdata_template[IS_TOD_ZIP] = os.path.join(self.vdc_config.get_section(ZIP_DIR), method + ZIP_FORMAT)
            else:
                outdata_template[IS_TOD_ZIP] = 'File not found'
            outdata.append(outdata_template)
        self.bp[INTERNAL_STRUCTURE_SECTION][IS_TESTING_OUTPUT_DATA] = outdata

    def save(self):
        with open(self.vdc_config.get_path_from_section(BLUEPRINT), 'w') as outfile:
            json.dump(self.bp, outfile, indent=4)


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
