#!/bin/bash

#echo -e " Displaying Package Info in AndroidManifest.xml..."
echo -e " Package : " >> $1/Static_Features.txt
grep -oP 'package=.*" ' $1/AndroidManifest.xml | sort -u >> $1/Static_Features.txt
echo -e "  " >> $1/Static_Features.txt

#echo -e " Displaying Activities in AndroidManifest.xml..."
echo -e " Activities : " >> $1/Static_Features.txt
grep -oP 'activity.*" ' $1/AndroidManifest.xml  | cut -f -1  | sort -u >> $1/Static_Features.txt
echo -e "  " >> $1/Static_Features.txt

#echo -e " Displaying Services AndroidManifest.xml..."
echo -e " Services : " >> $1/Static_Features.txt
grep -oP 'service .*"' $1/AndroidManifest.xml | sort -u >> $1/Static_Features.txt
echo -e "  " >> $1/Static_Features.txt

#echo -e " Displaying Content Providers in AndroidManifest.xml..."
echo -e " Providers : " >> $1/Static_Features.txt
grep -oP 'provider .*"' $1/AndroidManifest.xml | sort -u >> $1/Static_Features.txt
echo -e "  " >> $1/Static_Features.txt

#echo -e " Displaying Broadcast Receivers in AndroidManifest.xml..."
echo -e " Receivers : " >> $1/Static_Features.txt
grep -oP 'receiver .*"' $1/AndroidManifest.xml | sort -u >> $1/Static_Features.txt
echo -e "  " >> $1/Static_Features.txt

#echo -e " Displaying Intent Filter Actions in AndroidManifest.xml..."
echo -e " Intents Action : " >> $1/Static_Features.txt
grep -oP 'action.*".*"' $1/AndroidManifest.xml | sort -u >> $1/Static_Features.txt
echo -e "  " >> $1/Static_Features.txt

#echo -e " Displaying Intent Filter Categories in AndroidManifest.xml..."
echo -e " Intents Category : " >> $1/Static_Features.txt
grep -oP 'category.*"' $1/AndroidManifest.xml | sort -u >> $1/Static_Features.txt
echo -e "  " >> $1/Static_Features.txt

#echo -e " Displaying Permissions in AndroidManifest.xml..."
echo -e " Permissions : " >> $1/Static_Features.txt
grep -oP 'permission.*"' $1/AndroidManifest.xml  | sort -u >> $1/Static_Features.txt
echo -e "  " >> $1/Static_Features.txt

#echo -e " Displaying Exports in AndroidManifest.xml..."
echo -e " Exported : " >> $1/Static_Features.txt
grep -oP 'exported="true".*"' $1/AndroidManifest.xml | sort -u >> $1/Static_Features.txt
echo -e "  " >> $1/Static_Features.txt

#echo -e " Displaying Backups in AndroidManifest.xml..."
echo -e " Backup : " >> $1/Static_Features.txt
egrep -o 'allowBackup.*" ' $1/AndroidManifest.xml | sort -u >> $1/Static_Features.txt
echo -e "  " >> $1/Static_Features.txt

#echo -e " Displaying meta-data in AndroidManifest.xml..."
echo -e " Meta-Data : " >> $1/Static_Features.txt
grep -oP 'meta-data.*"' $1/AndroidManifest.xml | sort -u >> $1/Static_Features.txt
echo -e "  " >> $1/Static_Features.txt

#echo -e " Displaying uses-features in AndroidManifest.xml..."
echo -e " Uses-Features : " >> $1/Static_Features.txt
egrep -i 'uses-features.*"' $1/AndroidManifest.xml | sort -u >> $1/Static_Features.txt
echo -e "  " >> $1/Static_Features.txt

#echo -e " Displaying Number of icons..."
echo -e " Number of Icons : " >> $1/Static_Features.txt
find $1/ -iname "*.png" -type f -printf '.' | wc -c  >> $1/Static_Features.txt
echo -e "  " >> $1/Static_Features.txt

#echo -e " Displaying Number of Pictures..."
echo -e " Number of Pictures : " >> $1/Static_Features.txt
find $1/* -iname "*.jpg" -type f -printf '.' | wc -c  >> $1/Static_Features.txt
echo -e "  " >> $1/Static_Features.txt

#echo -e " Displaying Number of Audio..."
echo -e " Number of Audio : " >> $1/Static_Features.txt
find $1/* -iname "*.mp3" -type f -printf '.' | wc -c  >> $1/Static_Features.txt
echo -e "  " >> $1/Static_Features.txt

#echo -e " Displaying Number of Videos..."
echo -e " Number of Videos : " >> $1/Static_Features.txt
find $1/* -iname "*.mp4" -type f -printf '.' | wc -c  >> $1/Static_Features.txt
echo -e "  " >> $1/Static_Features.txt

#echo -e " Displaying Size of the App..."
echo -e " Size of the App : " >> $1/Static_Features.txt
du -sh $1/ | cut -f -1 >> $1/Static_Features.txt
echo -e "  " >> $1/Static_Features.txt

#echo -e " DONE!"
