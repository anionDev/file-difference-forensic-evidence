import logging
import os
import subprocess
import time
import re

class Action:
    name :str
    id :str
    argument :str
    name_of_based_snapshot :str
    is_noise_action :Action
    noise_action :Action
    def __init__(self, name:str, id:str,argument, name_of_based_snapshot:str, is_noise_action:bool):
        self.name = name
        self.id = id
        self.argument = argument
        self.name_of_based_snapshot = name_of_based_snapshot
        self.is_noise_action = is_noise_action
        if(self.is_noise_action):
            self.noise_action = None
        else:
            self.noise_action = Action(self.name + "_noise", self.id + "_noise", [], self.name_of_based_snapshot, True)

class Configuration:
    project_name = "fdfe"
    working_directory :str = f"C:\\projects\\{project_name}\\" #use 'os.path.dirname(os.path.abspath(__file__)) + "\\"' for the current directory
    log_file :str = working_directory + project_name + "_execution.log"
    log_format :str = '%(asctime)s [%(name)s] [%(levelname)s] %(message)s'
    log_dateformat :str = '%Y-%m-%d %H:%M:%S'
    log_loglevel = logging.DEBUG
    log = logging.getLogger(project_name)

    name_of_vm_to_analyse :str = "M118_A"
    user_of_vm_to_analyse :str = "Marius"
    password_of_vm_to_analyse :str = ""
    snapshot_name_for_initial_state_of_vm_to_analyse :str = "initial"

    amount_of_executions_per_action = 3
    actions = [
        Action("Special:WaitUntilUserContinues:install program", "01_InstallProgram", [], snapshot_name_for_initial_state_of_vm_to_analyse, False), 
        Action("Special:WaitUntilUserContinues:start program", "02_StartProgram", [], "prepared_01_after_action1_program_installed", False),
        Action("Special:WaitUntilUserContinues:login to program", "03_LoginToProgram", [], "prepared_02_after_action2_program_started", False),
        Action("Special:WaitUntilUserContinues:lock program", "04_LockProgram", [], "prepared_03_after_action3_logged_in", False),
        Action("Special:WaitUntilUserContinues:uninstall program", "05_UninstallProgram", [], "prepared_04_after_action3_logged_in_and_closed_program", False),
    ]
    
    path_of_init_raw :str = working_directory
    folder_for_idiff_files :str = working_directory + "idiff\\"
    shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference :str = working_directory + "shared\\"


    name_of_vm_which_has_idifference :str = "ST_fiwalk"
    user_of_vm_which_has_idifference :str = "fiwalk"
    password_of_which_has_idifference :str = "password"
    path_of_python3_in_vm_which_has_idifference :str = "/usr/bin/python3"
    path_of_difference_in_vm_which_has_idifference :str = "home/" + user_of_vm_which_has_idifference + "/dfxml-master/python/idifference2.py"

    overwrite_existing_files_and_snapshots :bool = False
    generate_init_raw :bool = True
    overwrite_existing_init_raw :bool = False
    name_of_shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference :str = "sharepoint"
    vboxmanage_executable :str = "C:/Program Files/Oracle/VirtualBox/VBoxManage.exe"
    noise_recording_time_in_seconds : int = 300 #Recommended value: 300
    clear_logfile_before_execution :bool = True
    delete_trace_image_after_analysis :bool = False
    create_snapshots_after_action_execution :bool = True
    prefix_of_snapshotnames_of_actions :str = "fdfe_snapshot"

def get_vm_state(configuration: Configuration, vm_name: str):
    return re.compile("VMState=\"(.*)\"").search(subprocess.check_output("\"" + configuration.vboxmanage_executable + "\" " + "showvminfo " + vm_name + " --machinereadable").decode()).group(1)

def start_program(configuration: Configuration, executable_with_full_path: str, argument: str, waiting_time_in_seconds_after_execution:int=0, title=""):
    if(not title == ""):
        configuration.log.info(title + ":")
    configuration.log.debug("Start " + executable_with_full_path + " " + argument)
    arguments = list()
    arguments.insert(len(arguments), executable_with_full_path)
    for argument_without_whitespace in argument.split():
        arguments.insert(len(arguments),argument_without_whitespace)
    process = subprocess.Popen(arguments)
    process.wait()
    time.sleep(waiting_time_in_seconds_after_execution)
def ensure_vm_which_has_idifference_has_shared_folder(configuration: Configuration):
    if(not vm_which_has_idifference_has_shared_folder(configuration)):
        start_program(configuration, configuration.vboxmanage_executable,"sharedfolder add " + configuration.name_of_vm_which_has_idifference + " --name " + configuration.name_of_shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + " -hostpath " + configuration.shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + " -automount")
def vm_which_has_idifference_has_shared_folder(configuration):
    return configuration.name_of_shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference in get_shared_folders_of_vm(configuration,configuration.name_of_vm_which_has_idifference)

def get_shared_folders_of_vm(configuration,name_of_vm):
    output = subprocess.check_output("\"" + configuration.vboxmanage_executable + "\" " + "showvminfo " + name_of_vm).decode("utf-8").strip()
    splitted = output.splitlines()
    isInSharedFolder = False
    result = []
    for line in splitted:
        if isInSharedFolder:
            lineToAnalyse = line.strip()
            if(lineToAnalyse == ""):
                pass
            elif (lineToAnalyse.startswith("Name:")):
                result.append(lineToAnalyse.split(" ")[1][1:][:-2])
            else:
                isInSharedFolder = False
        if line == "Shared folders:":
            isInSharedFolder = True
    return result
def remove_shared_folder_from_vm_which_has_idifference(configuration: Configuration):
    start_program(configuration, configuration.vboxmanage_executable, "sharedfolder remove " + configuration.name_of_vm_which_has_idifference + " --name " + configuration.name_of_shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference)

def execute_program_in_vm(configuration:Configuration,name_of_vm: str,executable_file_with_path: str, username: str, password: str, waiting_time_in_seconds_after_execution:int, arguments):
    if(len(arguments) == 0):
       argument = " -- " + " ".join(map(lambda concrete_argument: "\"" + concrete_argument + "\"",arguments))
    else:
       argument = ""
    start_program(configuration, configuration.vboxmanage_executable, "guestcontrol " + name_of_vm + " run --exe " + executable_file_with_path + " --username " + username + " --password " + password + argument,waiting_time_in_seconds_after_execution)

def ensure_vm_is_running(name_of_vm: str, configuration: Configuration, use_gui=True):
    if get_vm_state(configuration, name_of_vm) != "running":
        if use_gui:
            gui_argument = "gui"
        else:
            gui_argument = "headless"
        start_program(configuration, configuration.vboxmanage_executable,"startvm " + name_of_vm + " -type " + gui_argument, 5)

def ensure_vm_is_shutdown(name_of_vm: str, configuration:Configuration):
    if get_vm_state(configuration, name_of_vm) == "running":
        start_program(configuration, configuration.vboxmanage_executable,"controlvm " + name_of_vm + " poweroff", 5)

def ensure_vm_is_in_save_state(name_of_vm: str, configuration:Configuration):
    if get_vm_state(configuration, name_of_vm) == "running":
        start_program(configuration,configuration.vboxmanage_executable,"controlvm " + name_of_vm + " savestate", 5)

def continue_vm(configuration:Configuration, use_gui=True):
    ensure_vm_is_running(configuration.name_of_vm_to_analyse, configuration, use_gui)

def execute_action_in_vm(action,configuration:Configuration):
    execute_program_in_vm(configuration, configuration.name_of_vm_to_analyse, action.name, configuration.user_of_vm_to_analyse, configuration.password_of_vm_to_analyse, 5, action.argument)

def save_state_of_vm(name_of_vm: str,configuration: Configuration):
    ensure_vm_is_in_save_state(name_of_vm,configuration)
def create_snapshot(configuration:Configuration, name_of_vm: str, snapshot_name: str):
    start_program(configuration, configuration.vboxmanage_executable,"snapshot " + name_of_vm + " take " + snapshot_name, 5)
def ensure_snapshot_does_not_exist(configuration:Configuration,name_of_vm: str, name_of_snapshot: str):
    if snapshot_exists(configuration,name_of_vm, name_of_snapshot):
        delete_snapshot(configuration,name_of_vm, name_of_snapshot)
def snapshot_exists(configuration:Configuration, name_of_vm: str, name_of_snapshot: str):
   output = subprocess.check_output("\"" + configuration.vboxmanage_executable + "\" " + "snapshot " + name_of_vm + " list").decode("utf-8").strip()
   splitted = output.splitlines()
   for line in splitted:
       if(line[6:].startswith(name_of_snapshot)):
           return True
   return False
def delete_snapshot(configuration:Configuration,name_of_vm: str, name_of_snapshot: str):
    start_program(configuration, configuration.vboxmanage_executable,"snapshot " + name_of_vm + " delete " + name_of_snapshot, 5)

def get_hdd_uuid(configuration: Configuration, vm_name:str):
        output = subprocess.check_output("\"" + configuration.vboxmanage_executable + "\" " + "showvminfo " + vm_name + " --machinereadable").decode()
        return re.compile("\"SATA-ImageUUID-0-0\"=\"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\"").search(output).group(1)
