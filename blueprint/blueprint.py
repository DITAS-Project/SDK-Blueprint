import json
import os
import copy
import yaml
import re
from blueprint.config_file.vdc_configfile import VDCConfigFile
from blueprint.config_file.dal_configfile import DALConfigFile
from blueprint.config_file.configfile import MissingReferenceException


BLUEPRINT_FOLDER = 'blueprint'
JSON_TEMPLATES_FOLDER = 'json'
DM_EL_ATT_DU_PR_SE_STRUCTURE = 'DATA_MGMT_dataUtility_security_privacy_elem.json'
DM_EL_ATT_DU_PR_SE_PROPERTIES_STRUCTURE = 'DATA_MGMT_dataUtility_security_privacy_elem_prop.json'
DM_METRICS = 'metrics.json'
DM_METRICS_DATA_UTILITY = 'dataUtility'
DM_METRICS_PRIVACY = 'privacy'
DM_METRICS_SECURITY = 'security'

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
IS_DATA_SOURCES = "Data_Sources"
IS_FLOW = 'Flow'
IS_FLOW_PLATFORM = 'platform'
IS_FLOW_PARAMS = 'parameters'
IS_FLOW_SOURCE = 'source'
IS_TESTING_OUTPUT_DATA = 'Testing_Output_Data'
IS_TOD_METHODID = 'method_id'
IS_TOD_ZIP = 'zip_data'
DATA_MANAGEMENT_SECTION = 'DATA_MANAGEMENT'
DM_EL_METHOD_ID = 'method_id'
DM_EL_ATTRIBUTES = 'attributes'
DM_EL_ATT_DATA_UTILITY = 'dataUtility'
DM_EL_ATT_PRIVACY = 'privacy'
DM_EL_ATT_SECURITY = 'security'
DM_EL_ATT_DU_PR_SE_ID = 'id'
DM_EL_ATT_DU_PR_SE_NAME = 'name'
DM_EL_ATT_DU_PR_SE_TYPE = 'type'
DM_EL_ATT_DU_PR_SE_PROPERTIES = 'properties'
DM_EL_ATT_DU_PR_SE_PROPERTIES_UNIT = 'unit'
DM_EL_ATT_DU_PR_SE_PROPERTIES_MAX = 'maximum'
DM_EL_ATT_DU_PR_SE_PROPERTIES_MIN = 'minimum'
DM_EL_ATT_DU_PR_SE_PROPERTIES_VALUE = 'value'
ABSTRACT_PROPERTIES_SECTION = 'ABSTRACT_PROPERTIES'
COOKBOOK_APPENDIX_SECTION = 'COOKBOOK_APPENDIX'
EXPOSED_API_SECTION = 'EXPOSED_API'

# const referred to the api file
API_PATHS = 'paths'

# const referred to the metrics file
METRICS_ROOT = 'metrics'
METRIC_NAME = 'name'
METRIC_UNIT = 'unit'
METRIC_MAXIMUM = 'maximum'
METRIC_MINIMUM = 'minimum'

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
        try:
            self.vdc_config = VDCConfigFile(vdc_repo_path, VDC_CONFIG)
        except MissingReferenceException:
            raise FileNotFoundError('Missing file ' + VDC_CONFIG + 'in repo ' + vdc_repo_path)

        # loading dal_config_file
        self.dal_configs = []
        for path in dal_repo_paths:
            try:
                self.dal_configs.append(DALConfigFile(path, DAL_CONFIG))
            except MissingReferenceException:
                raise FileNotFoundError('Missing file ' + DAL_CONFIG + 'in repo ' + path)

        # if method update the bp file is loaded from the configuration file
        if update:
            print("Trying to open existing blueprint at " + self.vdc_config.get_blueprint_path())
            self.bp = get_dict_from_file(self.vdc_config.get_blueprint_path())

    def add_exposed_api(self):
        try:
            path = self.vdc_config.get_api_path()
            print('Opening api file: ' + path)
            self.bp[EXPOSED_API_SECTION] = get_dict_from_file(path)
        except MissingReferenceException as e:
            e.print(VDC_CONFIG)

    def add_is_tags(self):
        try:
            path = self.vdc_config.get_api_path()
            print('Gathering methods info from API file')
            api = get_dict_from_file(path)
            tags = []
            for method in api[API_PATHS].keys():
                tag_template = copy.deepcopy(self.template[INTERNAL_STRUCTURE_SECTION][IS_OVERVIEW][IS_OW_TAGS][0])
                tag_template[IS_OW_TAGS_METHODID] = method.replace('/', '')
                tags.append(tag_template)
            self.bp[INTERNAL_STRUCTURE_SECTION][IS_OVERVIEW][IS_OW_TAGS] = tags
        except TypeError:
            print('API file corrupted!\nCannot extract methods info from API file')
        except MissingReferenceException as e:
            e.print(VDC_CONFIG)

    def add_is_flow(self):
        try:
            if self.vdc_config.get_flow_platform().lower() == NODERED:
                print('Detected Node-Red platform')
                path = self.vdc_config.get_flow_source_path()
                print('Gathering flow data from ' + path)
                flow = {
                    IS_FLOW_PLATFORM: self.vdc_config.get_flow_platform(),
                    IS_FLOW_SOURCE: get_dict_from_file(path)
                }
                self.bp[INTERNAL_STRUCTURE_SECTION][IS_FLOW] = flow
            elif self.vdc_config.get_flow_platform().lower() == SPARK:
                print('Detected SPARK platform')
                flow = {
                    IS_FLOW_PLATFORM: self.vdc_config.get_flow_platform(),
                    IS_FLOW_PARAMS: ''
                }
                self.bp[INTERNAL_STRUCTURE_SECTION][IS_FLOW] = flow
        except MissingReferenceException as e:
            e.print(VDC_CONFIG)

    def add_cookbook(self):
        cookbook = {
            VDC_SECTION: {},
            DAL_SECTION: {}
        }
        try:
            with open(self.vdc_config.get_cookbook_path(), 'r') as vdc_cookbook:
                cookbook[VDC_SECTION][self.vdc_config.repo_name] = vdc_cookbook.read()
        except MissingReferenceException as e:
            e.print(VDC_CONFIG)
        for dal_config in self.dal_configs:
            try:
                with open(dal_config.get_cookbook_path(), 'r') as dal_cookbook:
                    cookbook[DAL_SECTION][dal_config.repo_name] = dal_cookbook.read()
            except MissingReferenceException as e:
                e.print(dal_config.repo_name)
        self.bp[COOKBOOK_APPENDIX_SECTION] = cookbook

    def add_is_testing_output_data(self):
        try:
            api = get_dict_from_file(self.vdc_config.get_api_path())
            outdata = []
            zip_path = self.vdc_config.get_data_management_path()
            print('Zip files at ' + zip_path)
            for method in api[API_PATHS].keys():
                outdata_template = copy.deepcopy(self.template[INTERNAL_STRUCTURE_SECTION][IS_TESTING_OUTPUT_DATA][0])
                method = method.replace('/', '')
                outdata_template[IS_TOD_METHODID] = method
                zip_file = os.path.join(zip_path, method + ZIP_FORMAT)
                print('Searching for ' + zip_file)
                if os.path.exists(zip_file):
                    print('Zip file found!')
                    outdata_template[IS_TOD_ZIP] = os.path.join(self.vdc_config.get_data_management(), method + ZIP_FORMAT)
                else:
                    print('Zip file not found!')
                    outdata_template[IS_TOD_ZIP] = ''
                outdata.append(outdata_template)
            self.bp[INTERNAL_STRUCTURE_SECTION][IS_TESTING_OUTPUT_DATA] = outdata
        except MissingReferenceException as e:
            e.print(VDC_CONFIG)

    def add_is_data_sources(self):
        # Copy the content of proto files
        data_sources = {}
        for dal_config in self.dal_configs:
            imports = []
            # Parse the main proto file looking for all the imports statement
            file_content = ""
            try:
                with open(dal_config.get_path_from_main_proto(), 'r') as main_proto:
                    main_proto_folder = os.path.abspath(os.path.join(dal_config.get_path_from_main_proto(), os.pardir))
                    print("main_proto_folder: " + main_proto_folder)
                    file_lines = main_proto.readlines()
                    for line in file_lines:
                        file_content += line
                        matches = re.match(r'import "(.*)";', line)
                        if matches:
                            # line is an import statement
                            imported_file = matches.group(1)
                            if imported_file not in imports:
                                print("Adding " + imported_file)
                                imports.append(imported_file)
                # TODO: do something with the whole the content of the file (file_content)
                main_proto_file_name = os.path.basename(dal_config.get_main_proto())
                data_sources[main_proto_file_name] = file_content

                # For each imported file, recursively look for imports statement
                for proto in imports:
                    file_content = ""
                    subproto_file = os.path.join(main_proto_folder, proto)
                    print("Opening sub-proto file: " + subproto_file)
                    with open(subproto_file, 'r') as proto_file:
                        file_lines = proto_file.readlines()
                        for line in file_lines:
                            file_content += line
                            matches = re.match(r'import "(.*)";', line)
                            if matches:
                                # line is an import statement
                                imported_file = matches.group(1)
                                if imported_file not in imports:
                                    imports.append(imported_file)
                    # TODO: do something with the whole the content of the file (file_content)
                    data_sources[proto] = file_content
            except MissingReferenceException as e:
                e.print(dal_config.repo_name)
        self.bp[INTERNAL_STRUCTURE_SECTION][IS_DATA_SOURCES] = data_sources

    def add_data_management(self):
        #try:
            api_path = self.vdc_config.get_api_path()
            print('Gathering methods info from API file')
            api = get_dict_from_file(api_path)
            metrics_path = os.path.abspath(os.path.join(BLUEPRINT_FOLDER, JSON_TEMPLATES_FOLDER, DM_METRICS))
            print('Gathering standard metrics from: ' + metrics_path)
            dm_du_pr_se_elem = get_dict_from_file(os.path.abspath(os.path.join(BLUEPRINT_FOLDER, JSON_TEMPLATES_FOLDER,
                                                                               DM_EL_ATT_DU_PR_SE_STRUCTURE)))
            dm_du_pr_se_elem_prop = get_dict_from_file(os.path.abspath(os.path.join(BLUEPRINT_FOLDER,
                                                                                    JSON_TEMPLATES_FOLDER,
                                                                                    DM_EL_ATT_DU_PR_SE_PROPERTIES_STRUCTURE)))

            data_mgmt_list = []
            for method_raw in api[API_PATHS].keys():
                method = method_raw.replace('/', '')
                dm_elem = copy.deepcopy(self.template[DATA_MANAGEMENT_SECTION][0])
                dm_elem[DM_EL_METHOD_ID] = method
                # Fill ATTRIBUTES section of each method element
                data_mgmt_path = self.vdc_config.get_data_management_path()
                method_metrics_path = os.path.abspath(os.path.join(data_mgmt_path, method + "_metrics.json"))
                metrics = get_dict_from_file(method_metrics_path)
                print("Gathering metrics of method " + method + " from " + method_metrics_path)
                # Fill dataUtility elements
                for metric in metrics[METRICS_ROOT][DM_METRICS_DATA_UTILITY]:
                    # Extract template as a copy of the structure taken from file
                    dm_metric_elem = copy.deepcopy(dm_du_pr_se_elem)
                    dm_metric_elem_prop = copy.deepcopy(dm_du_pr_se_elem_prop)
                    # Fill the structure
                    dm_metric_elem[DM_EL_ATT_DU_PR_SE_ID] = metric[METRIC_NAME]
                    # TODO: name and type missing
                    dm_metric_elem_prop[DM_EL_ATT_DU_PR_SE_PROPERTIES_UNIT] = metric[METRIC_UNIT]
                    dm_metric_elem_prop[DM_EL_ATT_DU_PR_SE_PROPERTIES_MAX] = metric[METRIC_MAXIMUM]
                    dm_metric_elem_prop[DM_EL_ATT_DU_PR_SE_PROPERTIES_MIN] = metric[METRIC_MINIMUM]
                    # TODO: where to get the metrics value??
                    dm_metric_elem_prop[DM_EL_ATT_DU_PR_SE_PROPERTIES_VALUE] = metric[METRIC_UNIT]

                    dm_metric_elem[DM_EL_ATT_DU_PR_SE_PROPERTIES] = {metric[METRIC_NAME]: dm_metric_elem_prop}
                    dm_elem[DM_EL_ATTRIBUTES][DM_EL_ATT_DATA_UTILITY].append(dm_metric_elem)

                # Fill privacy elements
                for metric in metrics[METRICS_ROOT][DM_METRICS_PRIVACY]:
                    # Extract template as a copy of the structure taken from file
                    dm_metric_elem = copy.deepcopy(dm_du_pr_se_elem)
                    dm_metric_elem_prop = copy.deepcopy(dm_du_pr_se_elem_prop)
                    # Fill the structure
                    dm_metric_elem[DM_EL_ATT_DU_PR_SE_ID] = metric[METRIC_NAME]
                    # TODO: name and type missing
                    dm_metric_elem_prop[DM_EL_ATT_DU_PR_SE_PROPERTIES_UNIT] = metric[METRIC_UNIT]
                    dm_metric_elem_prop[DM_EL_ATT_DU_PR_SE_PROPERTIES_MAX] = metric[METRIC_MAXIMUM]
                    dm_metric_elem_prop[DM_EL_ATT_DU_PR_SE_PROPERTIES_MIN] = metric[METRIC_MINIMUM]
                    # TODO: where to get the metrics value??
                    dm_metric_elem_prop[DM_EL_ATT_DU_PR_SE_PROPERTIES_VALUE] = metric[METRIC_UNIT]

                    dm_metric_elem[DM_EL_ATT_DU_PR_SE_PROPERTIES] = {metric[METRIC_NAME]: dm_metric_elem_prop}
                    dm_elem[DM_EL_ATTRIBUTES][DM_EL_ATT_PRIVACY].append(dm_metric_elem)

                # Fill security elements
                for metric in metrics[METRICS_ROOT][DM_METRICS_SECURITY]:
                    # Extract template as a copy of the structure taken from file
                    dm_metric_elem = copy.deepcopy(dm_du_pr_se_elem)
                    dm_metric_elem_prop = copy.deepcopy(dm_du_pr_se_elem_prop)
                    # Fill the structure
                    dm_metric_elem[DM_EL_ATT_DU_PR_SE_ID] = metric[METRIC_NAME]
                    # TODO: name and type missing
                    dm_metric_elem_prop[DM_EL_ATT_DU_PR_SE_PROPERTIES_UNIT] = metric[METRIC_UNIT]
                    dm_metric_elem_prop[DM_EL_ATT_DU_PR_SE_PROPERTIES_MAX] = metric[METRIC_MAXIMUM]
                    dm_metric_elem_prop[DM_EL_ATT_DU_PR_SE_PROPERTIES_MIN] = metric[METRIC_MINIMUM]
                    # TODO: where to get the metrics value??
                    dm_metric_elem_prop[DM_EL_ATT_DU_PR_SE_PROPERTIES_VALUE] = metric[METRIC_UNIT]

                    dm_metric_elem[DM_EL_ATT_DU_PR_SE_PROPERTIES] = {metric[METRIC_NAME]: dm_metric_elem_prop}
                    dm_elem[DM_EL_ATTRIBUTES][DM_EL_ATT_SECURITY].append(dm_metric_elem)

                data_mgmt_list.append(dm_elem)

            self.bp[DATA_MANAGEMENT_SECTION] = data_mgmt_list
        #except TypeError:
        #    print('API file corrupted!\nCannot extract methods info from API file')
        #except MissingReferenceException as e:
        #    e.print(VDC_CONFIG)

    def save(self):
        file_path = self.vdc_config.get_blueprint_path()
        print("Saving blueprint at " + file_path)
        with open(file_path, 'w') as outfile:
            json.dump(self.bp, outfile, indent=4)


# supported extension for dictionaries
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
        return ''


def generate_api_metrics_files(vdc_repo_path):
    # loading vdc_config_file
    try:
        vdc_config = VDCConfigFile(vdc_repo_path, VDC_CONFIG)
    except MissingReferenceException:
        raise FileNotFoundError('Missing file ' + VDC_CONFIG + 'in repo ' + vdc_repo_path)

    # Retrieving API file
    try:
        api_path = vdc_config.get_api_path()
        print('Opening api file: ' + api_path)
        api = get_dict_from_file(api_path)
        metrics_template_path = os.path.abspath(os.path.join(BLUEPRINT_FOLDER, JSON_TEMPLATES_FOLDER, DM_METRICS))
    except MissingReferenceException as e:
        e.print(VDC_CONFIG)

    # For each method create a file with method name as prefix and
    # copy the whole list of standard metrics as content
    for method_raw in api[API_PATHS].keys():
        method = method_raw.replace('/', '')
        print("Creating metrics file for method '" + method + "'")
        data_mgmt_path = vdc_config.get_data_management_path()
        method_metrics_path = os.path.abspath(os.path.join(data_mgmt_path, method + "_metrics.json"))

        with open(metrics_template_path, "r") as source, open(method_metrics_path, "w") as destination:
            destination.write(source.read())
