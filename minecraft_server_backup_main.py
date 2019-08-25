import subprocess
import os
import shutil
import time
import threading
import logging

#todo: implement config 
DEBUG = True
process = None
processOpen = False
ignoreTimedBackup = False
beginThread = True
#begin functions
def beginServer(mcdir):
    '''function contains logic to start server and to continue communicating with it.'''
    os.chdir(mcdir)
    #java is in system path so using 'java' works when invoking the server.jar
    return subprocess.Popen(['java', '-Xmx4G', '-Xms4G', '-jar', 'server.jar', 'nogui'], stdin = subprocess.PIPE) 

def commandServer(process, cmd):
    '''this function writes the command to the input stream the accepting input on'''
    process.stdin.write(bytes(cmd,'utf-8'))

def debugCurrentDir():
    '''this function prints the current directory, used for debugging purposes'''
    cwd = os.getcwd()
    print("current directory: ", cwd)

def beginBackup(process, mcsdir, backuloc, worldName, startServer):
    '''this function handles backing up world file, returns the new server process'''
    gracePeriod = 30
    commandServer(process, "/stop")
    print(">>> Waiting %s seconds for server to stop..." % (gracePeriod))
    time.sleep(gracePeriod)
    if process.returncode is None:
        process.terminate()
    print("Beginning backup...")
    copyToOtherDir(mcsdir + "/" + worldName, backuloc + "/" + worldName) #todo: implement a better solution for pathing.
    print("Server Backed up sucessfully!")
    if startServer:
        return beginServer(mcsdir)
    return None

def copyToOtherDir(source, destination):
    '''this function handles copying world file to backup targetlocation'''
    if os.path.exists(destination):
        #recrusive file removal and remove dir
        shutil.rmtree(destination)
    shutil.copytree(source, destination)

def timedBackup(mcsdir, backuloc, worldName):
    global process
    global processOpen
    global beginThread
    print("Thread: timer began")
    timeBeforeBackup = 60
    timeStart = time.time()
    lap = timeStart
    while lap - timeStart < timeBeforeBackup:
        lap = time.time()
        if lap - timeStart > timeBeforeBackup - 10:
            #send command to server
            commandServer(process, "/say backup starting soon")
    if not process is None: 
        processOpen = False
        process = beginBackup(process, mcsdir, backuloc, worldName, True)
        processOpen = True
    beginThread = True

def timerManager(mcsDir, backuloc, worldName):
    global beginThread
    global process
    print(">> timer management thread: beginning backup timer.")
    while True and (not process is None):
        if beginThread:
            timerThread = threading.Thread(target = timedBackup, args = (mcsDir, backUpLoc, worldName))
            timerThread.start()
            beginThread = False

def main(mcsDir, backUpLoc, worldName):
    global process
    global processOpen
    command = ""
    vaildScriptCommands = ['start','quit','start backup timer','backup','quit','/[anything]'] #use a dictonary to store commands and their def, need to figure out how to print both key and def tho.
    timerManagerThread = None
    #todo: add email functionality
    print("Warning: Sever not started yet, use command 'start' to run the server program!\nuse command 'help' to see a list of available commands.\nuse /[command] to send command to sever.")
    while command != "quit":
        command = input(">>> Enter command: <<<\t")
        command = command.lower()
        if command == "start":
            if process is None:
                process = beginServer(mcsDir)
                time.sleep(15)
                processOpen = True
                print("Server Started!")
            else:
                print("Sever is already running!")     
        elif command == "start backup timer":
            timerManagerThread = threading.Thread(target = timerManager, args = (mcsDir, backUpLoc, worldName))
            timerManagerThread.start()
            time.sleep(1)
        elif command == "stop backup timer":
            print("Command not implemented currently")
        elif command == 'backup':
            #user prompted backup before timer or exit
            innerCommand = input(">>>\tRestart server after backup?(y/n) <<<\n$")
            startServer = False
            if innerCommand == "y":
                startServer = True
            processOpen = False
            process = beginBackup(process, mcsDir, backUpLoc, worldName, startServer)
            processOpen = True
            if startServer:
                print("Server restarted")
        elif command == 'quit':
            if not process is None:
                commandServer(process, "/stop")
            if not timerManagerThread is None:
                timerManagerThread.stop()
        elif command == 'help':
            print(vaildScriptCommands)
            #todo: expand this
        else:
            commandServer(process, command) 
    print("...End execution of script.")
    
#begin execution
print("Welcome to automated server backup script v1\n-- Written by James 'Joey' Ellerbee")
if not DEBUG:
    mcsdir = input("Input the directory containing server jar file... ")
else:
    #using os.path for portability.
    curdir = os.path.dirname(__file__)
    mcsdir = os.path.join(curdir, 'MCServer')
if mcsdir != "debug":
    worldName = ''
    backUpLoc = ''
    if not DEBUG:
        worldName = input("Input the name of the world... ")
        backUpLoc = input ("Input desired directory to store backups of minecraft world... ")
    else: 
        worldName = "world"
        curdir = os.path.dirname(__file__)
        backUpLoc = os.path.join(curdir, 'backups')  
    if not os.path.exists(backUpLoc):
        #create backup directory if it does not exist
        os.mkdir(backUpLoc)
    main(mcsdir, backUpLoc, worldName)