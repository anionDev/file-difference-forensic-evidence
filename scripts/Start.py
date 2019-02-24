import ge
import pe
import me
import ce
import Utilities

default_configuration_file="configuration.txt"

def create_configurationFile():
    Utilities.createConfiguration(default_configuration_file)

def calculate_evidences():
    executionSteps = [ge,pe,me,ce]
    configuration = Utilities.loadConfiguration(default_configuration_file)

    for executionStep in executionSteps:
        print("------------------------------------------------------------")
        print("Start " + executionStep.get_name())
        executionStep.execute(configuration)
        print("Finished " + executionStep.get_name())
    print("------------------------------------------------------------")
    print("Finished")
