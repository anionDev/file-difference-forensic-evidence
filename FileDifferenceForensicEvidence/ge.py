import subprocess
import os
import time
from shared_utilities import Configuration
from shared_utilities import Action
import shutil
import shared_utilities
import traceback

def get_name():
    return "Generate evidences"

def execute(configuration: Configuration):
    if os.path.exists(configuration.folder_for_idiff_files):
        shutil.rmtree(configuration.folder_for_idiff_files)
    os.makedirs(configuration.folder_for_idiff_files)
    init_raw_file = configuration.path_of_init_raw + configuration.TODO_name_of_init_raw_file
    init_raw_file_on_host_for_sharing_files_with_vm_which_has_idifference = configuration.shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + configuration.TODO_name_of_init_raw_file
    executed_actions = []
    if not os.path.exists(configuration.shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference):
        os.makedirs(configuration.shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference)
    if not os.path.exists(configuration.path_of_init_raw):
        os.makedirs(configuration.path_of_init_raw)

    def to_action_name_string(action:Action, iteration_number:int):
        if iteration_number == 0:
            return action.id
        else:
            return action.id + "." + str(iteration_number)
               
    def create_trace_image(action:Action, iteration_number:int, name:str):
        shared_utilities.start_program(configuration, configuration.vboxmanage_executable, "clonemedium disk " + shared_utilities.get_hdd_uuid(configuration,configuration.name_of_vm_to_analyse) + " --format RAW " + name,0,"Clone medium (Create raw-file with traces for " + action.id + ")")

    def restore_snapshot(snapshot_name:str):
        shared_utilities.start_program(configuration,configuration.vboxmanage_executable, "snapshot " + configuration.name_of_vm_to_analyse + " restore " + snapshot_name, 5, "Restore original state of vm")

    def execute_idifference_for_action(action:Action,iteration_number:int):
        shared_utilities.ensure_vm_is_running(configuration.name_of_vm_which_has_idifference,configuration, False)
        execute_idifference("/media/sf_" + configuration.name_of_shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + "/" + configuration.TODO_name_of_init_raw_file,"/media/sf_" + configuration.name_of_shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + "/" + to_action_name_string(action,iteration_number) + ".raw",configuration.folder_for_idiff_files + to_action_name_string(action,iteration_number) + ".idiff")

    def execute_idifference(raw_file_1:str,raw_file_2:str,result_file:str):
        idifference2_command = "\"" + configuration.vboxmanage_executable + "\" " + "guestcontrol " + configuration.name_of_vm_which_has_idifference + " run --exe " + configuration.path_of_python3_in_vm_which_has_idifference + " --username " + configuration.user_of_vm_which_has_idifference + " --password " + configuration.password_of_which_has_idifference + " --putenv PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin --wait-stdout --wait-stderr -- arg " + configuration.path_of_difference_in_vm_which_has_idifference + " " + raw_file_1 + " " + raw_file_2
        idifference2_output = subprocess.check_output(idifference2_command).decode()
        file = open(result_file, "w")
        file.write(idifference2_output)
        file.close()

    def delete_trace_image_if_desired(action:Action, iteration_number:int):
        if(delete_trace_image_after_analysis):
            os.remove(configuration.shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + to_action_name_string(action,iteration_number) + ".raw")

    def finalize_generate_evidence():
        shared_utilities.save_state_of_vm(configuration.name_of_vm_to_analyse,configuration)

    def generate_evidence(action:Action,iteration_number:int):
        result_file_name = configuration.shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + to_action_name_string(action,iteration_number) + ".raw"
        if(configuration.overwrite_existing_files_and_snapshots or not os.path.exists(result_file_name)):
            configuration.log.info("Start evidence generation for action " + action.id + " in iteration " + str(iteration_number))
            try:
                restore_snapshot(action.name_of_based_snapshot)
                if (action.name.lower().startswith("Special:".lower())):
                    if(action.name.lower().startswith("Special:WaitUntilUserContinues:".lower())):
                        input("Next action in the vm: " + action.id + " ('" + action.name.split(":")[2] + "'). Please press enter to continue the vm and then execute the action.")
                        shared_utilities.continue_vm(configuration, True)
                        input("Wait for execution of manual action " + action.id + " ('" + action.name.split(":")[2] + "') in the vm. Please press enter if this action is finished to continue generating evidences.")
                    elif action.name.lower().startswith("Special:Noise:".lower()):
                        configuration.log.info("Recording noise... (Waiting " + str(configuration.noise_recording_time_in_seconds) + " seconds)")
                        shared_utilities.continue_vm(configuratio, False)
                        time.sleep(configuration.noise_recording_time_in_seconds)
                    else:
                        raise Exception("Unknown action")
                else:
                    shared_utilities.continue_vm(configuration, False)
                    shared_utilities.execute_action_in_vm(action, configuration)
                shared_utilities.save_state_of_vm(configuration.name_of_vm_to_analyse, configuration)
                if(configuration.create_snapshots_after_action_execution):
                    snapshot_name = configuration.prefix_of_snapshotnames_of_actions + "_" + action.id + "_" + str(iteration_number)
                    if (configuration.overwrite_existing_files_and_snapshots):
                        shared_utilities.ensure_snapshot_does_not_exist(configuration,configuration.name_of_vm_to_analyse, snapshot_name)
                    shared_utilities.create_snapshot(configuration,configuration.name_of_vm_to_analyse, snapshot_name)
                create_trace_image(action,iteration_number,result_file_name)
                executed_actions.append([action,iteration_number])
            except Exception as exception_object:
                configuration.log.error("Exception occurred while generating evidence  for action " + action.id + " in iteration " + str(iteration_number) + ":")
                configuration.log.error(exception_object, exc_info=True)
            finally:
                finalize_generate_evidence()
            configuration.log.info("Evidence generation for action " + action.id + " in iteration " + str(iteration_number) + " finished")

    def generate_evidence_full():
        for action in configuration.actions:
            generate_evidence(["Special:Noise:", action.id + "_noise",[] , action.name_of_based_snapshot],0)
            for iteration_number in range(1, configuration.amount_of_executions_per_action + 1):
                generate_evidence(action, iteration_number)

    def generate_new_init_raw_file():
        restore_snapshot(configuration.snapshot_name_for_initial_state_of_vm_to_analyse)
        shared_utilities.start_program(configuration,configuration.vboxmanage_executable, "clonemedium disk " + shared_utilities.get_hdd_uuid(configuration, configuration.name_of_vm_to_analyse) + " --format RAW " + init_raw_file, 1, "Clone medium (Create raw-file of initial state)")
        if os.path.exists(init_raw_file_on_host_for_sharing_files_with_vm_which_has_idifference) and configuration.overwrite_existing_files_and_snapshots:
            os.remove(init_raw_file_on_host_for_sharing_files_with_vm_which_has_idifference)
        shutil.copy(init_raw_file, init_raw_file_on_host_for_sharing_files_with_vm_which_has_idifference)

    def generate_new_init_raw_file_if_desired():
        if configuration.generate_init_raw:
            if(os.path.isfile(init_raw_file)):
                if(configuration.overwrite_existing_init_raw):
                    os.remove(init_raw_file)
                    generate_new_init_raw_file()
            else:
                generate_new_init_raw_file()
    def generate_idiff_files():
        for executed_action in executed_actions:
            execute_idifference_for_action(executed_action.name, executed_action.id)
            delete_trace_image_if_desired(executed_action.name, executed_action.id)
    try:
        generate_new_init_raw_file_if_desired()
        shared_utilities.ensure_vm_which_has_idifference_has_shared_folder(configuration)
        shared_utilities.ensure_vm_is_shutdown(configuration.name_of_vm_which_has_idifference, configuration)
        generate_evidence_full()
        generate_idiff_files()
    except Exception as exception:
        configuration.log.error("Exception occurred in ge.py:")
        configuration.log.error(exception, exc_info=True)
    finally:
        shared_utilities.ensure_vm_is_shutdown(configuration.name_of_vm_which_has_idifference, configuration)
        shared_utilities.remove_shared_folder_from_vm_which_has_idifference(configuration)
