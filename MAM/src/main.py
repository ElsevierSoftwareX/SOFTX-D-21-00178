""" Source code of AAT """
import os
import xml.etree.ElementTree as ET
import subprocess
import argparse
import logging
import hashlib
import sys
import shutil
from time import sleep
from shutil import copyfile

# Global Arguments #
VERSION="1.0"
ENABLE_LOGGING = 1
PRINT_TO_SCREEN = 1
DONT_PRINT_TO_SCREEN = 0
ENABLE_FILE_LOGGING = 1

APKTOOL_VERSION="2.5.0"
APKTOOL_INSTALL ="https://ibotpeaches.github.io/Apktool/install/"

input_csv=""

#folders
INPUT_APKS_FOLDER="./../../input/apks/"
OUTPUT_FOLDER="./../../output/apks/"
APK_FOLDER="./../../output/apks/"
ASSETS_FOLDER="./../intermediates/"

CSV_FOLDER="./../../GANG/modified_feature_vector/"
LOGS_FOLDER ="./../../output/logs/"

#file
LOG_FILE = LOGS_FOLDER + "modification_engine_log.txt"
FAILED_APK_FILE = LOGS_FOLDER + "modification_failed_apks.txt"
XMLNS='{http://schemas.android.com/apk/res/android}'
KEYFILE="myKeyStore.jks"

#commands
KEYSTORE_CMD=["keytool","-genkey","-alias","myDomain","-keyalg","RSA",
"-keysize","2048","-validity","7300","-keystore","myKeyStore.jks",
"-storepass","myStrongPassword"]

# Emulator commands
emulator = ""
APP_INSTALL_CMD = "adb install "
APP_UNINSTALL_CMD = "adb uninstall "

EMULATOR_LAUNCH_CMD = "emulator -avd "
EMULATOR_CLOSE_CMD  = "adb emu kill"
PACKAGE_LAUNCH_COMMAND = "adb shell monkey -p "

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
        log("STDOUT: " + output.stdout, 2)
        log("STDERR: " + output.stderr, 2)
        log("RETURN: " + str(output.returncode), 2)

    return [output.returncode, output.stdout]

def application_child_mod(xml_root, findstr, misc_list):
    """ To modify child elements of <application> in manifest xml file
        Arguments  : xml_root  - root element after ETree parsing
            findstr   - child tag name
            misc_list - data to be modified, in required format
        Returns    : None
    """
    entries = len(misc_list)

    for i in range(0,entries):
        entry = misc_list[i]
        activity_name = entry[0]
        attr = entry[1]
        changed_from = entry[2]
        changed_to = entry[3]

        for ele in xml_root.iter("application"):
            for item in ele.iter(findstr):
                item_name = item.get(XMLNS+"name")
                if item_name == activity_name:
                    attr_val = item.get(XMLNS+attr)
                    if changed_to == 0:
                        changed_to = ""
                        if attr == "name":
                            ele.remove(item)

                    if changed_from == 0:
                        item.set(XMLNS+attr, changed_to)
                    if attr_val == changed_from:
                        item.set(XMLNS+attr, changed_to)
                    break


def parse_csv():
    """ To parse csv file and make changes in apk
        Arguments  : None
        Returns    : None
    """
    count =0
    header = []
    header_def = []
    #total_apk_found = len(apk_hash_list)
    total_apk_found = 0
    for folder in os.listdir(OUTPUT_FOLDER):
        if not folder.endswith(".apk"):
            total_apk_found = total_apk_found + 1

    if total_apk_found == 0:
        log("No apks found in input folder", 1)
        sys.exit(1)

    log(f"{total_apk_found} APK(s) found in apk folder", 1)
    log("Processing APK(s)", 1)

    apk_failed = 0
    apk_success = 0
    apk_missing = 0
    apk_installed = 0
    apk_launched = 0                
    fail_buffer = ""

    with open(input_csv, 'r') as reader:
        for line in reader:
            line_list = line.replace('\n','')
            line_list = line_list.split(',')

            if count == 0:
                header_def = line_list
                count = 1
                continue

            header = []
            header = header_def
            row_length=len(line_list)
            apk_hash = line_list[0]

            #apk_name = apk_hash_list.get(apk_hash)
            apk_name = apk_hash.replace(".apk","")

            #if apk_name is None:
            if not os.path.isdir(OUTPUT_FOLDER + apk_name + "_A"):
                apk_missing = apk_missing + 1
                fail_buffer = fail_buffer + apk_hash + " - " + " apk not found\n"
                log(f"    {apk_name} not found", 1)
                continue

            log(f"    {apk_name}", 1)

            apk_path = os.path.join(OUTPUT_FOLDER, apk_name + "_A")

            apk_name = apk_name.replace(".apk","")
            output_apk_path = os.path.join(OUTPUT_FOLDER, apk_name + "_A")
            manifest_path = os.path.join(output_apk_path, "AndroidManifest.xml")

            tree = ET.parse(manifest_path)
            root = tree.getroot()

            perm_list = []
            for ele in root.iter("uses-permission"):
                attr = ele.get(XMLNS+"name")
                perm_list.append(attr)

            activity_list = []
            service_list = []
            receiver_list = []
            provider_list = []
            action_list = []
            category_list = []
            provider_count = 0

            for apps in root.iter("application"):
                for item in apps.iter("activity"):
                    item_name = item.get(XMLNS+'name')
                    activity_list.append(item_name)

                for item in apps.iter("service"):
                    item_name = item.get(XMLNS+'name')
                    service_list.append(item_name)

                for item in apps.iter("receiver"):
                    item_name = item.get(XMLNS+'name')
                    receiver_list.append(item_name)

                for item in apps.iter("provider"):
                    item_name = item.get(XMLNS+'name')
                    provider_list.append(item_name)

            for ele in root.iter():
                if ele.tag == "application" :
                    apps = ele

            app_package_name = root.get('package')

            log("        Modifying elements", 1)
            for i in range(1,row_length):
                if line_list[i] == '1':
                    log(f"        item {header[i]}, val {line_list[i]}", 0)

                    if "permission." in header[i]:
                        if "android." + header[i] not in perm_list:
                            perm_ele = ET.Element("uses-permission")
                            perm_ele.set(XMLNS+'name', "android." + header[i])
                            perm_ele.tail = "\n    "
                            root.insert(0, perm_ele)
                            log(f"        Inserted {header[i]} in manifest", 0)
                        else:
                            log(f"        {header[i]} already present in manifest file", 0)
                        continue

                    if header[i].endswith('Activity'):
                        rep = header[i].rsplit('Activity', 1)
                        act_name = ''.join(rep)
                        if add_manifest_entry("activity", act_name, activity_list, apps):
                            add_smali(app_package_name, act_name, "activity", output_apk_path)
                        continue

                    if header[i].endswith('Service'):
                        #remove 'Service' from tail end
                        rep = header[i].rsplit('Service',1)
                        serv_name = ''.join(rep)
                        if add_manifest_entry("service", serv_name, service_list, apps):
                            add_smali(app_package_name, serv_name, "service", output_apk_path)
                        continue

                    if header[i].endswith('Receiver'):
                        rep = header[i].rsplit('Receiver',1)
                        recv_name = ''.join(rep)
                        if add_manifest_entry("receiver", recv_name, receiver_list, apps):
                            add_smali(app_package_name, recv_name, "receiver", output_apk_path)
                        continue

                    if "action." in header[i]:
                        action_list.append(header[i])

                    if "category." in header[i]:
                        category_list.append(header[i])

                    if header[i].endswith('Provider'):
                        rep = header[i].rsplit('Provider', 1)
                        prov_name = ''.join(rep)
                        if add_manifest_entry("provider","." + prov_name, provider_list, apps):
                            add_smali(app_package_name, "." +prov_name, "provider", output_apk_path)

                        tree.write(manifest_path, xml_declaration=True, encoding="utf-8")

                        misc_provider = [["." + prov_name, "authorities", 0,
                                                app_package_name + ".provider"
                                                + str(provider_count)]]
                        provider_count = provider_count + 1
                        application_child_mod(root, "provider", misc_provider)

            if len(action_list) > 0:
                add_intent(root, action_list, category_list)

            tree.write(manifest_path, xml_declaration=True, encoding="utf-8")

            if rebuild_apk(output_apk_path):
                apk_failed = apk_failed + 1
                fail_buffer = fail_buffer + apk_name + " - " + " rebuilding failed\n"
            else:

                #sign the modified apk
                if apk_signing(output_apk_path):
                    apk_failed = apk_failed + 1
                    fail_buffer = fail_buffer + apk_name + " - " + " signing failed\n"
                else:
                    apk_success = apk_success + 1

            #remove apk folder
            shutil.rmtree(output_apk_path)

    log(f"{apk_success}/{total_apk_found} modified, {apk_failed} failed", 1)
    if apk_missing:
        log(f"{apk_missing} apk missing based on csv input", 1)
    else:
        log("Processed all entries from the CSV file", 1)

    with open(FAILED_APK_FILE, "w") as writer:
        writer.write(fail_buffer)

def add_intent(xml_root, actions, categories):
    """ To add intent elements in a dummy service
        Arguments  : xml_root - xml root attribute tag
            actions  - list of action elements in csv
            categories - list of category elements in csv
        Returns    : None
    """
    for items in xml_root.iter():
        if items.tag == "application":
            #add parent service for intent
            service_ele = ET.Element("service")
            service_ele.set(XMLNS+'name', "dummyService")
            service_ele.tail = "\n    "
            service_ele.text="\n\t\t\t"
            items.append(service_ele)

            intent_ele = ET.Element("intent-filter")
            intent_ele.tail = "\n        "
            intent_ele.text = "\n\t\t\t\t"
            service_ele.append(intent_ele)

            for action in actions:
                act_ele = ET.Element("action")
                act_ele.set(XMLNS+'name', "android.intent."+ action)
                act_ele.tail = "\n\t\t\t\t"
                intent_ele.append(act_ele)

            for category in categories:
                cat_ele = ET.Element("category")
                cat_ele.set(XMLNS+'name', "android.intent." + category)
                cat_ele.tail = "\n\t\t\t\t"
                intent_ele.append(cat_ele)

def add_manifest_entry(feature, item, feat_list, etree_ele):
    """ To add application child elements in manifest from csv
        Arguments  : feature   - element type in the manifest application entry
            item      - entry from csv to be added in manifest
            feat_list - list of features from the apps manifest
            etree_ele - xml element to add the item to
        Returns    : None
    """
    flag = 1
    if item not in feat_list:
        new_val = ET.Element(feature)
        new_val.set(XMLNS+'name', item)
        new_val.tail = "\n        "
        etree_ele.append(new_val)
        log(f"        Inserted {item} in manifest", 0)
    else:
        log(f"        {item} already present in manifest file", 0)
        flag = 0

    return flag

def add_smali(package_name, item_name, item_type, path):
    """ To add smali code for the added application child elements
        Arguments  : package_name - Package name of the APK
            item_name    - Name of the element
            item_type    - element type in the manifest application entry
            path         - source path of the APK
        Returns    : None
    """
    folder_name = ""
    item_file_name = item_name.split('.')[-1]

    if item_name.startswith('.'):
        #log("        startswith .", 0)
        folder_name = item_name.replace(item_file_name, "")
        folder_name = folder_name[1:]
        folder_name = package_name + '.' + folder_name
    elif package_name in item_name:
        folder_name = item_name.replace('.' + item_file_name, "")
    else:
        #log("        different package & " + item_type +" name", 0)
        package_name = item_name.replace(item_file_name, "")
        folder_name = package_name

    folder_name = folder_name.replace('.','/')
    package_name = package_name.replace('.','/')

    #create new activity smali file
    original_file = os.path.join(ASSETS_FOLDER, "dummy_" + item_type + ".smali")
    new_temp_file = os.path.join(ASSETS_FOLDER, item_name + "_temp.smali")
    new_file = os.path.join(ASSETS_FOLDER, item_file_name + ".smali")

    copyfile(original_file, new_temp_file)

    with open(new_temp_file, 'r') as reader, \
            open(new_file, 'w') as writer:

        for line in reader:
            if "dummy_" + item_type in line:
                line = line.replace("dummy_" + item_type , item_file_name)

            if "package" in line:
                line = line.replace("package", package_name)

            writer.write(line)

    flag = False
    if item_type == "provider":
        folder_path = os.path.join(path, "smali")
        folder_path = os.path.join(folder_path, package_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        copyfile(new_file, folder_path + '/' + item_file_name + ".smali")
    else:
        for directory in os.listdir(path):
            if "smali" in  directory:
                smali_path = os.path.join(path, directory)
                loc = os.path.join(smali_path, folder_name)
                if os.path.exists(loc):
                    copyfile(new_file,  loc  + '/' + item_file_name + ".smali")
                    log("        Added smali equivalent code", 0)
                    flag = True
                    break

        if not flag:
            log(f"        Couldn't find the output path {loc} to add smali code", 0)

    if os.path.exists(new_temp_file):
        os.remove(new_temp_file)

    if os.path.exists(new_file):
        os.remove(new_file)

def rebuild_apk(out_apk_path):
    """ To rebuild apk using apktool and overwrite if apk exists
        Arguments  : out_apk_path - full path where apk is stored
        Returns    : return code for success/failure
    """
    log("        Rebulding APK", 1)

    res = run_command(["apktool","b",out_apk_path,"-o",out_apk_path+".apk"])
    return res[0]

def apk_signing(out_apk_path):
    """ To resign apk using jarsigner based on keytool generated
        Arguments  : out_apk_path - full path where apk is stored
        Returns    : return code for success/failure
    """
    jarsigner_cmd=["jarsigner","-verbose","-keystore","./myKeyStore.jks",
                            "-storepass","myStrongPassword", "apk", "myDomain"]

    #APK signing
    jarsigner_cmd[6] = out_apk_path + ".apk"

    #rebuild apk
    res = run_command(jarsigner_cmd)

    return res[0]

def check_apktool_version():
    """ To check if apktool exists and verfiy correct version
        Arguments  : None
        Returns    : None
    """
    log("Checking apktool version...", 0)
    res = run_command(['apktool','-version'])
    result = ""
    result = result.join(res[1]).strip('\n')
    if result == APKTOOL_VERSION:
        log("Apktool " + APKTOOL_VERSION + " found", PRINT_TO_SCREEN)
    else:
        log("Kindly install apktool version " + APKTOOL_VERSION + " from "
            + APKTOOL_INSTALL, PRINT_TO_SCREEN)
        sys.exit(0)

def validate_csv():
    """ To check if entries in csv are correct
        Arguments  : None
        Returns    : None
    """

    global input_csv

    line_no = 0
    entry_count = 0
    log("Validating the input CSV...", 0)

    with open(input_csv, 'r') as reader:
        for line in reader:

            line = line.strip("\n")
            if not line.endswith(","):
                line = line + ','

            line = line[:-1]
            header_list = line.split(',')
            header_list = header_list[1:]

            if line_no == 0:
                entry_count = len(header_list)

                for header_entry in header_list:
                    if( header_entry.startswith("permission.") or \
                        header_entry.endswith("Activity") or \
                        header_entry.endswith("Service") or \
                        header_entry.endswith("Receiver") or \
                        header_entry.endswith("Provider") or \
                        header_entry.startswith("action.") or \
                        header_entry.startswith("category.") ):
                        pass
                    else:
                        print("Header value is incorrect: " + str(header_entry))
                        sys.exit(0)
            else:
                diff = entry_count - len(header_list)
                if diff > 0:
                    print("Entry " + str(line_no) + " has " + str(diff) + " entry missing")
                    sys.exit(0)
                elif diff < 0:
                    print("Entry " + str(line_no) + " has " + str(abs(diff)) + " extra entry")
                    sys.exit(0)
                else:
                    pass

                for header_entry in header_list:
                    if header_entry in ('0', '1'):
                        pass
                    else:
                        print("Invaid entry \"" + str(header_entry) + "\" in line " + str(line_no))
                        sys.exit(0)

            line_no = line_no + 1

    log("Input CSV validated successfully", 1)

def check_def_folders():
    """ To check if default folders for the tool are present
        Arguments  : None
        Returns    : None
    """

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    if not os.path.exists(LOGS_FOLDER):
        os.makedirs(LOGS_FOLDER)

    if not os.path.exists(APK_FOLDER):
        print("Input APK folder not found. Create folder: " + APK_FOLDER +\
                " and add APK(s) into it")
        sys.exit(0)

    if input_csv == "":
        if not os.path.exists(CSV_FOLDER):
            print("Input csv folder not found. Create folder: " + \
                CSV_FOLDER + " or use '-c' option ")
            sys.exit(0)

    if not os.path.exists(ASSETS_FOLDER):
        print("Intermediates folder not found. sys.exiting application")
        sys.exit(0)
    else:
        if( not os.path.exists(ASSETS_FOLDER + "/dummy_activity.smali") or \
            not os.path.exists(ASSETS_FOLDER + "/dummy_service.smali") or \
            not os.path.exists(ASSETS_FOLDER + "/dummy_receiver.smali") or \
            not os.path.exists(ASSETS_FOLDER + "/dummy_provider.smali") ):
            print("Smali equivalents not found. sys.exiting application")
            sys.exit(0)

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

def decode_apks():
    count = 0
    for files in os.listdir(INPUT_APKS_FOLDER):
        if files.endswith(".apk"):
            apk_path = os.path.join(INPUT_APKS_FOLDER, files)
            if load_apk(apk_path) == 0:
                log("    Decoded " + files, 1)
                count = count + 1
    log("    " + str(count) + " files decoded\n", 1)
    
    if count > 0:
        pass
    else:
        log("No APKs decoded", 1)
        sys.exit(0)

def main():
    """ Handle flow of the tool """

    global input_csv

    check_def_folders()

    csv_count = 0
    if input_csv == "":
        for files in os.listdir(CSV_FOLDER):
            if files.endswith(".csv"):
                csv_count = csv_count + 1
                input_csv = os.path.join(CSV_FOLDER,files)

        if csv_count > 1:
            print("Too many csv found in folder.")
            sys.exit(0)

        if csv_count == 0:
            print("No CSV found in folder.")
            sys.exit(0)

    #check file logging
    if ENABLE_FILE_LOGGING:
        logging.basicConfig(filename=LOG_FILE,
              format='%(asctime)s %(message)s', filemode='w')

    #validate the input csv
    validate_csv()

    #check apktool is present
    check_apktool_version()

    input_dir = os.listdir(INPUT_APKS_FOLDER)
    out_dir = []
    input_items = []

    for files in os.listdir(OUTPUT_FOLDER):
        if not files.endswith(".apk"):
            out_dir.append(files)
        
    if len(input_dir) == 0:
        log("No apks found in input folder", 1)
        sys.exit(0)

    for item in input_dir:
        input_items.append(item.replace(".apk","_A"))

    input_items.sort()
    out_dir.sort()
    if (len(out_dir) == 0) or (input_items != out_dir):
        log("Decoding apks", 1)
        decode_apks()
    else:
        log("Using existing APKs in the output folder", 1)

    #keystore generation
    if os.path.exists(KEYFILE):
        pass
    else:
        run_command(KEYSTORE_CMD)

    log("Loading modifications from CSV file", 1)
    parse_csv()

    #APK generated
    log("Execution completed",PRINT_TO_SCREEN)

if __name__ == '__main__':
    main()
