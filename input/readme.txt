---------------------------
GANG-MAM Framework - Input
---------------------------

	This section describes how to configure the input for the Android Automation Framework.
	The tree diagram of the input subsection is as follows:
	
	input
	│
	├── apks
	│   ├── 30f0543918729e06d26aa9275ec654244cffb9f39251a560de49cdc44c5dd749.apk   	=> Sample apks
	│   └── 61bad95f8bdc1493bca5b0398c6364d3aff4bccec8ba8686c37ad31cbfa7f92a.apk
	│
	├── feature_vector
	│   └── input.csv						=> Feature vector generated from the sample apks
	│
	├── readme.txt
	│
	└── src									=> Source files for the input framework
	    ├── create_unique_lists.py
	    ├── create_vectors.py
	    ├── main.py
    	└── static_code_capturing.sh

------
Usage
------

	$. cd  input/src
	$. python3 main.py

