import subprocess
import shlex
import os
import time
import argparse
import sys
import shutil
import re
import logging
import shared_utilities

def get_name():
    return "Generate evidences"

def execute(configuration):
    if os.path.exists(folder_for_idiff_files):
        shutil.rmtree(folder_for_idiff_files)
    os.makedirs(folder_for_idiff_files)
    init_raw_file = configuration.path_of_init_raw + configuration.name_of_init_raw_file
    init_war_file_on_host_for_sharing_files_with_vm_which_has_idifference = configuration.shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + configuration.name_of_init_raw_file
    if not os.path.exists(configuration.shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference):
        os.makedirs(configuration.shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference)
    if not os.path.exists(configuration.path_of_init_raw):
        os.makedirs(configuration.path_of_init_raw)

    def to_action_name_string(action,iteration_number):
        if iteration_number == 0:
            return action[1]
        else:
            return action[1] + "." + str(iteration_number)
               
    def create_trace_image(action, iteration_number):
        shared_utilities.start_program(configuration.vboxmanage_executable,"clonemedium disk " + shared_utilities.get_hdd_uuid(configuration.name_of_vm_to_analyse) + " --format RAW " + configuration.shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + to_action_name_string(action,iteration_number) + ".raw")

    def restore_original_image():
        shared_utilities.start_program(configuration.vboxmanage_executable, "snapshot " + configuration.name_of_vm_to_analyse + " restore " + configuration.snapshot_name_for_initial_state_of_vm_to_analyse,5)

    def execute_idifference_for_action(action,iteration_number):
        ensure_vm_is_running(name_of_vm_which_has_idifference,configuration.use_gui_mode_for_vm,configuration)
        execute_idifference("/media/sf_" + configuration.name_of_shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + "/" + configuration.name_of_init_raw_file,"/media/sf_" + configuration.name_of_shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + "/" + to_action_name_string(action,iteration_number) + ".raw",folder_for_idiff_files + to_action_name_string(action,iteration_number) + ".idiff")

    def execute_idifference(raw_file_1,raw_file_2,result_file):
        idifference2_command = "\"" + configuration.vboxmanage_executable + "\" " + "guestcontrol " + configuration.name_of_vm_which_has_idifference + " run --exe " + configuration.path_of_python3_in_vm_which_has_idifference + " --username " + configuration.user_of_vm_which_has_idifference + " --password " + configuration.password_of_which_has_idifference + " --putenv PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin --wait-stdout --wait-stderr -- arg " + configuration.path_of_difference_in_vm_which_has_idifference + " " + raw_file_1 + " " + raw_file_2
        idifference2_output = subprocess.check_output(idifference2_command).decode()
        file = open(result_file, "w")
        file.write(idifference2_output)
        file.close()

    def delete_trace_image_if_desired(action,iteration_number):
        if(delete_trace_image_after_analysis):
            os.remove(configuration.shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + to_action_name_string(action,iteration_number) + ".raw")

    def prepare_generate_evidence():
        configuration.restore_original_image()

    def finalize_generate_evidence():
        shared_utilities.save_state_of_vm(configuration.name_of_vm_to_analyse,configuration)

    def generate_evidence(action,iteration_number):
        configuration.log.info("Start evidence generation for action " + action[1] + " in iteration " + str(iteration_number))
        try:
            prepare_generate_evidence()
            shared_utilities.continue_vm(configuration)
            if(action[1] == configuration.name_of_noise_action):
                time.sleep(configuration.noise_recording_time_in_seconds)
            else:
                if (action[0].lower().startswith("Special:".lower())):
                    if(action[0].lower().startswith("Special:WaitUntilUserContinues:".lower())):
                        input("Wait for execution of manual action " + action[1] + " ('" + action[0].split(":")[2] + "') in the vm. Please press enter if this action is finished to continue generating evidences.")
                    else:
                        raise Exception("Unknown action") 
                else:
                    shared_utilities.execute_action_in_vm(action,configuration)

            configuration.save_state_of_vm(configuration.name_of_vm_to_analyse,configuration)
            if(configuration.create_snapshots_after_action_execution):
                shared_utilities.create_snapshot(configuration.name_of_vm_to_analyse, "fdfe_snapshot_" + action[1] + "_" + str(iteration_number))
            create_trace_image(action,iteration_number)
            configuration.restore_original_image()
            execute_idifference_for_action(action,iteration_number)
            delete_trace_image_if_desired(action,iteration_number)
        except Exception as exception:
            configuration.log.error("Exception occurred while generating evidence  for action " + action[1] + " in iteration " + str(iteration_number) + ":")
            configuration.log.error(exception, exc_info=True)
        finally:
            finalize_generate_evidence()
        configuration.log.info("Evidence generation for action " + action[1] + " in iteration " + str(iteration_number) + " finished")

    def generate_evidence_full():
        for action in configuration.actions:
             for iteration_number in range(1, configuration.amount_of_executions_per_action + 1):
                 generate_evidence(action,iteration_number)

    def generate_new_init_raw_file_if_desired():
        if generate_init_raw:
            if os.path.isfile(configuration.init_raw_file):
                os.remove(configuration.init_raw_file)
            configuration.restore_original_image()
            shared_utilities.start_program(configuration.vboxmanage_executable,"clonemedium disk " + shared_utilities.get_hdd_uuid(configuration.name_of_vm_to_analyse) + " --format RAW " + configuration.init_raw_file)
            if os.path.isfile(configuration.init_war_file_on_host_for_sharing_files_with_vm_which_has_idifference):
                os.remove(configuration.init_war_file_on_host_for_sharing_files_with_vm_which_has_idifference)
            shutil.copy(configuration.init_raw_file, configuration.init_war_file_on_host_for_sharing_files_with_vm_which_has_idifference)

    try:
        generate_new_init_raw_file_if_desired()
        shared_utilities.add_shared_folder_for_vm_which_has_idifference(configuration)
        shared_utilities.ensure_vm_is_shutdown(configuration.name_of_vm_which_has_idifference,configuration)
        generate_evidence(configuration.name_of_noise_action,0)
        generate_evidence_full()
    except Exception as exception:
        configuration.log.error("Exception occurred in ge.py:")
        configuration.log.error(exception, exc_info=True)
    finally:
        shared_utilities.ensure_vm_is_shutdown(configuration.name_of_vm_which_has_idifference,configuration)
        shared_utilities.remove_shared_folder_from_vm_which_has_idifference(configuration)
