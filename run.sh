#!/bin/bash

version=1.0 
no_gan_flag=false
no_gan_csv=""

clean_flag=false
emulator_flag=false

versionmsg()
{
   echo "Version " $version
}

usage()
{
   echo ""
   echo "Usage: $0 -e <emulator_name> [-c] [-n]"
   echo -e "\t-e Name of the emulator"
   echo -e "\t-c Clean all output folder before starting the tool"
   echo -e "\t-n Path of the feature vector file to run in No GAN mode"
   echo -e "\t-v Print current tool version"
   echo -e "\t-h help message"
   exit 1
}

clean_folders()
{
    rm -f ./input/feature_vector/*
    rm -f ./GANG/modified_feature_vector/*
    rm -rf ./output/apks/*
    rm -f ./output/logs/*
    clean_logs
}

clean_logs()
{
    rm -f ./validation/monkey/comparison/*
    rm -f ./validation/monkey/input_apks_result/*
    rm -f ./validation/monkey/modified_apks_result/*
}

while getopts "ce:vnh" opt
do
   case "$opt" in
      e ) emulator="$OPTARG" 
          emulator_flag=true ;;
      n ) no_gan_flag=true ;;
      c ) clean_flag=true ;;
      h ) usage ;;
      v ) versionmsg 
          exit 1;;
      ? ) usage ;;
      :) echo "missing argument for -%s\n" "$OPTARG" >&2
          usage;;
	  *) echo "Invalid option " "$OPTARG"
		  usage;;
   esac
done
shift $((OPTIND-1))

if $clean_flag; then
    
    clean_folders
    
    if $emulator_flag || $no_gan_flag; then
        :
    else
        echo "Output folders cleared"
        exit 1
    fi
fi

# mandatory arguments
if [ ! "$emulator" ] ; then
    echo "Emulator name must be provided"
    usage
fi

echo "******************* 
*   Version 1.0   *         
*******************"

echo "Cleaning output log folders"
clean_logs

if $no_gan_flag ; then
    cp ./input/no_gan_feature_vector/* ./GANG/modified_feature_vector/
    echo "Skipping feature extraction and geneartion using GAN model"
    echo ""
else
    echo "Executing Input module"
    cd  ./input/src
    python3 main.py
    cd ../../

    echo ""
    echo "Applying ML algorithm"
    cd ./GANG/src
    source AAT/bin/activate
    python3 modifiy_feature_vectors.py ./../../input/feature_vector/input.csv
    deactivate
    cd ../../
fi

echo ""
echo "Executing APK Modification Engine"
cd  ./MAM/src
python3 main.py
cd ../../

echo ""
echo "Validating the APKS"
cd ./validation/monkey/src
python3 main.py -e $emulator
cd ../../


echo ""
echo "DONE!"
