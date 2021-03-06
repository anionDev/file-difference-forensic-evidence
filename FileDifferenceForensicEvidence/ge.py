import subprocess
import os
import time
from utilities import Configuration
from utilities import Action
from utilities import MergeActionObject
import shutil
import utilities
import traceback
import uuid
import copy

def get_name():
    return "Generate evidences"

def execute(configuration: Configuration):
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
        utilities.start_program(configuration, configuration.vboxmanage_executable, "clonemedium disk " + utilities.get_hdd_uuid(configuration,configuration.name_of_vm_to_analyse) + " --format RAW " + name,0,"Clone medium (Create raw-file with traces for " + action.id + ")")
        utilities.calculate_sha2_of_file(configuration, name)

    def restore_snapshot(snapshot_name:str):
        utilities.start_program(configuration,configuration.vboxmanage_executable, "snapshot " + configuration.name_of_vm_to_analyse + " restore " + snapshot_name, 5, "Restore original state of vm")
    def get_pe_file_for_action(action,iteration_number):
        return configuration.working_directory + "pe\\" + to_action_name_string(action,iteration_number) + ".pe"
    def execute_idifference_for_action(action:Action):
        action.result_idiff_file = configuration.folder_for_idiff_files + to_action_name_string(action,action.iteration_number) + ".idiff"
        if(configuration.overwrite_existing_files_and_snapshots or not os.path.exists(action.result_idiff_file)):
            configuration.log.info("Start idiff generation for action " + action.id + " from iteration " + str(action.iteration_number))
            execute_idifference("/media/sf_" + configuration.name_of_shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + "/" + action.name_of_init_raw_file,
                                "/media/sf_" + configuration.name_of_shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + "/" + action.name_of_result_raw_file,
                                action.result_idiff_file)
            if(configuration.delete_trace_image_after_analysis):
                os.remove(configuration.shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + action.name_of_result_raw_file)
        utilities.calculate_sha2_of_file(configuration,action.result_idiff_file)

    def execute_idifference(raw_file_1:str,raw_file_2:str,result_file:str):
        utilities.ensure_vm_is_running(configuration.name_of_vm_which_has_idifference,configuration,True)
        configuration.log("Execute idifference with input1='" + raw_file_1 + "', input2='" + raw_file_2 + "', output='" + result_file + "'")
        utilities.calculate_sha2_of_file(configuration,raw_file_1)
        utilities.calculate_sha2_of_file(configuration,raw_file_2)
        idifference2_command = "\"" + configuration.vboxmanage_executable + "\" " + "guestcontrol " + configuration.name_of_vm_which_has_idifference + " run --exe " + configuration.path_of_python3_in_vm_which_has_idifference + " --username " + configuration.user_of_vm_which_has_idifference + " --password " + configuration.password_of_which_has_idifference + " --putenv PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin --wait-stdout --wait-stderr -- arg " + configuration.path_of_difference_in_vm_which_has_idifference + " " + raw_file_1 + " " + raw_file_2
        idifference2_output = subprocess.check_output(idifference2_command).decode()
        file = open(result_file, "w")
        file.write(idifference2_output)
        file.close()

    def generate_evidence(action:Action,iteration_number:int):
        action.iteration_number = iteration_number
        action.name_of_result_raw_file = to_action_name_string(action,action.iteration_number) + ".raw"
        configuration.executed_action_instances_for_pe.append(action)
        result_file_name = configuration.shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + action.name_of_result_raw_file
        if(configuration.overwrite_existing_files_and_snapshots or not os.path.exists(result_file_name)):
            configuration.log.info("Start evidence generation for action " + action.id + " in iteration " + str(action.iteration_number))
            try:
                restore_snapshot(action.name_of_based_snapshot)
                if (action.name.lower().startswith("Special:".lower())):
                    if(action.name.lower().startswith("Special:WaitUntilUserContinues:".lower())):
                        input("Next action in the vm: " + action.id + " ('" + action.name.split(":")[2] + "'). Please press enter to continue the vm and then execute the action.")
                        utilities.continue_vm(configuration, True)
                        input("Wait for execution of manual action " + action.id + " ('" + action.name.split(":")[2] + "') in the vm. Please press enter when this action is finished to continue generating evidences.")
                    elif action.name.lower().startswith("Special:Noise:".lower()):
                        utilities.continue_vm(configuration, False)
                        time.sleep(configuration.noise_recording_time_in_seconds)
                        configuration.log.info("Recording noise... (Waiting " + str(configuration.noise_recording_time_in_seconds) + " seconds)")
                    else:
                        raise Exception("Unknown action")
                else:
                    configuration.log.info("Execute action " + action.id + " in vm...")
                    utilities.continue_vm(configuration, False)
                    utilities.execute_action_in_vm(action, configuration)
                utilities.save_state_of_vm(configuration.name_of_vm_to_analyse, configuration)
                if(configuration.create_snapshots_after_action_execution):
                    snapshot_name = configuration.prefix_of_snapshotnames_of_actions + action.id + "." + str(iteration_number)
                    if (configuration.overwrite_existing_files_and_snapshots):
                        utilities.ensure_snapshot_does_not_exist(configuration,configuration.name_of_vm_to_analyse, snapshot_name)
                    utilities.create_snapshot(configuration,configuration.name_of_vm_to_analyse, snapshot_name)
                configuration.log.debug("Create trace image...")
                create_trace_image(action,iteration_number,result_file_name)
            except Exception as exception_object:
                configuration.log.error("Exception occurred while generating evidence  for action " + action.id + " in iteration " + str(iteration_number) + ":")
                configuration.log.error(exception_object, exc_info=True)
                raise
            finally:
                utilities.save_state_of_vm(configuration.name_of_vm_to_analyse,configuration)
            configuration.log.info("Evidence generation for action " + action.id + " in iteration " + str(iteration_number) + " finished")

    def generate_evidence_full():
        for action in configuration.actions:
            generate_noise_and_generate_new_init_raw_file_if_desired(action)
            action.noise_action.result_pe_file = get_pe_file_for_action(action.noise_action,0)
            merge_action = MergeActionObject(action)
            for iteration_number in range(1, configuration.amount_of_executions_per_action + 1):
                action.result_pe_file = get_pe_file_for_action(action,iteration_number)
                copied_action = copy.copy(action)
                copied_action.uuid = uuid.uuid4()
                generate_evidence(copied_action, iteration_number)                
                merge_action.action_instances.append(copied_action)
            configuration.executed_action_instances_merge_list.append(merge_action)

    def generate_noise_and_generate_new_init_raw_file_if_desired(action:Action):
        if configuration.generate_init_raw:
            init_raw_file = configuration.shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + action.name_of_init_raw_file
            if(os.path.isfile(init_raw_file)):
                if(configuration.overwrite_existing_init_raw):
                    os.remove(init_raw_file)
                    generate_new_init_raw_file(action)
            else:
                generate_new_init_raw_file(action)
        generate_evidence(action.noise_action, 0)

    def generate_new_init_raw_file(action:Action):
        restore_snapshot(action.name_of_based_snapshot)
        init_raw_file_on_host_for_sharing_files_with_vm_which_has_idifference = configuration.shared_folder_on_host_for_sharing_files_with_vm_which_has_idifference + action.name_of_init_raw_file
        utilities.start_program(configuration,configuration.vboxmanage_executable, "clonemedium disk " + utilities.get_hdd_uuid(configuration, configuration.name_of_vm_to_analyse) + " --format RAW " + init_raw_file_on_host_for_sharing_files_with_vm_which_has_idifference, 1, "Clone medium (Create raw-file of initial state)")
        utilities.calculate_sha2_of_file(configuration, init_raw_file_on_host_for_sharing_files_with_vm_which_has_idifference)

    def generate_idiff_files():
        if not os.path.exists(configuration.folder_for_idiff_files):
            os.makedirs(configuration.folder_for_idiff_files)
        for executed_action in configuration.executed_action_instances_for_pe:
            try:
                execute_idifference_for_action(executed_action)
            except Exception as exception:
                configuration.log.warning("Exception occurred in execute_idifference_for_action(" + executed_action.id + ", " + str(executed_action.iteration_number) + ")")
                configuration.log.warning(exception, exc_info=True)
                raise            
    try:
        utilities.ensure_vm_which_has_idifference_has_shared_folder(configuration)        
        utilities.ensure_vm_is_shutdown(configuration.name_of_vm_which_has_idifference,configuration)
        generate_evidence_full()
        generate_idiff_files()
    except Exception as exception:
        configuration.log.error("Exception occurred in ge.py:")
        configuration.log.error(exception, exc_info=True)
        raise
    finally:
        utilities.ensure_vm_is_shutdown(configuration.name_of_vm_which_has_idifference, configuration)
        utilities.remove_shared_folder_from_vm_which_has_idifference(configuration)
