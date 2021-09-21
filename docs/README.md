GANG-MAM is an automated tool aiming at making existing malware strongly evasive, namely GAN Generated malware for Modifying Android Malware (GANG-MAM), based on a GAN engine. The tool consists of two parts: the GANG that produces an evasive features vector and the MAM that accordingly modifies the existing malware, preserving its malicious behaviour

-------------
DEPENDENCIES 
-------------

	1. Programming dependencies

		a. Python3 (version 3.6+)

		b. Machine learning packages: 
            i. Tensorflow (version 2.4.1)
           ii. Keras (version 2.4.3)
          iii. Scikit-learn (version 0.23.1)
           iv. Matplotlib (version 3.2.2)
            v. Xgboost (version 1.4.2)

		c. Other Python packages: ElementTree, numpy, pandas, pickle, 
            logging, argparse, subprocess, os, sys, time, warning & shutil

	2. System dependencies

		a. Ubuntu 18.04
		b. Virtualization support
		c. RAM 8GB or more

	3. External dependencies

		a. Apktool (version 2.5.0)
		b. QEMU emulator (version 2.11.1)
        c. Android Studio (version ):
			  i. Android Emulator (version 30.7.5.0)
			 ii. Android SDK Tools (version 26.1.1)
			iii. Android SDK Platform-Tools (version 29.0.5)
		d. AAPT (version 0.2-27.0.1)
		e. Java (version 1.8)

------
SETUP
------

	The tool requires all the dependencies mentioned in the previous section
for its operation. The following describes how to install these dependencies in
an Ubuntu 18.04 OS with virtualization enabled.

	1. Python3	

		$ sudo apt install python3.8
		or download from link: https://www.python.org/downloads/

        Packages:

        $ pip3 install tensorflow==2.4.1
		$ pip3 install keras==2.4.3
		$ pip3 install scikit-learn==0.23.1
		$ pip3 install matplotlib==3.2.2
		$ pip3 install xgboost==1.4.2
		$ pip3 install numpy
		$ pip3 install pandas
		$ pip3 install pickle

	2. Apktool

		a. Save the contents from https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool
            as "apktool"
        b. Download apktool v2.5.0. from https://bitbucket.org/iBotPeaches/apktool/downloads/
        c. Rename downloaded jar to apktool.jar
        d. Move both files (apktool.jar & apktool) to /usr/local/bin (root needed)
        e. Make sure both files are executable (chmod +x)
        f. Try running "apktool -version" via command line

	3. QEMU
	
		$ sudo apt install qemu-kvm qemu

	4. Virtualization

		$ sudo apt install cpu-checker
		$ kvm-ok
		   
		The result "INFO: /dev/kvm exists. KVM acceleration can be used" ensures that virtualisation is 
		enabled and can be used. For more info, refer: https://developer.android.com/studio/run/emulator-acceleration#vm-linux

	5. Android Studio

        a. Download Android Studio from https://developer.android.com/studio
        b. Extract and navigate to the folder and run
            $ cd <path_to_extracted_folder>/bin
            $ ./studio.sh

    6. Android SDK & Emulator

		a. Launch Android studio by navigating to the extracted folder and run 
			$. ./studio.sh
			
		b. Follow the steps in link to install Android SDK and Emulator from the Android studio:
			https://developer.android.com/studio/intro/update#sdk-manager

	7. Creating an AVD
		
		a. Steps to create an AVD can be found in https://developer.android.com/studio/run/managing-avds#createavd
           The following are the avd details used for testing the tool:
        
            Device: Pixel 4a
            System Image: 
                Release name: R
                API level: 30
                ABI: x86_64
                Target: Android 11.0 (Google APIs)

		b. Try launching the emulator from the tools > avdmanager tab in Android Studio to ensure that its working.
		    
		c. Some of the common errors encountered and its solution are given below:
		
			i. Android studio shows permission denied for /dev/kvm
				- Add user to the group
					$ sudo adduser $USER kvm
				- Logout and log in 
				- Try launching emulator again
				
			ii. Emulator settings
				- From within the avdmanager in Android studio, choose the emulator to be modified
				- Click on edit option in "Actions" menu
				- Click on advanced options
				- Set "Boot option" to "Quick boot"
				- Set "Emulated graphics" to "software"
		
	8. AAPT

		$ sudo apt install aapt

	9. JAVA 1.8

		$ sudo apt install openjdk-8-jdk

After installing the required packages, ensure that the Android emulator, aapt and apktool is available
from the terminal. This can be verified by running the following commands from the terminal:

	$ emulator -version
	$ aapt version
	$ apktool -version

If any of the command returns error, export the path of the install files. The Android tools can be found in ~/Android/Sdk/ 
Example:
 
	$ export PATH=~/Android/Sdk/platform-tools:~/Android/Sdk/emulator:$PATH

---------------
DIRECTORY TREE
---------------

	By default, the tool assumes the following folder structure exists for 
	its operation:

	.
	├── input			
	│   │							
	│   ├── apks						    --> Input folder for APK(s)
	│   │   ├── 09edb4...8de.apk		    --> Sample APK to be modified
	│   │   └── 61bad9...92a.apk
	│   │
	│   ├── feature_vector
	│   │   └── input.csv				    --> Input CSV file created from static features of the APKS
	│   │
	│   ├── no_gan_feature_vector
	│   │   └── input.csv				    --> Input CSV file for running the No GAN mode
	│   │
	│   └── src						        --> Source folder of the input section of the tool
	│       ├── create_unique_lists.py
	│       ├── create_vectors.py
	│       ├── main.py
	│       └── static_code_capturing.sh
	│	
	├── GANG
	│	│
	│	├── src						        --> Source folder of the feature vector modification engine
	│	│   ├── gan                 	    --> Folder for GAN binaries
	│	│   ├── blackboxmodel          	    --> Folder for blackbox model binaries
	│	│   ├── feature
	│	│   └── modified_feature_vector.py
	│	│
	│	└── modified_feature_vector			--> Folder to store the modified csvs
	│   	└── input.csv					--> CSV generated from the pre-trained GAN model
	│
    ├── MAM
    │   │
    │   ├── intermediates          	        --> Intermediate smali files used in processing
    │   │   ├── dummy_activity.smali
    │   │   ├── dummy_provider.smali
    │   │   ├── dummy_receiver.smali
    │   │   └── dummy_service.smali
    │   │
    │   └── src						        --> Source folder of the APK modification engine
    │       ├── main.py
    │       └── myKeyStore.jks
	│	
    ├── validation
    │   │
    │   ├── monkey
    │   │   ├── comparison			        --> Monkey comparison report of input and modified apks
    │   │   ├── input_apks_result			--> Monkey testing logs of input APKs
    │   │   ├── modified_apks_result		--> Monkey testing logs of modified APKs
    │   │   └── src						    --> Source folder for Monkey testing
    │   │
    │   └── vt
    │       ├── input_apks_result
    │       ├── modified_apks_result
    │       └── src
	│	
    ├── output
    │   │
    │   ├── apks				        	--> Output folder for the APKs
	│   │   ├── 09edb4...8de_A.apk	        --> Modified APK(s)
	│   │   └── 61bad9...92a_A.apk
    │   │
    │   └── logs    			    		--> Output folder for the storing runtime logs
	│	
    ├── docs
	│	
    └── run.sh						        --> Driver script for running the Modification framework

--------------
COMPILE & RUN 
--------------

	To run the tool, open a terminal and navigate to the root folder. Issue the following command to
run the tool.

	$ chmod +x run.sh
    $ chmod +x ./input/src/static_code_capturing.sh
    $ ./run.sh -e <emulator_name>

------
USAGE
------

	$ ./run.sh -h

	Version  1.0

	Usage: ./run.sh -e <emulator_name> [-c] [-n]
		-e Name of the emulator
    	-c Clean all output folder before starting the tool
		-n Path of the feature vector file to run in No GAN mode
		-v Print current tool version
		-h help message
		
	The emulator to be used for testing the modified APKS can be passed to the tool
	using the '-e' flag. The tool checks for the name of the emulator in the 
	available emulator list, and if found will use it for testing the APKS.
	To see the availble list of AVDs present, use 

		$ emulator -list-avds

	Sample usage of the '-e' flag :

		$ ./run.sh -e Nexus_4a

	To run the tool without feature vector generation (GAN model), use
	the '-n' option. The feature vector to be used should be present in the 
	'input/no_gan_feature_vector' folder.

		$ ./run.sh -e Nexus_4a -n 

    To clean all the output folders before running the tool use '-c' flag:

        $ ./run.sh -c

-------------------------
GANG-MAM FRAMEWORK USAGE
-------------------------

	The purpose of the tool is to generate and modify the static features of the input APKs 
	and to subsequently test the modified APKS in an Android emulator. The steps described 
	below illustrates how to achieve this:

		1. Place all the APKs to be modified in the 'input/apks' folder
		2. Open a terminal and navigate to the root folder of the tool
		3. Ensure that the Android emulator, aapt and apktool are accessible from the terminal.
		4. Choose an emulator to test the modified APKs. Available emulators can be found using
			'emulator -list-avds' command.
		5. Run the tool:
			$ ./run.sh -e <emulator_name>
		6. Once the modifications and testing are completed, the generated apks can be found
			in 'output/apks' folder.


