import os
from shared_utilities import Configuration
import re
import shutil

def get_name():
    return "Calculate characteristical evidences"

def execute(configuration: Configuration):
    if os.path.exists(configuration.working_directory + "ce\\"):
        shutil.rmtree(configuration.working_directory + "ce\\")
    os.makedirs(configuration.working_directory + "ce\\")
    class Trace(object):
        def __init__(self, file, operation,amount_of_occurrence):
            self.file = file
            self.operation = operation
            self.amount_of_occurrence = amount_of_occurrence
        def __eq__(self, other):
            if isinstance(self, other.__class__):
                return (self.file == other.file) and (self.operation == other.operation) and (self.amount_of_occurrence == other.amount_of_occurrence)
            else:
                return False
        def __hash__(self):
            return 0
    def get_trace_from_me_file(me_file_with_full_path:str):
        traces = set()
        with open(me_file_with_full_path) as fileStream:
            lines = fileStream.readlines()
            for line in lines:
                if ('\t' in line):
                    splitted = re.split(r'\t+', line)
                    traces.add(Trace(splitted[0],splitted[1],int(splitted[2])))
        return traces
    def characteristic_evidence_for_file(me_file_with_full_path:str,me_files_of_ignored_traced,result_ce_file_with_full_path:str):
        if os.path.exists(result_ce_file_with_full_path and configuration.overwrite_existing_files_and_snapshots):
            os.remove(result_ce_file_with_full_path)
        trace_of_action = get_trace_from_me_file(me_file_with_full_path)
        ignored_traces = set()
        for me_file_of_ignored_traced in me_files_of_ignored_traced:
            for trace in get_trace_from_me_file(me_file_of_ignored_traced):
                ignored_traces.add(trace)
        possible_characteristic_traces_of_action = trace_of_action - ignored_traces
        characteristic_traces = set()
        for possible_characteristic_trace in possible_characteristic_traces_of_action:
            if possible_characteristic_trace.amount_of_occurrence == configuration.amount_of_executions_per_action:
                characteristic_traces.add(possible_characteristic_trace)
        characteristic_traces_lines = list()
        for characteristic_trace in characteristic_traces:
            characteristic_traces_lines.append(characteristic_trace.file + "\t" + characteristic_trace.operation)
        with open(result_ce_file_with_full_path, "w") as file:
            file.write("\n".join(characteristic_traces_lines))
    def characteristic_evidence():
        for action in configuration.actions:
            configuration.log.info("Start characteristic evidence for action " + action[1])
            try:
                ignored_files = [configuration.working_directory + "me\\" + configuration.name_of_noise_action + ".me"]
                for ignore_action_name in configuration.actions:
                    if ignore_action_name[1] != action[1]:
                        ignored_files.append(configuration.working_directory + "me\\" + ignore_action_name[1] + ".me")
                characteristic_evidence_for_file(configuration.working_directory + "me\\" + action[1] + ".me",ignored_files,configuration.working_directory + "ce\\" + action[1] + ".ce")
            except Exception as exception_object:
                configuration.log.error("Exception occurred while characteristic evidence  for action " + action + ":")
                configuration.log.error(exception_object, exc_info=True)
            configuration.log.info("Characteristic evidence for action " + action[1] + " finished")

    try:
        characteristic_evidence()
    except Exception as exception:
        configuration.log.error("Exception occurred in ce.py:")
        configuration.log.error(exception, exc_info=True)