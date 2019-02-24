import ge
import pe
import me
import ce
import Utilities
import logging

logging.basicConfig(filename=log_file,
                    filemode='a',
                    format='%(asctime)s.%(msecs)03d %(name)s [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=loglevel)

def calculate_evidences():
    executionSteps = [ge,pe,me,ce]
    configuration = Utilities.Configuration()
    for executionStep in executionSteps:
        print("------------------------------------------------------------")
        print("Start " + executionStep.get_name())
        executionStep.execute(configuration)
        print("Finished " + executionStep.get_name())
    print("------------------------------------------------------------")
    print("Finished")
