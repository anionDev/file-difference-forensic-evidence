import json
import pickle
import logging
import os
import sys
import subprocess
import time
import re
import shlex
import argparse
import shutil

class Configuration:
    current_folder = os.path.dirname(os.path.abspath(__file__)) + "\\result"
    log_file = "log.log"
    log_filemode = 'a'
    log_format = '%(asctime)s.%(msecs)03d %(name)s [%(levelname)s] %(message)s'
    log_dateformat = '%Y-%m-%d %H:%M:%S'
    log_loglevel = logging.DEBUG
    log = logging.getLogger('Calculate evidences')
    amount_of_executions_per_action = 3
    actions = [["Special:WaitUntilUserContinues:install program","action1",[]], 
        ["Special:WaitUntilUserContinues:uninstall program","action2",[]],]
    name_of_noise_action = "noise"
    name_of_noise_idiff_file = name_of_noise_action + ".idiff"
    path_of_init_raw = "C:\\temp\\initraw\\"
    folder_for_idiff_files = "C:\\temp\\\\idiff\\"
    shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference = "C:\\temp\\shared\\"

    name_of_vm_to_analyse = "Win10M118"
    user_of_vm_to_analyse = "Marius"
    password_of_vm_to_analyse = ""
    snapshot_name_for_initial_state_of_vm_to_analyse = "initial2suspended"

    name_of_vm_which_has_idifference = "ST_fiwalk"
    user_of_vm_which_has_idifference = "fiwalk"
    password_of_which_has_idifference = "password"
    path_of_python3_in_vm_which_has_idifference = "/usr/bin/python3"
    path_of_difference_in_vm_which_has_idifference = "home/" + user_of_vm_which_has_idifference + "/dfxml-master/python/idifference2.py"

    generate_init_raw = True
    name_of_shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference = "sharepoint"
    vboxmanage_executable = "C:/Program Files/Oracle/VirtualBox/VBoxManage.exe"
    noise_recording_time_in_seconds = 300
    name_of_init_raw_file = "init.raw"
    name_of_noise_raw_file = name_of_noise_action + ".raw"
    clear_logfile_before_execution = True
    delete_trace_image_after_analysis = False
    use_gui_mode_for_vm = True
    create_snapshots_after_action_execution = True

def get_vm_state(configuration, vm_name):
    return re.compile("VMState=\"(.*)\"").search(subprocess.check_output("\"" + configuration.vboxmanage_executable + "\" " + "showvminfo " + vm_name + " --machinereadable").decode()).group(1)

def start_program(configuration, executable_with_full_path, argument, waiting_time_in_seconds_after_execution = 1):
    configuration.log.debug("Start " + executable_with_full_path + " " + argument)
    arguments = list()
    arguments.insert(len(arguments), executable_with_full_path)
    for argument_without_whitespace in argument.split():
        arguments.insert(len(arguments),argument_without_whitespace)
    process = subprocess.Popen(arguments)
    process.wait()
    time.sleep(waiting_time_in_seconds_after_execution)
def add_shared_folder_for_vm_which_has_idifference(configuration):
    start_program(configuration, configuration.vboxmanage_executable,"sharedfolder add " + configuration.name_of_vm_which_has_idifference + " --name " + configuration.name_of_shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + " -hostpath " + configuration.shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + " -automount")

def remove_shared_folder_from_vm_which_has_idifference(configuration):
    start_program(configuration, configuration.vboxmanage_executable, "sharedfolder remove " + configuration.name_of_vm_which_has_idifference + " --name " + configuration.name_of_shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference)

def execute_program_in_vm(name_of_vm,executable_file_with_path, username, password, waiting_time_in_seconds_after_execution, arguments):
    if(len(arguments) == 0):
       argument = " -- " + " ".join(map(lambda argument: "\"" + argument + "\"",arguments))
    else:
       argument = ""
    start_program(configuration, configuration.vboxmanage_executable, "guestcontrol " + name_of_vm + " run --exe " + executable_file_with_path + " --username " + username + " --password " + password,waiting_time_in_seconds_after_execution + argument)

def ensure_vm_is_running(name_of_vm, configuration):
    if get_vm_state(configuration, name_of_vm) != "running":
        if use_gui_mode_for_vm:
            gui_argument = "gui"
        else:
            gui_argument = "headless"
        start_program(configuration, configuration.vboxmanage_executable,"startvm " + name_of_vm + " -type " + gui_argument, 5)

def ensure_vm_is_shutdown(name_of_vm, configuration):
    if get_vm_state(configuration, name_of_vm) == "running":
        start_program(configuration, configuration.vboxmanage_executable,"controlvm " + name_of_vm + " poweroff", 5)

def ensure_vm_is_in_save_state(name_of_vm, configuration):
    if get_vm_state(configuration, name_of_vm) == "running":
        start_program(configuration.vboxmanage_executable,"controlvm " + name_of_vm + " savestate", 5)

def continue_vm(configuration):
    ensure_vm_is_running(configuration.name_of_vm_to_analyse, configuration.configuration.use_gui_mode_for_vm)

def execute_action_in_vm(action,configuration):
    execute_program_in_vm(name_of_vm_to_analyse, action[0], configuration.user_of_vm_to_analyse, configuration.password_of_vm_to_analyse, 5, action[2], configuration)

def save_state_of_vm(name_of_vm,configuration):
    ensure_vm_is_in_save_state(name_of_vm,configuration)
def create_snapshot(name_of_vm, snapshot_name):
    start_program(configuration, configuration.vboxmanage_executable,"snapshot " + name_of_vm + " take " + snapshot_name, 5)
    
def start_program_with_parameter_list(executable_with_full_path, arguments, waiting_time_in_seconds_after_execution=1):
    log.debug("Start " + executable_with_full_path + " " + " ".join(arguments))
    argument_list = list()
    argument_list.append(executable_with_full_path)
    argument_list.extend(arguments)
    process = subprocess.Popen(argument_list)
    process.wait()
    time.sleep(waiting_time_in_seconds_after_execution)

def get_hdd_uuid(configuration, vm_name):
        id = subprocess.check_output("\"" + configuration.vboxmanage_executable + "\" " + "showvminfo " + vm_name + " --machinereadable").decode()
        return re.compile("\"SATA-ImageUUID-0-0\"=\"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\"").search(id).group(1)
