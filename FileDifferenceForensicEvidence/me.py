import os
from shared_utilities import Configuration
import shutil
import re

def get_name():
    return "Merge evidences"

def execute(configuration : Configuration):
    if os.path.exists(configuration.current_folder + "\\me\\"):
        shutil.rmtree(configuration.current_folder + "\\me\\")
    os.makedirs(configuration.current_folder + "\\me\\")
    def write_content_merged(dictionary:str,output_me_file_with_full_path:str, label_for_operation:str):
        result = ""
        for key in dictionary:
            result = result + key + "\t" + label_for_operation + "\t" + str(dictionary[key]) + "\n"
        with open(output_me_file_with_full_path, "a") as file:
            file.write(result)
    def merge_evidence_for_file(input_pe_files_with_full_path, output_me_file_with_full_path:str):
        dictionary_access = {}
        dictionary_modify = {}
        dictionary_created = {}
        dictionary_changed = {}
        dictionary_deleted = {}
        for pe_file in input_pe_files_with_full_path:
            with open(pe_file) as file_stream:
                lines = file_stream.readlines()
                for line in lines:
                    if('\t' in line):
                        splitted = re.split(r'\t+', line)
                        found_file = splitted[0]
                        operation = splitted[1].replace("\n","")
                        if (operation == "a"):
                            if found_file in dictionary_access:
                                dictionary_access[found_file] = dictionary_access[found_file] + 1
                            else:
                                dictionary_access[found_file] = 1
                        if(operation == "m"):
                            if found_file in dictionary_modify:
                                dictionary_modify[found_file] = dictionary_modify[found_file] + 1
                            else:
                                dictionary_modify[found_file] = 1
                        if(operation == "c"):
                            if found_file in dictionary_changed:
                                dictionary_changed[found_file] = dictionary_changed[found_file] + 1
                            else:
                                dictionary_changed[found_file] = 1
                        if(operation == "cr"):
                            if found_file in dictionary_created:
                                dictionary_created[found_file] = dictionary_created[found_file] + 1
                            else:
                                dictionary_created[found_file] = 1
                        if(operation == "d"):
                            if found_file in dictionary_deleted:
                                dictionary_deleted[found_file] = dictionary_deleted[found_file] + 1
                            else:
                                dictionary_deleted[found_file] = 1

        if os.path.exists(output_me_file_with_full_path and configuration.overwrite_existing_files_and_snapshots):
            os.remove(output_me_file_with_full_path)
        with open(output_me_file_with_full_path, 'w'):
            pass
        write_content_merged(dictionary_access,output_me_file_with_full_path,"a")
        write_content_merged(dictionary_modify,output_me_file_with_full_path,"m")
        write_content_merged(dictionary_changed,output_me_file_with_full_path,"c")
        write_content_merged(dictionary_created,output_me_file_with_full_path,"cr")
        write_content_merged(dictionary_deleted,output_me_file_with_full_path,"d")

    def merge_evidence():
        merge_evidence_for_file([configuration.current_folder + "\\pe\\" + configuration.name_of_noise_action + ".pe"],configuration.current_folder + "\\me\\" + configuration.name_of_noise_action + ".me")
        for action in configuration.actions:
            configuration.log.info("Start merge evidence for action " + action[1])
            try:
                pe_files = []
                for i in range(1, configuration.amount_of_executions_per_action + 1):
                    pe_files.append(configuration.current_folder + "\\pe\\" + action[1] + "." + str(i) + ".pe")
                merge_evidence_for_file(pe_files,configuration.current_folder + "\\me\\" + action[1] + ".me")
            except Exception as exception_argument:
                configuration.log.error("Exception occurred while merge evidence  for action " + action[1] + ":")
                configuration.log.error(exception_argument, exc_info=True)
            configuration.log.info("Merge evidence for action " + action[1] + " finished")
            
    try:
        merge_evidence()
    except Exception as exception:
        configuration.log.error("Exception occurred in me.py:")
        configuration.log.error(exception, exc_info=True)