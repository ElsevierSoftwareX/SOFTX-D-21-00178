#!/usr/bin/env python
# coding: utf-8
#Program for 'OR' Black Box Detector

import pandas as pd
import pickle5 as pickle
import numpy 
import numpy as np
import keras
from keras.models import Sequential
from keras.layers import Dense, Conv1D, Flatten, MaxPooling1D
from numpy import unique
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
import warnings
import sys
if not sys.warnoptions:
    warnings.simplefilter("ignore")
    
def predict(genVector):
    #svm
    filenameSvm = 'blackboxmodel/blackbox_svm_model.pickle'
    loaded_modelSvm = pickle.load(open(filenameSvm, 'rb'))
    resultSvm = loaded_modelSvm.predict(genVector)

    #rf Model
    filenameRf = 'blackboxmodel/blackbox_rf_model.pickle'
    loaded_modelRf = pickle.load(open(filenameRf, 'rb'))
    resultRf = loaded_modelRf.predict(genVector)

    #xgBoost Model
    filenameXgBoost= 'blackboxmodel/blackbox_xgBoost_model.pickle'
    loaded_modelXgBoost = pickle.load(open(filenameXgBoost, 'rb'))
    resultXgBoost = loaded_modelXgBoost.predict(genVector)

    #dt Model
    filenameDt = 'blackboxmodel/blackbox_dt_model.pickle'
    loaded_modelDt = pickle.load(open(filenameDt, 'rb'))
    resultDt = loaded_modelDt.predict(genVector)

    #lr Model
    filenameLr = 'blackboxmodel/blackbox_lr_model.pickle'
    loaded_modelLr = pickle.load(open(filenameLr, 'rb'))
    resultLr = loaded_modelLr.predict(genVector)
    
    #1D CNN Model
    genVector_cnn = genVector.reshape(genVector.shape[0], genVector.shape[1], 1)
    loaded_modelCnn = keras.models.load_model('blackboxmodel/blackbox_1d_cnn.h5')
    resultCnn_ = loaded_modelCnn.predict(genVector_cnn)
    resultCnn =np.argmax(resultCnn_ , axis=1)

    result = [(resultSvm[i] or resultRf[i] or resultXgBoost[i] or resultLr[i] or resultDt[i] or resultCnn[i] ) for i in range(len(resultSvm))]
    return (numpy.array(result))


#score/accuracy calculation
def score(genVector, vectorLabel):
    #loading model
    #svm
    filenameSvm = 'blackboxmodel/blackbox_svm_model.pickle'
    loaded_modelSvm = pickle.load(open(filenameSvm, 'rb'))
    resultSvm = loaded_modelSvm.predict(genVector)

    #rf Model
    filenameRf = 'blackboxmodel/blackbox_rf_model.pickle'
    loaded_modelRf = pickle.load(open(filenameRf, 'rb'))
    resultRf = loaded_modelRf.predict(genVector)

    #xgBoost Model
    filenameXgBoost= 'blackboxmodel/blackbox_xgBoost_model.pickle'
    loaded_modelXgBoost = pickle.load(open(filenameXgBoost, 'rb'))
    resultXgBoost = loaded_modelXgBoost.predict(genVector)

    #dt Model
    filenameDt = 'blackboxmodel/blackbox_dt_model.pickle'
    loaded_modelDt = pickle.load(open(filenameDt, 'rb'))
    resultDt = loaded_modelDt.predict(genVector)

    #lr Model
    filenameLr = 'blackboxmodel/blackbox_lr_model.pickle'
    loaded_modelLr = pickle.load(open(filenameLr, 'rb'))
    resultLr = loaded_modelLr.predict(genVector)
    
    #1D CNN Model
    genVector_cnn = genVector.reshape(genVector.shape[0], genVector.shape[1], 1)
    loaded_modelCnn = keras.models.load_model('blackboxmodel/blackbox_1d_cnn.h5')
    resultCnn_ = loaded_modelCnn.predict(genVector_cnn)
    resultCnn =np.argmax(resultCnn_ , axis=1)

    result = [(resultSvm[i] or resultRf[i] or resultXgBoost[i] or resultLr[i] or resultDt[i] or resultCnn[i])  for i in range(len(resultSvm))]

    result = numpy.array(result )
    cs = accuracy_score(result , vectorLabel)
    return (cs)
    
#train
def fit(X,y):
    #svm
    classifierSvm = SVC(gamma='scale',kernel='linear',probability=True)
    classifierSvm.fit(X, y) 
    with open("blackboxmodel/blackbox_svm_model.pickle","wb") as file_:
        pickle.dump(classifierSvm, file_, -1)
    
    #rf
    classifierRf = RandomForestClassifier(n_estimators = 300, criterion = 'gini') 
    classifierRf.fit(X, y)
    with open("blackboxmodel/blackbox_rf_model.pickle","wb") as file_:
        pickle.dump(classifierRf, file_, -1)
    
    #xgb classifier
    classifierXgb = XGBClassifier(random_state=42,verbosity = 0)
    classifierXgb.fit(X, y)
    with open("blackboxmodel/blackbox_xgBoost_model.pickle","wb") as file_:
        pickle.dump(classifierXgb, file_, -1)
    
    #lr
    classifierLr = LogisticRegression()
    classifierLr.fit(X, y)
    with open("blackboxmodel/blackbox_lr_model.pickle","wb") as file_:
        pickle.dump(classifierLr, file_, -1)
    
    #dt    
    classifierDt = DecisionTreeClassifier()
    classifierDt.fit(X, y)
    with open("blackboxmodel/blackbox_dt_model.pickle","wb") as file_:
        pickle.dump(classifierDt, file_, -1)
    
    #cnn
    X_ = X.reshape(X.shape[0], X.shape[1], 1)
    modelCnn = Sequential()
    modelCnn.add(Conv1D(64, 2, activation="relu", input_shape=(X.shape[1],1)))
    modelCnn.add(Dense(16, activation="relu"))
    modelCnn.add(MaxPooling1D())
    modelCnn.add(Flatten())
    modelCnn.add(Dense(2, activation = 'softmax'))
    modelCnn.compile(loss = 'sparse_categorical_crossentropy', optimizer = "adam", metrics = ['accuracy'])
    modelCnn.fit(X_, y, batch_size=64, epochs=150, verbose=0)
    modelCnn.save("blackboxmodel/blackbox_1d_cnn.h5")
