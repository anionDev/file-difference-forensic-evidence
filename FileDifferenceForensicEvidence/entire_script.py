import shared_utilities
import ge
import pe
import me
import ce
from shared_utilities import Configuration
import logging
import os

def calculate_evidences():
    configuration : Configuration = shared_utilities.Configuration()
    if configuration.clear_logfile_before_execution and os.path.isfile(configuration.log_file):
        open(configuration.log_file, 'w').close()
    logging.basicConfig(filename=configuration.log_file,
                        filemode=configuration.log_filemode,
                        format=configuration.log_format,
                        datefmt=configuration.log_dateformat,
                        level=configuration.log_loglevel)
    executionSteps = [
        ge,
        pe,
        me,
        ce,
    ]
    print("Started")
    for execution_step in executionSteps:
        print("------------------------------------------------------------")
        print("Start " + execution_step.get_name())
        execution_step.execute(configuration)
        print("Finished " + execution_step.get_name())
    print("------------------------------------------------------------")
    print("Finished")

calculate_evidences()