#importing libraries
import numpy as np
import pandas as pd
import pickle5 as pickle 
from blackboxmodel import blackboxdetector
import os
import warnings
import sys
from keras.models import load_model
import tensorflow as tf
#ignore warning
if not sys.warnoptions:
    warnings.simplefilter("ignore")
    warnings.filterwarnings('ignore')
tf.get_logger().setLevel('ERROR')
    
#class 
class Gan():
        def __init__(self, sysArgs):
            #path
            self.input_or_model_path = 'gan/'
            self.output_or_csv_path = '../modified_feature_vector/'
            self.black_box_model_path = 'blackboxmodel/'
            self.feature_path = 'feature/'

            self.dataset_test = sysArgs[1]
            self.black_box_type = 0 
            self.csv_writing = 1
            self.noise_dimension = 2434
            
            #load features 
            with open (self.feature_path +'feature_list', 'rb') as fp:
                self.featurelist_train = pickle.load(fp)
                
            # load blackbox_detector
            if(self.black_box_type == 0):
                self.blackbox_detector = blackboxdetector
            self.generator = load_model(self.input_or_model_path +'Generator_model_gan_.h5', compile = False)
            #create folder for csv saving
            if not os.path.exists(self.output_or_csv_path):
                os.makedirs(self.output_or_csv_path)
        
        #dataframe to csv
        def to_CsvFormat(self, dataframe, csvName, index_csv = False):
            dataframe.to_csv(self.output_or_csv_path+ csvName+".csv", index = index_csv )
                
        #testing
        def test(self):
            dataFrame_Test = pd.read_csv(self.dataset_test) 
            df1 = pd.DataFrame()
            feature_dataset_train = self.featurelist_train
            df_test_category = dataFrame_Test.select_dtypes(exclude =["number"])
            for index_feat in range(len(feature_dataset_train)):
                if(feature_dataset_train[index_feat] in dataFrame_Test):
                    df1[feature_dataset_train[index_feat]] =  dataFrame_Test[feature_dataset_train[index_feat]].values

                else:    
                    df1[feature_dataset_train[index_feat]] = np.zeros((dataFrame_Test.shape[0],), dtype=int)
            dataFrame_Test = df1
            #droping Categorical feature
            df_test = dataFrame_Test.select_dtypes("number")
            if('apk_name' in df_test ):
                df_test = df_test.drop(['apk_name'], axis =1)
            if('apkname' in df_test ):
                df_test = df_test.drop(['apkname'], axis =1)
            if('SHA256' in df_test ):
                df_test = df_test.drop(['SHA256'], axis =1) 
                
            shape_dataSet_test = df_test.shape[1] - 1            
            shape_dataSet_category_test = df_test_category.shape[1] - 1
            df_test_categoryNumpy = df_test_category.values
            if('Class' in df_test ):
                xmal_test = df_test.drop(['Class'], axis = 1)
                ymal_test = df_test['Class']
            else:
                xmal_test = df_test
                ymal_test = np.ones(df_test.shape[0])
            #extracting feature names
            featureList_test = list(xmal_test.columns.values)
            xmal_test  = xmal_test.values
            input_test_score = self.blackbox_detector.score(xmal_test, ymal_test.values)
            #modifying features
            for index_df in range(df_test.shape[0]): 
                TPR = 1
                loopLimit = 100
                while(TPR == 1 and loopLimit != 0):
                    noise = np.random.normal(0, 1, (1, self.noise_dimension))
                    gen_examples = self.generator.predict([xmal_test[[index_df]], noise])
                    #converting/rounding to zero/one
                    gen_examples = np.ones((gen_examples.shape), dtype=int) *(gen_examples > 0.7)
                    TPR = self.blackbox_detector.score(gen_examples, [1])
                    loopLimit = loopLimit - 1
                trainPredicted_ylabel = self.blackbox_detector.predict(gen_examples)
                ytrain_mal_df = pd.DataFrame(ymal_test, columns = ['Class'])
                dataFrameIndex = list(ymal_test.index.values)
                dataFrameIndex_I = dataFrameIndex[index_df]
                gen_examples_train_df = pd.DataFrame(gen_examples, columns = featureList_test)
                trainPredicted_ylabel_df = pd.DataFrame(trainPredicted_ylabel, columns = ['Class'])
                xtrain_mal_with_apkname_df = pd.DataFrame(dataFrame_Test,index = [dataFrameIndex_I])
                gan_final_train_df = pd.concat([gen_examples_train_df, trainPredicted_ylabel_df], axis=1)
                if(shape_dataSet_category_test>= 0):
                    if(shape_dataSet_category_test == 0):
                        gan_final_train_df["apk_name"] = df_test_categoryNumpy[index_df]
                if(index_df == 0):
                    result_gan_final_train_df = gan_final_train_df
                    result_xtrain_mal_with_apkname_df = xtrain_mal_with_apkname_df
                else:
                    result_gan_final_train_df = result_gan_final_train_df.append(gan_final_train_df, sort=False)
                    result_xtrain_mal_with_apkname_df = result_xtrain_mal_with_apkname_df.append(xtrain_mal_with_apkname_df, sort=False)
                    result_gan_final_train_df_drop = result_gan_final_train_df.drop(['Class'], axis =1)
            result_gan_final_train_df_drop_final = result_gan_final_train_df_drop.reindex(columns=(['apk_name'] + list([sFeature for sFeature in result_gan_final_train_df_drop.columns if sFeature != 'apk_name']) ))
            if(self.csv_writing == 1):
                #self.to_CsvFormat(result_xtrain_mal_with_apkname_df, "input_feature_vectors")
                self.to_CsvFormat(result_gan_final_train_df_drop_final, "modified_feature_vectors")
            
            print('Actual_TPR before Modifying: {0}'.format(input_test_score))
            if("Class" in result_gan_final_train_df):
                print("___TPR after Modifying___")
                print("Total Count ", index_df+1)
                print("Benign Count ",(result_gan_final_train_df["Class"] == 0).sum())
                print("Malware Count ",(result_gan_final_train_df["Class"] != 0).sum())
                

if __name__ == "__main__":
        #create object
        ganObject = Gan(sys.argv)
        ganObject.test()
    

