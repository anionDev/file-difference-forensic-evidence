import shared_utilities
import ge
import pe
import me
import ce
from shared_utilities import Configuration
from shared_utilities import Action
import logging
import os
import subprocess
import sys
import ctypes

def calculate_evidences(configuration: Configuration):
    ctypes.windll.kernel32.SetConsoleTitleW("FileDifferenceForensicEvidence: " + configuration.project_name + " (" + configuration.working_directory + ")")
    if not os.path.exists(configuration.working_directory):
        os.makedirs(configuration.working_directory)
    if configuration.clear_logfile_before_execution and os.path.isfile(configuration.log_file):
        open(configuration.log_file, 'w').close()
    logging.basicConfig(format=configuration.log_format,
                        datefmt=configuration.log_dateformat,
                        level=configuration.log_loglevel,
                        handlers=[logging.FileHandler(configuration.log_file), logging.StreamHandler()])
    executionSteps = [ge, pe, me, ce]
    configuration.log.info("Start project " + configuration.project_name)
    for execution_step in executionSteps:
        configuration.log.info("------------------------------------------------------------")
        configuration.log.info("Start " + execution_step.get_name())
        try:
            execution_step.execute(configuration)
        except Exception as exception:
            break
        configuration.log.info("Finished " + execution_step.get_name())
    configuration.log.info("------------------------------------------------------------")
    configuration.log.info("Finished project " + configuration.project_name)

calculate_evidences(shared_utilities.Configuration())