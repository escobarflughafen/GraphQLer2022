

class Logger:

    def __init__(self):
        self.tasks = []


    def append_task(self, function_name, status, input, output):
        self.tasks.append({"function_name": function_name,
                        "status": status,
                        "input": input, 
                        "output": output,
                        })
        return

    def output(self, output_path):
        task_count = self.tasks.count()
        i = 1
        output = ""
        f = open(output_path, 'w')
        for task in self.tasks:
            output += "Task " + i + "/" + task_count + ":\n"
            output += "Fuzzing function: " + task["function_name"] + " with status: " + task["status"] + "\n"
            output += "----- Input string -----\n" + task["input"]
            output += "----- Output string -----\n" + task["output"]
            output += "\n\n"
            i += 1
        f.write(output)
        f.close()
        return
        

            

