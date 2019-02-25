import ge
import pe
import me
import ce
import utilities
import logging


def calculate_evidences():
    configuration = Utilities.Configuration()
    logging.basicConfig(filename=log_file,
                        filemode='a',
                        format='%(asctime)s.%(msecs)03d %(name)s [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=loglevel)
    executionSteps = [ge,pe,me,ce]
    print("Started")
    for executionStep in executionSteps:
        print("------------------------------------------------------------")
        print("Start " + executionStep.get_name())
        executionStep.execute(configuration)
        print("Finished " + executionStep.get_name())
    print("------------------------------------------------------------")
    print("Finished")
