import json
import os


TEMPLATE_PATH = 'blueprint_template.json'
VDC_CONFIG = 'bp_gen_vdc.cfg'
BLUEPRINT_NAME = 'blueprint.json'

INTERNAL_STRUCTURE_SECTION = 'INTERNAL_STRUCTURE'
IS_OVERVIEW = "Overview"
IS_OW_TAGS = "tags"
IS_OW_TAGS_METHODID = "method_id"
DATA_MANAGEMENT_SECTION = 'DATA_MANAGEMENT'
ABSTRACT_PROPERTIES_SECTION = 'ABSTRACT_PROPERTIES'
COOKBOOK_APPENDIX_SECTION = 'COOKBOOK_APPENDIX'
EXPOSED_API_SECTION = 'EXPOSED_API'

SWAGGER_PATHS = 'paths'


class Blueprint:
    def __init__(self, vdc_repo_path):
        self.vdc_repo_path = vdc_repo_path

        # loading template
        with open(TEMPLATE_PATH) as template:
            self.bp = json.load(template)

        # loading vdc_config_file
        with open(self.__get_vdc_path(VDC_CONFIG)) as vdc_config:
            self.vdc_config_file = json.load(vdc_config)

    def add_exposed_api(self):
        with open(self.__get_vdc_path(self.vdc_config_file['swagger'])) as swagger_file:
            self.bp[EXPOSED_API_SECTION] = json.load(swagger_file)

    def add_is_tags(self):
        with open(self.__get_vdc_path(self.vdc_config_file['swagger'])) as swagger_file:
            swagger = json.load(swagger_file)
        tag_template = self.bp[INTERNAL_STRUCTURE_SECTION][IS_OVERVIEW][IS_OW_TAGS][0]
        tags = []
        for method in swagger[SWAGGER_PATHS].keys():
            tag_template[IS_OW_TAGS_METHODID] = method.replace('/', '')
            tags.append(tag_template)
        self.bp[INTERNAL_STRUCTURE_SECTION][IS_OVERVIEW][IS_OW_TAGS] = tags

    def save(self):
        with open(self.__get_vdc_path(BLUEPRINT_NAME), 'w') as outfile:
            json.dump(self.bp, outfile, indent=4)

    def __get_vdc_path(self, filepath):
        return os.path.join(self.vdc_repo_path, filepath)