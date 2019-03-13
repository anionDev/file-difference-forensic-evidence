import shared_utilities
import ge
import pe
import me
import ce
import logging


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
    for executionStep in executionSteps:
        print("------------------------------------------------------------")
        print("Start " + executionStep.get_name())
        executionStep.execute(configuration)
        print("Finished " + executionStep.get_name())
    print("------------------------------------------------------------")
    print("Finished")

calculate_evidences()