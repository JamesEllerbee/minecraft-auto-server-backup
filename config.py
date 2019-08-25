'''this script reads a the config file, if it does not exist, it creates one with default parameters'''
import os

#DEBUG = False
mcsdir = ''
worldName = ''
backUpLoc = ''
timeBeforeBackup = 0

def conFErr(configF):
    print("Issue with config file, try deleting it and running the script again.") #will update this to be more useful in future iteration
    configF.close()
    exit()

def parseBool(inputStr):
    if inputStr == 'true':
        return True
    return False

def read():
    global mcsdir
    global worldName
    global backUpLoc
    if not os.path.exists('config'):
        print('Cannot find config file... creating one now.')
        newConfigFile = open('config', 'w+')
        mcsdir = input("Input the directory containing server jar file... > ")
        worldName = input("Input the dir name of the world file (can be found with in the dir containing the server script)...\n> ")
        backUpLoc = input ("Input desired directory to store backups of minecraft world... > ")
        newConfigFile.write('server directory=' + mcsdir + '\n')
        newConfigFile.write('world name=' + worldName + '\n')
        newConfigFile.write('backup location=' + backUpLoc + '\n')
        newConfigFile.write('time before backup=' + 3600 + '\n')
        newConfigFile.close()
        print("config created...")
    print("Reading config file...")
    inStr = ''
    #print(os.getcwd())
    configF = open('config', 'r')
    #begin parse
    inStr = configF.readline()
    inStr = inStr.split('=')
    if inStr[0] == 'server directory':
        mcsdir = inStr[1].strip()
        print("Looking for MCserver.jar in directory '" + mcsdir + "'")
    else:
        conFErr(configF)
    inStr = configF.readline()
    inStr = inStr.split('=')
    if inStr[0] == 'world name':
        worldName = inStr[1].strip()
        print("Looking for world named '" + worldName + "' when backing up world file.")
    else:
        conFErr(configF)
    inStr = configF.readline()
    inStr = inStr.split('=')
    if inStr[0] == 'backup location':
        backUpLoc = inStr[1].strip()
        print("World backup location in directory '" + backUpLoc + "'")
        if not os.path.exists(backUpLoc):
            #create backup directory if it does not exist
            print("It does not appear that directory exists, creating directory...")
            os.mkdir(backUpLoc)
    else:
        conFErr(configF)
    inStr = configF.readline()
    inStr = inStr.split('=')
    if inStr[0] == 'time before backup':
        timeBeforeBackup = int(inStr[1])
        print("time before back up: "+ timeBeforeBackup + " seconds.")
    else:
        conFErr(configF)
    configF.close()