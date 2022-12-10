import os
class Logger:
    """
    The class for output log file. Passed functions will be logged in the log_pass.txt, and failed functions will be logged in the log_fail.txt.

    Attributes
    ----------
    output_path: the folder to store the log file.

    Methods
    -------
    log_task(self, function_name, status, input, output):
        Add a new log entry. This function will call self.log() each time a new log entry has been added.
    log(self):
        Generate the log file for all current log entries. Usually no need to call this function as it will be called in the log_task() function.
    """

    STATUS_PASS = "Passed"
    STATUS_FAIL = "Failed"

    def __init__(self, output_path):

        self.tasks = []
        self.output_path = output_path


    def log_task(self, function_name, status, input, output):
        """
        Add a new log entry. This function will call self.log() each time a new log entry has been added.

        Parameters
        ----------
        function_name: The name for the function.
        status: The function call status, this can only be STATUS_PASS or STATUS_FAIL.
        input: The input string for the function call.
        output: The output string for the function call.
        """
        self.tasks.append({"function_name": function_name,
                        "status": status,
                        "input": input, 
                        "output": output,
                        })
        self.log()
        return

    def log(self):
        """
        Generate the log file for all current log entries. Usually no need to call this function as it will be called in the log_task() function.
        """
        task_count = self.tasks.__len__()
        i = 1
        output_pass = ""
        output_fail = ""
        f_pass = open(os.path.join(self.output_path, "log_pass.txt"), 'a')
        f_fail = open(os.path.join(self.output_path, "log_fail.txt"), 'a')
        for task in self.tasks:
            temp = ""
            temp += "Task " + str(i) + "/" + str(task_count) + ":\n"
            temp += "Fuzzing function: " + task["function_name"] + " with status: " + task["status"] + "\n"
            temp += "----- Input string -----\n" + task["input"] + "\n"
            temp += "----- Output string -----\n" + str(task["output"]) + "\n"
            temp += "\n\n"
            i += 1
            if task["status"] == self.STATUS_PASS:
                output_pass += temp
            elif task["status"] == self.STATUS_FAIL:
                output_fail += temp
        f_pass.write(output_pass)
        f_fail.write(output_fail)
        f_pass.close()
        f_fail.close()
        return
        

            

