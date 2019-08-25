import subprocess
import os
import shutil
import time
import threading
import logging

DEBUG = True
process = None
processOpen = False
ignoreTimedBackup = False
beginThread = True
#begin functions
def beginServer(mcdir):
    '''function contains logic to start server and to continue communicating with it.'''
    os.chdir(mcdir)
    #java is in system path so using just 'java' works when invoking the server.jar
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
    print("Waiting %s seconds for server to stop..." % (gracePeriod))
    time.sleep(gracePeriod)
    if process.returncode is None:
        process.terminate()
    print("Beginning backup...")
    copyToOtherDir(mcsdir, backuloc + "\\" + worldName)
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
    print(">>timer management thread: beginning backup timer.")
    while True and (not process is None):
        if beginThread:
            timerThread = threading.Thread(target = timedBackup, args = (mcsDir, backUpLoc, worldName))
            timerThread.start()
            beginThread = False

def main(mcsDir, backUpLoc, worldName):
    global process
    global processOpen
    command = ""
    timerManagerThread = None
    #todo: add email functionality
    print("Sever not started yet, use command 'start' to run the server program")
    while command != "quit":
        command = input(">>Enter command: <<\t")
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
            innerCommand = input("Restart server after backup?(y/n) << ")
            startServer = False
            if innerCommand == "y":
                startServer = True
            processOpen = False
            process = beginBackup(process, mcsDir, backUpLoc, worldName, startServer)
            processOpen = True
            print("Server restarted")
        elif command == 'refresh':
            commandServer(process, "/stop")
            time.sleep(10)
            process = beginServer(mcsDir)
            print("Server Started")
        elif command == 'quit':
            if not process is None:
                commandServer(process, "/stop")
            if not timerManagerThread is None:
                timerManagerThread.stop()
        else:
            commandServer(process, command) 
    print("ending execution of script")
#call to main
print("Welcome to automated server backup script v1.0\n-- Written by James 'Joey' Ellerbee")
mcsdir = ''
if not DEBUG:
    mcsdir = input("Input the directory containing server jar file... ")
else:
    mcsdir = r"C:\Users\ellerbee_james1\Documents\pythonprojects\minecraftserverscript\MCServer"
#todo: implement config file
if mcsdir != "debug":
    worldName = ''
    backUpLoc = ''
    if not DEBUG:
        worldName = input("Input the name of the world... ")
        backUpLoc = input ("Input desired directory to store backups of minecraft world... ")
    else: 
        worldName = "world"
        backUpLoc = r"C:\Users\ellerbee_james1\Documents\pythonprojects\minecraftserverscript\backups"     
    if not os.path.exists(backUpLoc):
        #create backup directory if it does not exist
        os.mkdir(backUpLoc)
    main(mcsdir, backUpLoc, worldName)