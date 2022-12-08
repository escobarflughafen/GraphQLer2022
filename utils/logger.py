class Logger:

    def __init__(self, output_path):
        self.tasks = []
        self.output_path = output_path


    def append_task(self, function_name, status, input, output):
        self.tasks.append({"function_name": function_name,
                        "status": status,
                        "input": input, 
                        "output": output,
                        })
        return

    def log(self):
        task_count = self.tasks.__len__()
        i = 1
        output = ""
        f = open(self.output_path, 'w')
        for task in self.tasks:
            output += "Task " + str(i) + "/" + str(task_count) + ":\n"
            output += "Fuzzing function: " + task["function_name"] + " with status: " + task["status"] + "\n"
            output += "----- Input string -----\n" + task["input"] + "\n"
            output += "----- Output string -----\n" + str(task["output"]) + "\n"
            output += "\n\n"
            i += 1
        f.write(output)
        f.close()
        return
        

            

