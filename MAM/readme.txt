----------------------------------------
MAM Framework - APK Modification Engine
----------------------------------------

	This section describes how to configure the APK modification engine for 
    the Android Automation Framework. The tree diagram is as follows:
	
	MAM
	│
	├── intermediates					=> Intermediate smali files used in processing
	│   ├── dummy_activity.smali
	│   ├── dummy_provider.smali
	│   ├── dummy_receiver.smali
	│   └── dummy_service.smali
	│
	├── readme.txt
	│
	└── src								=> Source files for the APK modification engine
    	├── main.py
    	└── myKeyStore.jks

------
Usage
------

	$. cd  MAM
	$. python3 main.py

