import json
import pickle
import logging
import os
class Configuration:
    current_folder = os.path.dirname(os.path.abspath(__file__))
    log_file = "log.txt"
    log = logging.getLogger('Calculate evidences')
    amount_of_executions_per_action = 3
    actions = ["C:\\actions\\a.exe", 
        "C:\\actions\\b.exe", 
        "C:\\actions\\c.exe", 
        "C:\\actions\\d.exe", 
        "C:\\actions\\e.exe"],
    name_of_noise_action = "noise"
    name_of_noise_idiff_file = "noise.idiff"
    path_of_init_raw = "C:\\temp\\M105\\initraw\\"
    folder_for_idiff_files = os.path.dirname(os.path.abspath(__file__)) + "\\idiff\\"
    shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference = "C:\\temp\\M105\\shared\\"

    name_of_vm_to_analyse = "win7-x86"
    user_of_vm_to_analyse = "win7"
    password_of_vm_to_analyse = "win7"
    snapshot_name_for_initial_state_of_vm_to_analyse = "analysis_base"

    name_of_vm_which_has_idifference = "ST_fiwalk"
    user_of_vm_which_has_idifference = "fiwalk"
    password_of_which_has_idifference = "fiwalk"

    generate_init_raw = False
    name_of_shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference = "sharepoint"
    vboxmanage_executable = "C:/Program Files/Oracle/VirtualBox/VBoxManage.exe"
    noise_recordding_time_in_seconds = 60
    name_of_init_raw_file = "init.raw"
    name_of_noise_raw_file = name_of_noise_action + ".raw"
    generate_noise = False
    clear_logfile_before_execution = False
    loglevel = logging.DEBUG
    generate_only_single_idiff_file = False
    action_if_generate_only_single_idiff_file = "a"
    iteration_number_if_generate_only_single_idiff_file = 1
    delete_trace_image_after_analysis = False
    use_gui_mode_for_vm = True

def get_vm_state(vm_name):
    return re.compile("VMState=\"(.*)\"").search(subprocess.check_output("\"" + vboxmanage_executable + "\" " + "showvminfo " + vm_name + " --machinereadable").decode()).group(1)

def start_program(executable_with_full_path, argument,waiting_time_in_seconds_after_execution=1):
    log.debug("Start " + executable_with_full_path + " " + argument)
    arguments = list()
    arguments.insert(len(arguments), executable_with_full_path)
    for argument_without_whitespace in argument.split():
        arguments.insert(len(arguments),argument_without_whitespace)
    process = subprocess.Popen(arguments)
    process.wait()
    time.sleep(waiting_time_in_seconds_after_execution)
def add_shared_folder_for_vm_which_has_idifference():
    start_program(vboxmanage_executable,"sharedfolder add " + name_of_vm_which_has_idifference + " --name " + name_of_shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + " -hostpath " + shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + " -automount")

def remove_shared_folder_from_vm_which_has_idifference():
    start_program(vboxmanage_executable, "sharedfolder remove " + name_of_vm_which_has_idifference + " --name " + name_of_shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference)

def execute_program_in_vm(name_of_vm,executable_file_with_path,username, password,waiting_time_in_seconds_after_execution):
    start_program(vboxmanage_executable, "guestcontrol " + name_of_vm + " run --exe " + executable_file_with_path + " --username " + username + " --password " + password,waiting_time_in_seconds_after_execution)

def ensure_vm_is_running(name_of_vm):
    if get_vm_state(name_of_vm) != "running":
        if use_gui_mode_for_vm:
            gui_argument = "gui"
        else:
            gui_argument = "headless"
        start_program(vboxmanage_executable,"startvm " + name_of_vm + " -type " + gui_argument,5)

def ensure_vm_is_shutdown(name_of_vm):
    if get_vm_state(name_of_vm) == "running":
        start_program(vboxmanage_executable,"controlvm " + name_of_vm + " poweroff",5)

def ensure_vm_is_in_save_state(name_of_vm):
    if get_vm_state(name_of_vm) == "running":
        start_program(vboxmanage_executable,"controlvm " + name_of_vm + " savestate",5)

def continue_vm():
    ensure_vm_is_running(name_of_vm_to_analyse)

def execute_action_in_vm(action):
    execute_program_in_vm(name_of_vm_to_analyse,action,user_of_vm_to_analyse,password_of_vm_to_analyse,5)

def save_state_of_vm(name_of_vm):
    ensure_vm_is_in_save_state(name_of_vm)

def start_program_with_parameter_list(executable_with_full_path, arguments, waiting_time_in_seconds_after_execution=1):
    log.debug("Start " + executable_with_full_path + " " + " ".join(arguments))
    argument_list = list()
    argument_list.append(executable_with_full_path)
    argument_list.extend(arguments)
    process = subprocess.Popen(argument_list)
    process.wait()
    time.sleep(waiting_time_in_seconds_after_execution)

def get_hdd_uuid(vm_name):
        antwort_uuid = subprocess.check_output("\"" + vboxmanage_executable + "\" " + "showvminfo " + vm_name + " --machinereadable").decode()
        return re.compile("\"SATA-ImageUUID-0-0\"=\"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\"").search(antwort_uuid).group(1)
