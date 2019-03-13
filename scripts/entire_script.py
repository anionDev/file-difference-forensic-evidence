import shared_utilities
import ge
import pe
import me
import ce
import logging
import os

def calculate_evidences():
    configuration = shared_utilities.Configuration()
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
    if os.path.isfile(configuration.log_file) & configuration.clear_logfile_before_execution:
        os.remove(configuration.log_file)
    for executionStep in executionSteps:
        print("------------------------------------------------------------")
        print("Start " + executionStep.get_name())
        executionStep.execute(configuration)
        print("Finished " + executionStep.get_name())
    print("------------------------------------------------------------")
    print("Finished")

calculate_evidences()