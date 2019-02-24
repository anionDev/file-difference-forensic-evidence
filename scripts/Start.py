import ge
import pe
import me
import ce
import Utilities
executionSteps = [ge,pe,me,ce]
configuration = Utilities.loadConfiguration("configuration.txt")

for executionStep in executionSteps:
    print("------------------------------------------------------------")
    print("Start " + executionStep.get_name())
    executionStep.execute(configuration)
    print("Finished " + executionStep.get_name())
print("------------------------------------------------------------")
print("Finished")