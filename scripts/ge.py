#---------------------
#imports:
import subprocess
import shlex
import os
import time
import argparse
import sys
import shutil
import re
import logging
#---------------------
#configuration:
use_command_line_argument_for_path_of_init_raw=True
actions = ["C:\\actions\\a.exe", "C:\\actions\\b.exe", "C:\\actions\\c.exe", "C:\\actions\\d.exe", "C:\\actions\\e.exe"]
name_of_noise_action="noise"
amount_of_executions_per_action=3
if(use_command_line_argument_for_path_of_init_raw):
    path_of_init_raw=' '.join(sys.argv[1:])
else:
    path_of_init_raw="C:\\temp\\M105\\initraw\\"
folder_for_idiff_files=os.path.dirname(os.path.abspath(__file__)) + "\\idiff\\"
shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference="C:\\temp\\M105\\shared\\"

name_of_vm_to_analyse= "win7-x86"
user_of_vm_to_analyse="win7"
password_of_vm_to_analyse="win7"
snapshot_name_for_initial_state_of_vm_to_analyse= "analysis_base"

name_of_vm_which_has_idifference= "ST_fiwalk"
user_of_vm_which_has_idifference="fiwalk"
password_of_which_has_idifference="fiwalk"

generate_init_raw=False
name_of_shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference="sharepoint"
log_file = os.path.dirname(os.path.abspath(__file__)) + "log.log"
vboxmanage_executable= "C:/Program Files/Oracle/VirtualBox/VBoxManage.exe"
noise_recordding_time_in_seconds=60
name_of_init_raw_file="init.raw"
name_of_noise_raw_file=name_of_noise_action+".raw"
generate_noise=False
clear_logfile_before_execution=False
loglevel=logging.DEBUG
generate_only_single_idiff_file=False
action_if_generate_only_single_idiff_file="a"
iteration_number_if_generate_only_single_idiff_file=1
delete_trace_image_after_analysis=False
use_gui_mode_for_vm=True
#---------------------
#implementation:
init_raw_file=path_of_init_raw+name_of_init_raw_file
init_war_file_on_host_for_sharing_files_with_vm_which_has_idifference=shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference+name_of_init_raw_file
if os.path.isfile(log_file) & clear_logfile_before_execution:
    os.remove(log_file)
if not os.path.exists(shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference):
    os.makedirs(shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference)
if not os.path.exists(folder_for_idiff_files):
    os.makedirs(folder_for_idiff_files)
if not os.path.exists(path_of_init_raw):
    os.makedirs(path_of_init_raw)
logging.basicConfig(filename=log_file,
                            filemode='a',
                            format='%(asctime)s.%(msecs)03d %(name)s [%(levelname)s] %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=loglevel)
log = logging.getLogger('M105')
def get_vm_state(vm_name):
    return re.compile("VMState=\"(.*)\"").search(subprocess.check_output("\""+vboxmanage_executable+"\" " + "showvminfo " + vm_name + " --machinereadable").decode()).group(1)

def start_program(executable_with_full_path, argument,waiting_time_in_seconds_after_execution=1):
    log.debug("Start " + executable_with_full_path + " " + argument)
    arguments=list()
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
    start_program(vboxmanage_executable, "guestcontrol " +name_of_vm+" run --exe "+executable_file_with_path+" --username "+username+" --password "+password,waiting_time_in_seconds_after_execution)

def ensure_vm_is_running(name_of_vm):
    if get_vm_state(name_of_vm)!="running":
        if use_gui_mode_for_vm:
            gui_argument="gui"
        else:
            gui_argument="headless"
        start_program(vboxmanage_executable,"startvm "+name_of_vm+" -type "+gui_argument,5)

def ensure_vm_is_shutdown(name_of_vm):
    if get_vm_state(name_of_vm)=="running":
        start_program(vboxmanage_executable,"controlvm "+name_of_vm+" poweroff",5)

def ensure_vm_is_in_save_state(name_of_vm):
    if get_vm_state(name_of_vm)=="running":
        start_program(vboxmanage_executable,"controlvm "+name_of_vm+" savestate",5)

def to_action_name_string(action,iteration_number):
    if iteration_number == 0:
        return action
    else:
        return action + "." + str(iteration_number)

def continue_vm():
    ensure_vm_is_running(name_of_vm_to_analyse)

def execute_action_in_vm(action):
    execute_program_in_vm(name_of_vm_to_analyse,action,user_of_vm_to_analyse,password_of_vm_to_analyse,5)

def save_state_of_vm(name_of_vm):
    ensure_vm_is_in_save_state(name_of_vm)

def start_program_with_parameter_list(executable_with_full_path, arguments, waiting_time_in_seconds_after_execution=1):
    log.debug("Start " + executable_with_full_path + " " + " ".join(arguments))
    argument_list=list()
    argument_list.append(executable_with_full_path)
    argument_list.extend(arguments)
    process = subprocess.Popen(argument_list)
    process.wait()
    time.sleep(waiting_time_in_seconds_after_execution)

def get_hdd_uuid(vm_name):
    antwort_uuid = subprocess.check_output("\""+vboxmanage_executable+"\" " + "showvminfo " + vm_name + " --machinereadable").decode()
    return re.compile("\"SATA-ImageUUID-0-0\"=\"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\"").search(antwort_uuid).group(1)

def create_trace_image(action, iteration_number):
    start_program(vboxmanage_executable,"clonemedium disk " + get_hdd_uuid(name_of_vm_to_analyse) + " --format RAW " + shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + to_action_name_string(action,iteration_number) + ".raw")

def restore_original_image():
    start_program(vboxmanage_executable, "snapshot " + name_of_vm_to_analyse + " restore "+ snapshot_name_for_initial_state_of_vm_to_analyse,5)

def execute_idifference_for_action(action,iteration_number):
    ensure_vm_is_running(name_of_vm_which_has_idifference)
    execute_idifference("/media/sf_"+name_of_shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference+"/"+name_of_init_raw_file,"/media/sf_"+name_of_shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference+"/"+to_action_name_string(action,iteration_number)+".raw",folder_for_idiff_files+ to_action_name_string(action,iteration_number)+".idiff")

def execute_idifference(raw_file_1,raw_file_2,result_file):
    idifference2_command = "\""+vboxmanage_executable+"\" " + "guestcontrol "+name_of_vm_which_has_idifference+" run --exe /usr/bin/python3.4 --username "+user_of_vm_which_has_idifference+" --password "+password_of_which_has_idifference+" --putenv PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin --wait-stdout --wait-stderr -- arg home/fiwalk/dfxml-master/python/idifference2.py " +  raw_file_1+" "+raw_file_2
    idifference2_output = subprocess.check_output(idifference2_command).decode()
    file = open(result_file, "w")
    file.write(idifference2_output)
    file.close()

def delete_trace_image_if_desired(action,iteration_number):
    if(delete_trace_image_after_analysis):
        os.remove(shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + to_action_name_string(action,iteration_number) + ".raw")

def prepare_generate_evidence():
    restore_original_image()

def finalize_generate_evidence():
    save_state_of_vm(name_of_vm_to_analyse)

def generate_evidence(action,iteration_number):
    log.info("Start evidence generation for action " + action + " in iteration " + str(iteration_number))
    try:
        prepare_generate_evidence()
        continue_vm()
        if(action==name_of_noise_action):
            pass
            time.sleep(noise_recordding_time_in_seconds)
        else:
            execute_action_in_vm(action)
        save_state_of_vm(name_of_vm_to_analyse)
        create_trace_image(action,iteration_number)
        restore_original_image()
        execute_idifference_for_action(action,iteration_number)
        delete_trace_image_if_desired(action,iteration_number)
    except Exception as exception:
        log.error("Exception occurred while generating evidence  for action "+action+" in iteration "+str(iteration_number) + ":")
        logging.error(exception, exc_info=True)
    finally:
        finalize_generate_evidence()
    log.info("Evidence generation for action "+action+" in iteration "+str(iteration_number)+" finished")

def generate_evidence_full():
    for action in actions:
         for iteration_number in range(1, amount_of_executions_per_action + 1):
             generate_evidence(action,iteration_number)
def generate_new_init_raw_file_if_desired():
    if generate_init_raw:
        if os.path.isfile(init_raw_file):
            os.remove(init_raw_file)
        restore_original_image()
        start_program(vboxmanage_executable,"clonemedium disk " + get_hdd_uuid(name_of_vm_to_analyse) + " --format RAW " + init_raw_file )
        if os.path.isfile(init_war_file_on_host_for_sharing_files_with_vm_which_has_idifference):
            os.remove(init_war_file_on_host_for_sharing_files_with_vm_which_has_idifference)
        shutil.copy(init_raw_file, init_war_file_on_host_for_sharing_files_with_vm_which_has_idifference)

log.info("---------------------")
log.info("Start ge.py")
try:
    generate_new_init_raw_file_if_desired()
    add_shared_folder_for_vm_which_has_idifference()
    ensure_vm_is_shutdown(name_of_vm_which_has_idifference)
    if generate_noise:
        generate_evidence(name_of_noise_action,0)
    if generate_only_single_idiff_file:
        generate_evidence(action_if_generate_only_single_idiff_file,iteration_number_if_generate_only_single_idiff_file)
    else:
        generate_evidence_full()
except Exception as exception:
    log.error("Exception occurred in ge.py:")
    logging.error(exception, exc_info=True)
finally:
    ensure_vm_is_shutdown(name_of_vm_which_has_idifference)
    remove_shared_folder_from_vm_which_has_idifference()
log.info("ge.py finished")
