import re
import csv
import sys
import os

def csv_gen(txt_file, folder):
    header = []
    Feature = []
    name = ""

    with open(txt_file, 'rt') as myfile:
        for myline in myfile:
            Feature.append(myline.rstrip('\n').rstrip(' '))

    end = folder
    sp1 = txt_file.split(end)
    sp2 = sp1[1].split('_A')

    Activities = []
    for index, line in enumerate(Feature):
        if " Activities :" in str(line):
            for a in range(index + 1, index + 100):
                if len(Feature[a]) == 0:
                    break
                else:
                    try:
                        act = re.search(r'android:name="([^"]*)"', Feature[a]).group(1)
                        Activities.append(act)
                    except:
                        #print(" None !!!!! ")
                        pass

    Services = []
    for index, line in enumerate(Feature):
        if " Services :" in str(line):
            for a in range(index + 1, index + 100):
                if len(Feature[a]) == 0:
                    break
                else:
                    try:
                        serv = re.search(r'(\w+)Service', Feature[a]).group(1)
                        Services.append(serv + "Service")
                    except:
                        #print(" None !!!! ")
                        pass

    Permissions = []
    for index, line in enumerate(Feature):
        if " Permissions :" in str(line):
            for a in range(index + 1, index + 100):
                if len(Feature[a]) == 0:
                    break
                else:
                    try:
                        perm = re.search(r'".*.permission.([^"]*)"', Feature[a]).group(1)
                        Permissions.append("permission." + perm)
                    except:
                        #print(" None !!!! ")
                        pass

    Actions = []
    for index, line in enumerate(Feature):
        if " Intents Action :" in str(line):
            for a in range(index + 1, index + 100):
                if len(Feature[a]) == 0:
                    break
                else:
                    try:
                        actio = re.search(r'".*.action.([^"]*)"', Feature[a]).group(1)
                        Actions.append("action." + actio)
                    except:
                        #print("None !!!!")
                        pass

    Categories = []
    for index, line in enumerate(Feature):
        if " Intents Category :" in str(line):
            for a in range(index + 1, index + 100):
                if len(Feature[a]) == 0:
                    break
                else:
                    try:
                        cate = re.search(r'".*.category.([^"]*)"', Feature[a]).group(1)
                        Categories.append("category." + cate)
                    except:
                        #print("None !!!!")
                        pass

    Meta = []
    for index, line in enumerate(Feature):
        if " Meta-Data :" in str(line):
            for a in range(index + 1, index + 100):
                if len(Feature[a]) == 0:
                    break
                else:
                    try:
                        met = re.search(r'"([^"]*)"', Feature[a]).group(1)
                        Meta.append(met)
                    except:
                        #print("None !!!!!")
                        pass

    Providers = []
    for index, line in enumerate(Feature):
        if " Providers :" in str(line):
            for a in range(index + 1, index + 100):
                if len(Feature[a]) == 0:
                    break
                else:
                    try:
                        porv = re.search(r'android:name="([^"]*)"', Feature[a]).group(1)
                        Providers.append(porv)
                    except:
                        #print("None !!!!")
                        pass

    receivers = []
    for index, line in enumerate(Feature):
        if " Receivers :" in str(line):
            for a in range(index + 1, index + 100):
                if len(Feature[a]) == 0:
                    break
                else:
                    try:
                        Ress = re.search(r'android:name="([^"]*)"', Feature[a]).group(1)
                        receivers.append(Ress)
                    except:
                        #print("None !!!!")
                        pass

    Hardware = []
    header.append("apk_name")

    Values = []
    Values.append(sp2[0])

    with open('./1_List_Permissions.csv') as csvFile:
        dataPer = csvFile.readlines()

    csvFile.close()
    for i in dataPer:
        if(i.strip() == ""):
            continue
        header.append(i.strip())
        if i.strip() in Permissions:
            Values.append(1)
        else:
            Values.append(0)

    with open('./3_List_Actions.csv') as csvFile:
        dataAct = csvFile.readlines()
    csvFile.close()
    for i in dataAct:
        if(i.strip() == ""):
            continue
        header.append(i.strip())
        if i.strip() in Actions:
            Values.append(1)
        else:
            Values.append(0)

    with open('./2_List_Services.csv') as csvFile:
        dataSer = csvFile.readlines()
    csvFile.close()
    for i in dataSer:
        if(i.strip() == ""):
            continue
        header.append(i.strip())
        if i.strip() in Services:
            Values.append(1)
        else:
            Values.append(0)

    with open('./4_List_Categories.csv') as csvFile:
        dataCat = csvFile.readlines()
    csvFile.close()
    for i in dataCat:
        if(i.strip() == ""):
            continue
        header.append(i.strip())
        if i.strip() in Categories:
            Values.append(1)
        else:
            Values.append(0)

    if not os.path.isfile('./../feature_vector/input.csv'):
        with open('./../feature_vector/input.csv','a') as cs:
            writer = csv.writer(cs)
            writer.writerow(header)

    with open('./../feature_vector/input.csv', 'a+') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(Values)
    csvFile.close()

if __name__ == '__main__':
    input_folder = "./"
    output_folder = "./output"

    for apk_folders in os.listdir(output_folder):
        for files in os.listdir(output_folder + "/" + apk_folders):
            if files.endswith(".txt"):
                csv_gen(output_folder + "/" + apk_folders + "/" + files, output_folder)


