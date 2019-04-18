import os
import re
import shutil
from utilities import Configuration
from utilities import Action
import utilities

def get_name():
    return "Prepare evidences"

def execute(configuration: Configuration):
    if os.path.exists(configuration.working_directory + "pe\\"):
        shutil.rmtree(configuration.working_directory + "pe\\")
    os.makedirs(configuration.working_directory + "pe\\")
    def get_pe_line(line_splitted_at_tab,operation:str):
        result = list()
        try:
            if operation == "cr":
                result.append(line_splitted_at_tab[1] + "\t" + operation)
            if operation == "c":
                pass
            if operation == "d":
                result.append(line_splitted_at_tab[1] + "\t" + operation)
            if operation == "r":
                pass
            if operation == "m":
                result.append(line_splitted_at_tab[0] + "\t" + operation)
            if operation == "a":
                pass
        except:
            pass
        return result
    def prepare_evidence_for_file(idiff_file:str, pe_file:str):
        configuration.log.info("Start prepare_evidence_for_file with idiff_file='" + idiff_file + "'")
        utilities.calculate_sha2_of_file(configuration, idiff_file)
        result = list()
        with open(idiff_file) as file:
            idiff_file_lines = file.readlines()
        for line_with_new_line_character in idiff_file_lines:
            line = line_with_new_line_character.replace("\n","")
            if "\t" in line:
                splitted = re.split(r'\t+', line)
                result.extend(get_pe_line(splitted,current_operation))
            else:
                if line == "New files:":
                    current_operation = "cr"
                if line == "Deleted files:":
                    current_operation = "d"
                if line == "Renamed files:":
                    current_operation = "r"
                if line == "Files with modified contents:":
                    current_operation = "m"
                if line == "Files with changed properties:":
                    current_operation = "c"
        result_as_set = set(result)
        with open(pe_file, "w") as file:
            for line in result_as_set:
                file.write("%s\n" % line)
        utilities.calculate_sha2_of_file(configuration, pe_file)

    def prepare_evidence():
        for action in configuration.executed_action_instances_for_pe:
            configuration.log.info("Start prepare evidence for action " + action.id + " in iteration " + str(action.iteration_number))
            try:
                prepare_evidence_for_file(action.result_idiff_file, action.result_pe_file)
            except Exception as exception_object:
                configuration.log.error("Exception occurred while prepare evidence  for action " + action.id + " in iteration " + str(action.iteration_number) + ":")
                configuration.log.error(exception_object, exc_info=True)
                raise
            configuration.log.info("Prepare evidence for action " + action.id + " in iteration " + str(action.iteration_number) + " finished")

    try:
        prepare_evidence()
    except Exception as exception:
        configuration.log.error("Exception occurred in pe.py:")
        configuration.log.error(exception, exc_info=True)
        raise