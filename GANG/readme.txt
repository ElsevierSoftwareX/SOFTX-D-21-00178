
----------------------------------------------------
GANG Framework - Feature Vector Modification Engine 
----------------------------------------------------

	This section describes how feature vectors are modified in the 
    the Android Automation Framework. The tree diagram is as follows:
	
	GANG
	│
	├── src					
	│   ├── gan                              => Folder for GAN binaries
	│   │   └─generator_model_gan_.h5
	│   │
	│   ├── blackboxmodel                    => Folder for blackbox model binaries
	│   │   ├──blackboxdetector.py           => python program to 'OR' models 
	│   │   ├──blackbox_svm_model.pickle
	│   │   ├──blackbox_rf_model.pickle
	│   │   ├──blackbox_xgBoost_model.pickle
	│   │   ├──blackbox_dt_model.pickle
	│   │   ├──blackbox_lr_model.pickle
	│   │   └──blackbox_1d_cnn.h5
	│   │
	│   ├── feature
	│   │   └──feature_list
	│   │
	│   └── modified_feature_vector.py
	│
	├── modified_feature_vector					=> Folder to store the modified csvs
	│
	└── readme.txt
	
------
Usage
------

	$. cd  GANG\src
	$. python modifiy_feature_vectors.py <path to csv file>
