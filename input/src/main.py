import re
import csv
import sys
import os
import subprocess
import logging

import create_unique_lists
import create_vectors

APKTOOL_VERSION="2.5.0"
APKTOOL_INSTALL ="https://ibotpeaches.github.io/Apktool/install/"

LOGS_FOLDER ="./../../output/logs/"
LOG_FILE = LOGS_FOLDER + "input_engine_log.txt"
ENABLE_LOGGING = 1
ENABLE_FILE_LOGGING = 1

def log(msg,lvl):
    """ To enable single point logging with different log levels.
         Arguments  : msg - msg to be logged
            lvl - debug log level
                0 - No logging
                1 - Logging enabled (Info/warning)
                2 - Error
        Returns    : None
    '"""
    if ENABLE_LOGGING:
        if lvl == 1:
            print(msg)

    if ENABLE_FILE_LOGGING:
        if lvl==2:
            logging.error(msg)
        else:
            logging.warning(msg)

def run_command(cmd):
    """ To run commands using subprocess module instead of os.system()
                            This enables us to handle all error cases in one place.
        Arguments  : cmd - command to be executed
        Returns      : code - return value of the command
        Example     : run_command(["ls", "-l"]) - arguments should be in a list format
    """
    output = subprocess.run(cmd, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,universal_newlines=True)
    
    if output.returncode != 0:
        log("Error..",2)
        log("STDOUT: " + str(output.stdout), 2)
        log("STDERR: " + str(output.stderr), 2)
        log("RETURN: " + str(output.returncode), 2)

    return [output.returncode, output.stdout]

def load_apk(apk_path):
    """ To decode apk using apktool and overwrite if folder exists
        Arguments  : apk_path - full path where apk is stored
        Returns    : return code for success/failure
    """

    apk_output_folder = "./../../output/apks/"

    #split apk_path & apk name
    apk_path_only, apk_name = os.path.split(apk_path)
    apk_name = apk_name.replace(".apk","")

    #set output path
    out = os.path.join(apk_output_folder, apk_name + "_A")

    #-f argument overwrites the folder
    #-o argument specifies output directory
    res = run_command(["apktool","d",apk_path,"-f","-o",out])
    #print(res)
    return res[0]

def check_apktool_version():
    """ To check if apktool exists and verfiy correct version
        Arguments  : None
        Returns    : None
    """
    #print("Checking apktool version...")
    res = run_command(['apktool','-version'])
    result = ""
    result = result.join(res[1]).strip('\n')
    if result == APKTOOL_VERSION:
        log("Apktool " + APKTOOL_VERSION + " found", 1)
    else:
        log("Kindly install apktool version " + APKTOOL_VERSION + " from "
            + APKTOOL_INSTALL, 1)
        sys.exit(0)

def main():
    """ Main fuction """

    input_folder = "./../apks"
    apk_output_folder = "./../../output/apks/"

    if ENABLE_FILE_LOGGING:
        logging.basicConfig(filename=LOG_FILE,
              format='%(asctime)s %(message)s', filemode='w')

    #check apktool is present
    check_apktool_version()

    log("Decoding APKs", 1)
    count = 0
    failed_count = 0
    for files in os.listdir(input_folder):
        if files.endswith(".apk"):
            apk_path = os.path.join(input_folder, files)
            if load_apk(apk_path) == 0:
                log("    Decoded " + files, 1)
                apk_name = files.replace(".apk","")
                run_command(["./static_code_capturing.sh", apk_output_folder + apk_name + "_A"]) 
                count = count + 1
            else:
                failed_count = failed_count + 1
                log("    Failed to decode " + files, 0)
    log("    " + str(count) + " files decoded", 1)
    if failed_count:
        log("    Failed to decode " + str(count) + " files", 1)        
    
    if count > 0:
        pass
    else:
        log("No APKs decoded", 1)
        sys.exit(0)

    #Create temp files
    log("    Creating temp files for storing the static features", 0)
    with open('./1_List_Permissions.csv', 'w') as fp:
        pass

    with open('./2_List_Services.csv', 'w') as fp:
        pass

    with open('./3_List_Actions.csv', 'w') as fp:
        pass

    with open('./4_List_Categories.csv', 'w') as fp:
        pass

    print("    Generating unique lists")
    for apk_folders in os.listdir(apk_output_folder):
        if not apk_folders.endswith(".apk"):
            for files in os.listdir(apk_output_folder + apk_folders):
                if files.endswith(".txt"):
                    create_unique_lists.func(apk_output_folder + apk_folders + "/" + files)

    if os.path.isfile('./../feature_vector/input.csv'):
        os.remove('./../feature_vector/input.csv')

    log("    Generating the csv file", 1)
    for apk_folders in os.listdir(apk_output_folder):
        if not apk_folders.endswith(".apk"):
            for files in os.listdir(apk_output_folder +  apk_folders):
                if files.endswith(".txt"):
                    create_vectors.csv_gen(apk_output_folder + apk_folders + "/" + files, apk_output_folder)

    log("    Removing temp files used for storing the static features", 0)
    os.remove('./1_List_Permissions.csv')
    os.remove('./2_List_Services.csv')
    os.remove('./3_List_Actions.csv')
    os.remove('./4_List_Categories.csv')

    for apk_folders in os.listdir(apk_output_folder):
        if not apk_folders.endswith(".apk"):
            for files in os.listdir(apk_output_folder +  apk_folders):
                if files.endswith(".txt"):
                    os.remove(apk_output_folder + apk_folders + "/" + files)

if __name__ == '__main__':
    main()

