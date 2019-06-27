import json
import os
import copy


TEMPLATE_PATH = 'blueprint_template.json'
VDC_CONFIG = 'bp_gen_vdc.cfg'

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
    def __init__(self, vdc_repo_path, update=False):
        self.vdc_repo_path = vdc_repo_path
        ''' 
        loading template and blueprint:
        -   template remains constant
        -   bp will be modified during the execution        
        '''
        with open(TEMPLATE_PATH) as template:
            self.bp = json.load(template)
            self.template = copy.deepcopy(self.bp)

        # loading vdc_config_file
        with open(self.__get_vdc_path(VDC_CONFIG)) as vdc_config:
            self.vdc_config_file = json.load(vdc_config)

        # if method update the bp file is loaded from the configuration file
        if update:
            with open(self.__get_vdc_path(self.vdc_config_file[BLUEPRINT])) as bp_file:
                self.bp = json.load(bp_file)

    def add_exposed_api(self):
        with open(self.__get_vdc_path(self.vdc_config_file[SWAGGER])) as swagger_file:
            self.bp[EXPOSED_API_SECTION] = json.load(swagger_file)

    def add_is_tags(self):
        with open(self.__get_vdc_path(self.vdc_config_file[SWAGGER])) as swagger_file:
            swagger = json.load(swagger_file)
        tags = []
        for method in swagger[SWAGGER_PATHS].keys():
            tag_template = copy.deepcopy(self.template[INTERNAL_STRUCTURE_SECTION][IS_OVERVIEW][IS_OW_TAGS][0])
            tag_template[IS_OW_TAGS_METHODID] = method.replace('/', '')
            tags.append(tag_template)
        self.bp[INTERNAL_STRUCTURE_SECTION][IS_OVERVIEW][IS_OW_TAGS] = tags

    def add_is_flow(self):
        if self.vdc_config_file[FLOW][FLOW_PLATFORM].lower() == NODERED:
            with open(self.__get_vdc_path(self.vdc_config_file[FLOW][FLOW_PATH])) as flow_source:
                flow = {
                    IS_FLOW_PLATFORM: self.vdc_config_file[FLOW][FLOW_PLATFORM],
                    IS_FLOW_SOURCE: json.load(flow_source)
                }
                self.bp[INTERNAL_STRUCTURE_SECTION][IS_FLOW] = flow
        elif self.vdc_config_file[FLOW][FLOW_PLATFORM].lower() == SPARK:
            flow = {
                IS_FLOW_PLATFORM: self.vdc_config_file[FLOW][FLOW_PLATFORM],
                IS_FLOW_PARAMS: ''  # TODO da modificare, al momento non so cosa inserire
            }
            self.bp[INTERNAL_STRUCTURE_SECTION][IS_FLOW] = flow
        else:
            print('Flow platform not recognized!')  # TODO forse qua bisogna lanciare una eccezione

    def save(self):
        with open(self.__get_vdc_path(self.vdc_config_file[BLUEPRINT]), 'w') as outfile:
            json.dump(self.bp, outfile, indent=4)

    def __get_vdc_path(self, filepath):
        return os.path.join(self.vdc_repo_path, filepath)
