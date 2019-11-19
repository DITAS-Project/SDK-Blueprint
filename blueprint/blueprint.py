import datetime
import json
import os
import copy
import yaml
import re
from blueprint.config_file.vdc_configfile import VDCConfigFile
from blueprint.config_file.dal_configfile import DALConfigFile
from blueprint.config_file.configfile import MissingReferenceException, InvalidRootDirectory

BLUEPRINT_FOLDER = 'blueprint'
JSON_TEMPLATES_FOLDER = 'json'

DM_JSON_TEMPLATE = os.path.abspath(os.path.join(BLUEPRINT_FOLDER, JSON_TEMPLATES_FOLDER, 'data_management.json'))

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
DATA_SOURCES_SCHEMA = "schema"
IS_FLOW = 'Flow'
IS_FLOW_PLATFORM = 'platform'
IS_FLOW_PARAMS = 'parameters'
IS_FLOW_SOURCE = 'source'
IS_TESTING_OUTPUT_DATA = 'Testing_Output_Data'
IS_TOD_METHODID = 'method_id'
IS_TOD_ZIP = 'zip_data'
IS_METHODS_INPUT = 'Methods_Input'
IS_MI_METHODS = 'Methods'
IS_MI_METHODS_METHODID = 'method_id'
DATA_MANAGEMENT_SECTION = 'DATA_MANAGEMENT'
DM_EL_METHOD_ID = 'method_id'
DM_EL_ATTRIBUTES = 'attributes'
ABSTRACT_PROPERTIES_SECTION = 'ABSTRACT_PROPERTIES'
COOKBOOK_APPENDIX_SECTION = 'COOKBOOK_APPENDIX'
EXPOSED_API_SECTION = 'EXPOSED_API'

# const referred to the api file
API_PATHS = 'paths'

# const referred to the metrics file
METRIC_NAME = 'name'
METRIC_UNIT = 'unit'
METRIC_MAXIMUM = 'maximum'
METRIC_MINIMUM = 'minimum'


def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")


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
            # TODO: Could the constructor of VDCConfigFile actually raise this exceptions??
        except MissingReferenceException:
            print('ERROR: Missing file ' + VDC_CONFIG + 'in repo ' + vdc_repo_path)

        # loading dal_config_file
        self.dal_configs = []
        for path in dal_repo_paths:
            try:
                self.dal_configs.append(DALConfigFile(path, DAL_CONFIG))
                # TODO: Could the constructor of DALConfigFile actually raise this exceptions??
            except MissingReferenceException:
                print('ERROR: Missing file ' + DAL_CONFIG + 'in repo ' + path)

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
        except InvalidRootDirectory as e:
            e.print(VDC_CONFIG)

    def add_is_tags(self):
        try:
            path = self.vdc_config.get_api_path()
            print('Gathering methods info from API file')
            api = get_dict_from_file(path)
            tags = []

            for method in api[API_PATHS].keys():
                operation_id = find_op_id(api[API_PATHS][method])
                tag_template = copy.deepcopy(self.template[INTERNAL_STRUCTURE_SECTION][IS_OVERVIEW][IS_OW_TAGS][0])
                tag_template[IS_OW_TAGS_METHODID] = operation_id
                tags.append(tag_template)
            self.bp[INTERNAL_STRUCTURE_SECTION][IS_OVERVIEW][IS_OW_TAGS] = tags
        except TypeError:
            print('API file corrupted!\nCannot extract methods info from API file')
        except MissingReferenceException as e:
            e.print(VDC_CONFIG)
        except InvalidRootDirectory as e:
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
        except InvalidRootDirectory as e:
            e.print(VDC_CONFIG)

    def add_cookbook(self):
        try:
            self.bp[COOKBOOK_APPENDIX_SECTION] = get_dict_from_file(self.vdc_config.get_cookbook_path())
        except MissingReferenceException as e:
            e.print(VDC_CONFIG)
        except InvalidRootDirectory as e:
            e.print(VDC_CONFIG)

    def add_is_testing_output_data(self):
        try:
            api = get_dict_from_file(self.vdc_config.get_api_path())
            outdata = []
            zip_path = self.vdc_config.get_data_management_path()
            print('Zip files at ' + zip_path)
            for method in api[API_PATHS].keys():
                outdata_template = copy.deepcopy(self.template[INTERNAL_STRUCTURE_SECTION][IS_TESTING_OUTPUT_DATA][0])
                operation_id = find_op_id(api[API_PATHS][method])
                outdata_template[IS_TOD_METHODID] = operation_id
                zip_file = os.path.join(zip_path, operation_id + ZIP_FORMAT)
                print('Searching for ' + zip_file)
                if os.path.exists(zip_file):
                    print('Zip file found!')
                    outdata_template[IS_TOD_ZIP] = os.path.join(self.vdc_config.get_data_management(),
                                                                method.replace("/", "-") + ZIP_FORMAT)
                else:
                    print('Zip file not found!')
                    outdata_template[IS_TOD_ZIP] = ''
                outdata.append(outdata_template)
            self.bp[INTERNAL_STRUCTURE_SECTION][IS_TESTING_OUTPUT_DATA] = outdata
        except MissingReferenceException as e:
            e.print(VDC_CONFIG)
        except InvalidRootDirectory as e:
            e.print(VDC_CONFIG)

    def add_is_data_sources(self):
        # Copy the content of proto files
        data_sources = []
        for dal_config in self.dal_configs:
            print('#####################################################################################')
            try:
                for i in range(dal_config.count_sources()):
                    imports = []
                    file_content = ""
                    schema = []

                    data_source = get_dict_from_file(dal_config.get_path_from_source(i))

                    # Parse the main proto file looking for all the imports statement
                    with open(dal_config.get_path_from_main_proto(i), 'r') as main_proto:
                        main_proto_folder = os.path.abspath(os.path.join(dal_config.get_path_from_main_proto(i), os.pardir))
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
                    main_proto_file_name = os.path.basename(dal_config.get_main_proto(i))
                    #data_sources[main_proto_file_name] = file_content
                    schema.append({main_proto_file_name: file_content})

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
                        #data_sources[proto] = file_content
                        schema.append({proto: file_content})
                    data_source[DATA_SOURCES_SCHEMA] = schema
                    data_sources.append(data_source)
            except MissingReferenceException as e:
                e.print(dal_config.repo_name)
            except InvalidRootDirectory as e:
                e.print(VDC_CONFIG)
        self.bp[INTERNAL_STRUCTURE_SECTION][IS_DATA_SOURCES] = data_sources

    def add_data_management(self):
        try:
            api_path = self.vdc_config.get_api_path()
            print('Gathering methods info from API file')
            api = get_dict_from_file(api_path)

            data_mgmt_list = []
            for method_raw in api[API_PATHS].keys():
                operation_id = find_op_id(api[API_PATHS][method_raw])
                dm_elem = copy.deepcopy(self.template[DATA_MANAGEMENT_SECTION][0])
                dm_elem[DM_EL_METHOD_ID] = operation_id
                # Fill ATTRIBUTES section of each method element
                data_mgmt_path = self.vdc_config.get_data_management_path()
                method_metrics_path = os.path.abspath(os.path.join(data_mgmt_path, operation_id + "_metrics.json"))

                print("Gathering metrics of operation " + operation_id + " from " + method_metrics_path)
                metrics = get_dict_from_file(method_metrics_path)

                dm_elem[DM_EL_ATTRIBUTES] = copy.deepcopy(metrics)
                data_mgmt_list.append(dm_elem)

            self.bp[DATA_MANAGEMENT_SECTION] = data_mgmt_list
        except TypeError:
            print('API file corrupted!\nCannot extract methods info from API file')
        except MissingReferenceException as e:
            e.print(VDC_CONFIG)
        except InvalidRootDirectory as e:
            e.print(VDC_CONFIG)

    def add_is_methods_input(self):
        try:
            path = self.vdc_config.get_api_path()
            print('Gathering methods info from API file')
            api = get_dict_from_file(path)
            methods_input = []

            for method in api[API_PATHS].keys():
                #print("Found method: ", method.strip("/"))
                operation_id = find_op_id(api[API_PATHS][method])
                mi_template = copy.deepcopy(self.template[INTERNAL_STRUCTURE_SECTION][IS_METHODS_INPUT][IS_MI_METHODS][0])
                mi_template[IS_MI_METHODS_METHODID] = operation_id
                methods_input.append(mi_template)
            self.bp[INTERNAL_STRUCTURE_SECTION][IS_METHODS_INPUT][IS_MI_METHODS] = methods_input
        except TypeError:
            print('API file corrupted!\nCannot extract methods info from API file')
        except MissingReferenceException as e:
            e.print(VDC_CONFIG)

    def save(self):
        file_path = self.vdc_config.get_blueprint_path()
        print("Saving blueprint at " + file_path)
        with open(file_path, 'w') as outfile:
            json.dump(self.bp, outfile, indent=4, default=datetime_handler)


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
        # TODO: Could the constructor of VDCConfigFile actually raise those exceptions??
    except MissingReferenceException:
        print('ERROR: Missing file ' + VDC_CONFIG + 'in repo ' + vdc_repo_path)

    # Retrieving API file
    try:
        api_path = vdc_config.get_api_path()
        print('Opening api file: ' + api_path)
        api = get_dict_from_file(api_path)
        metrics_template_path = DM_JSON_TEMPLATE

        # For each method create a file with method name as prefix and
        # copy the whole list of standard metrics as content
        for method_raw in api[API_PATHS].keys():
            operation_id = find_op_id(api[API_PATHS][method_raw])
            print("Creating metrics file for operation '" + operation_id + "'")
            data_mgmt_path = vdc_config.get_data_management_path()
            method_metrics_path = os.path.abspath(os.path.join(data_mgmt_path, operation_id + "_metrics.json"))

            # print("metrics_template_path", metrics_template_path)
            # print("method_metrics_path", method_metrics_path)

            with open(metrics_template_path, "r") as source, open(method_metrics_path, "w") as destination:
                destination.write(source.read())

    except MissingReferenceException as e:
        e.print(VDC_CONFIG)
    except InvalidRootDirectory as e:
        e.print(VDC_CONFIG)


# For each method structure, find the corresponding operationId attribute
# for whatsoever HTTP method

def find_op_id(j):
    if isinstance(j, dict):
        if 'operationId' in j:
            return j['operationId']
        for v in j.values():
            r = find_op_id(v)
            if r: return r
    if isinstance(j, list):
        for e in j:
            r = find_op_id(e)
            if r: return r