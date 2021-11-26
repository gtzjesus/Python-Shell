

import os, re, sys

class Shell:

    # File Descriptors:
    #       0: input
    #       1: output

    def __init__(self):
        self.prompt()

    def prompt(self):
        while 1:
            command = self.getCommand()
            if command == "exit":
                sys.exit(0)
            elif command == "":
                pass
            elif command[0] == "#":
                pass
            elif command[0:2] == "cd":
                command = command.split()
                self.changeDirectory(command[1])
            elif ">" in command or "<" in command:
                self.redirection(command)
            elif "&" in command:
                self.runEXECVE(command)
            elif "|" in command:
                pid = os.fork() 
                if pid == 0: 
                    self.piping(command)
                elif pid > 0: 
                    os.wait() 
                else: # pid < 0 => error
                    print("fork() failed")
            else:
                self.execute(command)

    def getCommand(self):
        os.write(1, (os.getcwd() + "\n$ ").encode())
        userInput = os.read(0, 128)
        userInput = userInput.strip()
        userInput = userInput.decode().split("\n")
        userInput = userInput[0]
        userInput = str(userInput)
        return userInput

    def changeDirectory(self, path):
        try:
            os.chdir(path)
        except:
            os.write(1, "No such directory\n".encode())

    def execute(self, command):
        pid = os.fork() 
        if pid == 0: 
            self.runEXECVE(command)
        elif pid > 0: 
            os.wait() 
        else: # pid < 0 => error
            print("fork() failed")

    def runEXECVE(self, command):
        line = command.split()
        for dir in re.split(":", os.environ['PATH']):
            program = "%s/%s" % (dir, line[0])
            try:
                os.execve(program, line, os.environ) 
            except:                
                pass
        os.write(1, ("shell: "+ line[0] +" command not found\n").encode())
        sys.exit(0)

    def redirection(self, command):
        pid = os.fork() 
        if pid == 0:
            if ">" in command:
                command = command.split(">")
                os.close(1)
                os.open(command[1], os.O_CREAT | os.O_WRONLY)
                os.set_inheritable(1,True)

            else:
                command = command.split("<")
                os.close(0)
                command[1] = command[1].strip()
                os.open(command[1], os.O_RDONLY)
                os.set_inheritable(0, True)

            self.runEXECVE(command[0])
        elif pid > 0:
            os.wait()
        else:
            print("redirection() failed")

    def piping(self, command):
        command = command.split("|", 1)
        first    = command[0]
        second   = command[1]
        inputPipe, outputPipe = os.pipe()
        pid = os.fork()
        if pid == 0: # child
            os.close(1)
            os.dup(outputPipe)
            os.set_inheritable(1, True)
            for fd in (inputPipe, outputPipe):
                os.close(fd)
            self.runEXECVE(first)
        elif pid > 0: # parent
            os.close(0)
            os.dup(inputPipe)
            os.set_inheritable(0, True)
            for fd in (outputPipe, inputPipe):
                os.close(fd)
            if "|" in second: # in case there are more commands
                self.piping(second)
            self.runEXECVE(second)

shell = Shell()