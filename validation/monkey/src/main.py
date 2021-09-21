""" Source code of Validation Module """
import os
import xml.etree.ElementTree as ET
import subprocess
import argparse
import logging
import hashlib
import sys
import shutil
from time import sleep
from shutil import copyfile, which
from os import listdir
from os.path import isfile, join
import pandas as pd

# Global Arguments #
ENABLE_LOGGING = 1
PRINT_TO_SCREEN = 1
DONT_PRINT_TO_SCREEN = 0
ENABLE_FILE_LOGGING = 1

PASS_PERCENT=15

#folders
INPUT_APK_FOLDER="./../../../input/apks/"
MODIFIED_APK_FOLDER="./../../../output/apks/"

INPUT_APKS_RESULT = "./../input_apks_result/"
MODIFIED_APKS_RESULT = "./../modified_apks_result/"
LOGS_FOLDER ="./../../../output/logs/"

#file
LOG_FILE = LOGS_FOLDER + "validation_log.txt"
FAILED_APK_FILE = LOGS_FOLDER + "validation_failed_apks.txt"

#Comparison output
COMPARISON_OUTPUT_FOLDER="./../comparison/"
TEMP_INPUT_CROP_FOLDER1="crop_1/"
TEMP_INPUT_CROP_FOLDER2="crop_2/"

# Emulator commands
emulator = ""
APP_INSTALL_CMD = "adb install "
APP_UNINSTALL_CMD = "adb uninstall "

EMULATOR_LAUNCH_CMD = "emulator -avd "
EMULATOR_CLOSE_CMD  = "adb emu kill"
PACKAGE_LAUNCH_COMMAND = "adb shell monkey -p "
MONKEY_CMD_PARAMS = " -s 200 --throttle 100 --kill-process-after-error --monitor-native-crashes -v 500"
EMULATOR_LAUNCH_SLEEP = 90

package_name_command = 'aapt dump badging ## | grep \'package\|^launchable-activity\' | cut -d \' \' -f 2 | head -n 1'

# Functions
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

def parse_csv():
    """ To parse csv file and make changes in apk
        Arguments  : None
        Returns    : None
    """
    count =0
    total_apk_found = 0

    for folder in os.listdir(INPUT_APK_FOLDER):
        if folder.endswith(".apk"):
            total_apk_found = total_apk_found + 1

    if total_apk_found == 0:
        log("No apks found in input folder", 1)
        sys.exit(1)

    #kill_server = run_command("adb kill-server")
    launch_emulator()
    #start_server = run_command("adb start-server")
    sleep(5)

    log(f"\n{total_apk_found} APK(s) found in Input apk folder", 1)

    apk_failed = 0
    apk_success = 0
    apk_missing = 0
    apk_installed = 0
    apk_launched = 0                
    fail_buffer = ""

    input_failed_list = []
    modified_failed_list = []

    monkey_apps = 0
    non_monkey_apps = 0

    #input folder
    for apk_file in os.listdir(INPUT_APK_FOLDER):
        if apk_file.endswith(".apk"):
            # Command to get package name of the app from its apk.
            pkg_name = get_package_name(INPUT_APK_FOLDER + apk_file)
            if pkg_name:
                log(pkg_name, 1)
                if install_apk(INPUT_APK_FOLDER + apk_file):
                    if launch_apk(pkg_name):  
                        pin_apk(pkg_name, INPUT_APKS_RESULT)  
                        uninstall_apk(pkg_name)
                else:
                    fail_buffer = fail_buffer + str(apk_file) + " - install failed\n"
                    input_failed_list.append(apk_file)

    #run install failed apks
    if(len(input_failed_list) > 0):
        log("Rerunning " + str(len(input_failed_list))+ " apks that failed to install", 1)
        for apks in input_failed_list:
            pkg_name = get_package_name(INPUT_APK_FOLDER + apks)
            if pkg_name:
                log(pkg_name, 1)
                if install_apk(INPUT_APK_FOLDER + apks):
                    if launch_apk(pkg_name):  
                        pin_apk(pkg_name, INPUT_APKS_RESULT)  
                        uninstall_apk(pkg_name)


    #close and restart the emulator
    log("\n", 1)
    close_emulator()
    launch_emulator()


    total_apk_found = 0
    for folder in os.listdir(MODIFIED_APK_FOLDER):
        if folder.endswith(".apk"):
            total_apk_found = total_apk_found + 1

    if total_apk_found == 0:
        log("No apks found in Output folder", 1)
        sys.exit(1)

    log(f"\n{total_apk_found} APK(s) found in Output apk folder", 1)

    #modified apks
    for apk_file in os.listdir(MODIFIED_APK_FOLDER):
        if apk_file.endswith(".apk"):

            # Command to get package name of the app from its apk.
            pkg_name = get_package_name(MODIFIED_APK_FOLDER + apk_file)
            if pkg_name:
                log(pkg_name, 1)
                if install_apk(MODIFIED_APK_FOLDER + apk_file):
                    if launch_apk(pkg_name):  
                        pin_apk(pkg_name, MODIFIED_APKS_RESULT)  
                        uninstall_apk(pkg_name)
                else:
                    fail_buffer = fail_buffer + str(apk_file) + " - install failed\n"
                    modified_failed_list.append(apk_file)

    #run install failed apks
    if(len(modified_failed_list) > 0):
        log("Rerunning " + str(len(modified_failed_list))+ " apks that failed to install", 1)
        for apks in modified_failed_list:
            pkg_name = get_package_name(MODIFIED_APK_FOLDER + apks)
            if pkg_name:
                log(pkg_name, 1)
                if install_apk(MODIFIED_APK_FOLDER + apks):
                    if launch_apk(pkg_name):  
                        pin_apk(pkg_name, MODIFIED_APKS_RESULT)  
                        uninstall_apk(pkg_name)

    #remove apk folder
    #shutil.rmtree(output_apk_path)
    if emulator:
        close_emulator()

    '''
    log(f"{apk_success}/{total_apk_found} modified, {apk_failed} failed", 1)
    if emulator:
        log(f"{apk_installed}/{total_apk_found} installed, " \
            f"{total_apk_found - apk_installed} failed", 1)
        log(f"{apk_launched}/{total_apk_found} run in emulator, " \
            f"{total_apk_found - apk_launched} failed", 1)
    log(f"{apk_missing} apk missing based on csv input", 1)
    '''
    with open(FAILED_APK_FILE, "w") as writer:
        writer.write(fail_buffer)


def get_package_name(apk):
    """ To get package name of the apk
        Arguments  : apk - name of apk for which package name is to be found
        Returns    : return package name of the apk
    """
    log("Finding package name for " + apk, 0)
    package_name=""
    package_name_command = "aapt dump badging " + apk + \
                            ' | grep -n "package: name" | grep "1:"'
    package = subprocess.Popen(package_name_command,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (package, err) = package.communicate()
    package = package.decode()
    err = err.decode()

    if err:
        log("        Failed to get the package name", 0)
        log("        ERR: " + str(err), 2)
        return ""

    package_list = package.split("'")
    package_name = package_list[1]
    return package_name

def install_apk(apk):
    """ To install apk in emulator
        Arguments  : apk - path of apk to be installed
        Returns    : return code for success/failure
    """

    try:
        app_install_proc = subprocess.Popen(APP_INSTALL_CMD + apk,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        app_installation_status, err = app_install_proc.communicate(timeout=20)
        sleep(3)

        if "Success" in str(app_installation_status):
            log("        APK installed", PRINT_TO_SCREEN)
            return 1

        log("        APK install failed", PRINT_TO_SCREEN)
        log("        STDERR: " + str(err), 2)

    except subprocess.TimeoutExpired:
        log("        APK install failed", PRINT_TO_SCREEN)
        log("        APK Install timed out", 0)

    return 0

def uninstall_apk(apk):
    """ To uninstall apk in emulator
        Arguments  : apk - path of apk to be uninstalled
        Returns    : return code for success/failure
    """
    log("        Uninstalling apk : " + apk, 0)
    try:
        app_uninstall_proc = subprocess.Popen(APP_UNINSTALL_CMD + apk,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            start_new_session=True, shell=True)
        app_uninstallation_status, err = app_uninstall_proc.communicate(timeout=60)
        sleep(3)

        if "Success" in str(app_uninstallation_status):
            log("        APK uninstalled", PRINT_TO_SCREEN)
            return 1

        log("        APK uninstall failed", PRINT_TO_SCREEN)
        log("        STDERR: " + str(err), 2)

    except subprocess.TimeoutExpired:
        log("        APK uninstall failed", PRINT_TO_SCREEN)
        log("        APK Uninstall timed out", 0)

    return 0

def launch_apk(package_name):
    """ To launch apk in emulator
        Arguments  : package_name - name of apk to be launched
        Returns    : return code for success/failure
    """
    log("        Launching APK : " + package_name, 0)
    try:
        emulator_launch_proc = subprocess.Popen(PACKAGE_LAUNCH_COMMAND +
            package_name + " 1", stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            start_new_session=True, shell=True)
        sleep(10)

        pid_proc = subprocess.Popen('adb shell pidof ' + package_name,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        pid_proc_stdout, err = pid_proc.communicate(timeout=10)
        pid = pid_proc_stdout.decode()
        err = err.decode()

        if str(err) != "":
            log("        APK launching failed", PRINT_TO_SCREEN)
            log("        STDERR: " + str(err), 2)
            return 0

        log("        APK launched", PRINT_TO_SCREEN)

        if str(pid) == "":
            log("        APK PID failed", PRINT_TO_SCREEN)
            return 0

    except subprocess.TimeoutExpired:
        log("        APK launching failed", PRINT_TO_SCREEN)
        log("        APK launching timed out", 0)

    return 1

def pin_apk(package_name, log_folder):
    """ To pin apk in emulator
        Arguments  : package_name - name of apk to be launched
        Returns    : return code for success/failure
    """

    app_task_id_command = 'adb shell dumpsys activity recents | grep ## | cut -d \' \' -f 7 | head -n 1'
    app_task_id_command_temp = app_task_id_command.replace("##", package_name)

    app_pin_command = "adb shell am task lock "

    # Command to unpin app.
    app_unpin_command = 'adb shell am task lock stop'

    # Command to terminate app.
    app_terminate_command = 'adb shell am force-stop '

    monkey_file = " > " + log_folder + package_name + ".txt"

    log("        Pinning APK : " + package_name, 0)
    app_task_id_proc = subprocess.Popen(app_task_id_command_temp, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (app_task_id_status, err) = app_task_id_proc.communicate()
    app_task_id_temp = app_task_id_status.decode()
    sleep(3)

    if "#" in app_task_id_temp:
        app_task_id = app_task_id_temp[1:-1]
        log("        APK Task ID : " + app_task_id, 0)

        try:

            # Runs the command in the device shell to pin the app to the screen.
            app_pin = (app_pin_command + app_task_id)
            app_pin_proc = subprocess.Popen(app_pin, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            (app_pin_status, err) = app_pin_proc.communicate()
            log("        APK pinned to screen", PRINT_TO_SCREEN)
            sleep(3)

            monkey_event_command_temp = PACKAGE_LAUNCH_COMMAND + package_name + MONKEY_CMD_PARAMS + monkey_file
            monkey_proc = subprocess.Popen(monkey_event_command_temp, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            monkey_proc.communicate()
            sleep(3)

            # Gets PID after monitoring.
            pid_proc = subprocess.Popen('adb shell pidof ' + package_name,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            pid_proc_stdout, err = pid_proc.communicate(timeout=10)
            pid = pid_proc_stdout.decode()
            #print("Need to account for pid variation")	
            sleep(3)	

            # Runs the command in the device shell to unpin the app from the screen.
            app_unpin_proc = subprocess.Popen(app_unpin_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            (app_unpin_status, err) = app_unpin_proc.communicate()
            log("        APK unpinned", PRINT_TO_SCREEN)
            sleep(3)

            # Runs the command in the device shell to terminate the execution of the app.
            app_term_proc = subprocess.Popen(app_terminate_command + package_name, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            (app_term_status, err) = app_term_proc.communicate()
            sleep(3)
            
        except:
            log("        Exception occured in testing", PRINT_TO_SCREEN)

    else:
        log("        Screen pinning failed.", PRINT_TO_SCREEN)
        log(str (app_task_id_temp) + "\n" + str(err), PRINT_TO_SCREEN)
    
    log("        APK testing completed", PRINT_TO_SCREEN)
    return 1


def check_android_emulator():
    """ To check if emulator and aapt is installed
        Arguments  : None
        Returns    : None
    """
    #Checking Android Emulator
    log("Checking emulator is in path...", 0)
    try:
        res = run_command(['emulator','-version'])
        if res[0] == 0:
            log("Emulator found in PATH", PRINT_TO_SCREEN)
            log("Emulator found: " + str(res[1]), 0)

    except FileNotFoundError:
        log("Emulator not found", PRINT_TO_SCREEN)
        sys.exit(1)

    #Checking Aapt
    log("Checking aapt is in path...", 0)
    try:
        res = run_command(['aapt','version'])
        if res[0] == 0:
            log("Aapt found in PATH", PRINT_TO_SCREEN)
            log("Aapt found " + str(res[1]), 0)

    except FileNotFoundError:
        log("Aapt not found", PRINT_TO_SCREEN)
        sys.exit(1)

    #Checking Android emulator name
    log("Checking if emulator " + str(emulator) + " is available...", 0)
    emulators_list_proc = subprocess.Popen('emulator -list-avds',
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE, shell=True)
    emulators_list = emulators_list_proc.communicate()[0]
    emulators_list = emulators_list.decode()
    emulators_list = emulators_list.split("\n")
    emulators_list.remove('')
    if emulator not in emulators_list:
        log("Invalid emulator. \nAvaliable emulators : " + str(emulators_list), PRINT_TO_SCREEN)
        sys.exit(1)
    else:
        log("Emulator %s found"%emulator, PRINT_TO_SCREEN)

def launch_emulator():
    """ To launch the android emulator
        Arguments  : None
        Returns    : return code for success/failure
    """
    log("Launching android emulator", PRINT_TO_SCREEN)

    emulator_launch_proc = subprocess.Popen(EMULATOR_LAUNCH_CMD + emulator + " -wipe-data",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        start_new_session=True, shell=True)
    sleep(EMULATOR_LAUNCH_SLEEP)

def close_emulator():
    """ To close the android emulator
        Arguments  : None
        Returns    : return code for success/failure
    """
    log("Shutting down android emulator", PRINT_TO_SCREEN)

    emulator_close_proc = subprocess.Popen(EMULATOR_CLOSE_CMD,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        start_new_session=True, shell=True)
    sleep(15)

def init_argparse():
    """ To handle command line args
        Arguments  : None
        Returns    : None
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-e","--emulator", type=str,
                help="Emulator to test the generated APK")

    args = parser.parse_args()

    #validate args & set variables accordingly
    global emulator

    if args.emulator:
        emulator = args.emulator

def countLines(path):
    file = open(path, "r")
    Counter = 0
    Content = file.read()
    CoList = Content.split("\n")
    for i in CoList:
        if i:
            Counter += 1
    return(int(Counter))

def generate_csv(path1, path2, csv_name):
    features_df = ['APK_Name','Before_Modification','After_Modification','Line_difference','Percentage_difference']
    df = pd.DataFrame(columns = features_df )
    files_in_dir1 = [files_1 for files_1 in listdir(path1 ) if isfile(join(path1 , files_1))]
    files_in_dir2 = [files_2 for files_2 in listdir(path2 ) if isfile(join(path2 , files_2))]
    monkey_test_success = 0
    count_low = 0
    for range_file_1 in files_in_dir1:
        for range_file_2 in files_in_dir2:
            if (range_file_1 == range_file_2):
                list_values = []
                monkey_test_success = monkey_test_success + 1
                int_count_lines_1 = countLines(path1+range_file_1)
                int_count_lines_2 = countLines(path2+range_file_2)
                count_difference = 'sdiff -B -b -s '+ path1 + range_file_1 +' '+ path2 +range_file_1 +' | wc -l'
                int_count_difference = int(subprocess.check_output(count_difference, shell = True))
                percentage_run_1 = (int_count_difference/int_count_lines_1) * 100
                percentage_run_1 = float("{:.2f}".format(percentage_run_1))
                if(percentage_run_1 <= PASS_PERCENT):
                    count_low = count_low + 1
                list_values = [range_file_1, int_count_lines_1, int_count_lines_2, 
                               int_count_difference, percentage_run_1]
                df.loc[len(df.index)] =list_values 
    monkey_test_failed = (len(files_in_dir1) - monkey_test_success) + (len(files_in_dir2) - monkey_test_success)
    monkey_tested_files = monkey_test_success + monkey_test_failed
    total_failed_apk = len([files_ for files_ in listdir(INPUT_APK_FOLDER) if isfile(join(INPUT_APK_FOLDER , files_))]) - monkey_tested_files 
    log("Monkey Test Success - " + str(monkey_test_success), PRINT_TO_SCREEN)
    log("Monkey Test Failed  - " + str(monkey_test_failed), PRINT_TO_SCREEN)
    log("Total Failed APKs   - " + str(total_failed_apk), PRINT_TO_SCREEN)
    log("Total number of apks with percentage difference less than " + str(PASS_PERCENT) + "% is " + str(count_low), PRINT_TO_SCREEN)
    #df_low_15 = df[(df['Percentage_difference'] <= 15.0)]
    df.to_csv(COMPARISON_OUTPUT_FOLDER +csv_name, index = False)
    #df_low_15.to_csv(COMPARISON_OUTPUT_FOLDER + "df_low_15.csv", index = False)
    log("The detail comparison report can be found in " + COMPARISON_OUTPUT_FOLDER + csv_name , PRINT_TO_SCREEN)

def check_adb():
    if which('adb') is None:
        log("ADB not found in path", PRINT_TO_SCREEN)
        sys.exit(1)
    else:
        log("ADB found", PRINT_TO_SCREEN)

def main():
    """ Handle flow of the tool """
    init_argparse()

    global emulator

    #check file logging
    if ENABLE_FILE_LOGGING:
        logging.basicConfig(filename=LOG_FILE,
              format='%(asctime)s %(message)s', filemode='w')

    #check android sdk and emulator
    if emulator == "":
        log("No emulator specified.", PRINT_TO_SCREEN)
        sys.exit(0)
    else:
        log("Emulator is specified.", 0)
        check_android_emulator()

    check_adb()

    adb_kill_proc = subprocess.Popen("adb kill-server",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    adb_kill_status, err = adb_kill_proc.communicate()
    sleep(5)
    log("Killing adb:  " + str(adb_kill_status.decode()) + "\n" + str(err.decode()), 0)



    adb_kill_proc = subprocess.Popen("adb start-server",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    adb_kill_status, err = adb_kill_proc.communicate(timeout=20)
    sleep(5)
    log("Starting adb:  " + str(adb_kill_status.decode()) + "\n" + str(err.decode()), 0)

    parse_csv()

    #create folder for csv saving
    if not os.path.exists(TEMP_INPUT_CROP_FOLDER1 ):
        os.makedirs(TEMP_INPUT_CROP_FOLDER1 )
    if not os.path.exists(TEMP_INPUT_CROP_FOLDER2 ):
        os.makedirs(TEMP_INPUT_CROP_FOLDER2 )
    if not os.path.exists(COMPARISON_OUTPUT_FOLDER ):
        os.makedirs(COMPARISON_OUTPUT_FOLDER)

    files_in_dir_1 = [files_1 for files_1 in listdir(INPUT_APKS_RESULT ) if isfile(join(INPUT_APKS_RESULT , files_1))]
    files_in_dir_2 = [files_2 for files_2 in listdir(MODIFIED_APKS_RESULT ) if isfile(join(MODIFIED_APKS_RESULT , files_2))]

    if(len(files_in_dir_1)>0 and len(files_in_dir_2)>0):
        log("Removing \"system_uptime\" from the monkey log files", PRINT_TO_SCREEN)
        for range_file_1 in files_in_dir_1:
            subprocess.run('grep -vwE "system_uptime" '+ INPUT_APKS_RESULT + 
                    range_file_1 +' > '+ TEMP_INPUT_CROP_FOLDER1 +
                    range_file_1 , shell = True)
        for range_file_2 in files_in_dir_2:
            subprocess.run('grep -vwE "system_uptime" '+ MODIFIED_APKS_RESULT + 
                    range_file_2 +' > '+ TEMP_INPUT_CROP_FOLDER2 +
                    range_file_2 , shell = True)

        log("Generating the comparison report", PRINT_TO_SCREEN)
        generate_csv(TEMP_INPUT_CROP_FOLDER1, TEMP_INPUT_CROP_FOLDER2 , "comparison_report.csv")

        #remove temp dirs
        shutil.rmtree(TEMP_INPUT_CROP_FOLDER1)
        shutil.rmtree(TEMP_INPUT_CROP_FOLDER2)
    else:
        log("No files found in directories", PRINT_TO_SCREEN)

    #APK generated
    log("Execution completed",PRINT_TO_SCREEN)

if __name__ == '__main__':
    main()


