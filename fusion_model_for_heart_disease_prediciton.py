Bibtex of this file:
    
    @inproceedings{kibria2020efficient,
  title={An Efficient Machine Learning-Based Decision-Level Fusion Model to Predict Cardiovascular Disease},
  author={Kibria, Hafsa Binte and Matin, Abdul},
  booktitle={International Conference on Intelligent Computing \& Optimization},
  pages={1097--1110},
  year={2020},
  organization={Springer}
}
    
CODE:    
###############################################################################################################
# -*- coding: utf-8 -*-
"""Fusion_model_for_heart_disease_prediciton.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19FpdF9o5VjNGfF5vZBJPsB_-sjhZ9g4H
"""

from keras.models import Sequential
from keras.layers import Dense ,BatchNormalization
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler,StandardScaler
from tensorflow.keras.optimizers import Adam, SGD
from matplotlib import pyplot as plt
import numpy
import numpy as np

from google.colab import drive
drive.mount('/content/drive')

dataset = numpy.loadtxt("/content/drive/MyDrive/Colab Notebooks/feature_extraction_chi - Copy.csv", delimiter=",")
train_sample = dataset[:,0:13]
train_label = dataset[:,13]
X_train, X_test, y_train, y_test = train_test_split(train_sample, train_label , test_size=0.25,shuffle=True)

"""#ANN"""

scaler = MinMaxScaler(feature_range=(0,1))
scaled_X_train_ann=scaler.fit_transform(X_train)
scaled_X_test_ann=scaler.fit_transform(X_test)

"""**For KNN we have taken top 10 significant features using chi-square test**"""

scaler1 = StandardScaler()
scaler1.fit(X_train)
scaled_X_train_knn = scaler1.transform(X_train)
scaled_X_train_knn = scaled_X_train_knn[:,0:10]
scaler.fit(X_test)
scaled_X_test_knn = scaler1.transform(X_test)
scaled_X_test_knn = scaled_X_test_knn[:,0:10]

model = Sequential()
model.add(Dense(10, input_dim=13,use_bias=True,bias_initializer='zeros', activation='sigmoid'))
model.add(Dense(1, activation='sigmoid'))
sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='binary_crossentropy', optimizer='adam',metrics=['accuracy'])

history=model.fit(scaled_X_train_ann, y_train,validation_split=0.1, batch_size=5,epochs=20,shuffle=True,verbose=2)

predictions = model.predict(scaled_X_test_ann,batch_size=5,verbose=0)
predictions_annn=predictions
rounded_predictions = model.predict(scaled_X_test_ann,batch_size=5,verbose=0)
rounded_predictions=np.where(rounded_predictions>0.5,1,0)
#rounded_predictions = model.predict_classes(scaled_X_test_ann,batch_size=5,verbose=0)(not working in new tensorflow)

import sklearn.metrics as metrics
score=metrics.accuracy_score( y_test,rounded_predictions)
score

#import classification_report//FOR ANN
print(metrics.confusion_matrix(y_test,rounded_predictions))
print(metrics.classification_report(y_test,rounded_predictions))

fpr2, tpr2, threshold = metrics.roc_curve(y_test,rounded_predictions)
roc_auc2 = metrics.auc(fpr2, tpr2)
print("roc_auc_ann",roc_auc2)

# list all data in history
print(history.history.keys())
# summarize history for accuracy
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

"""#KNN"""

from sklearn.neighbors import KNeighborsClassifier

#Setup arrays to store training and test accuracies
neighbors = np.arange(1,30)
train_accuracy =np.empty(len(neighbors))
test_accuracy = np.empty(len(neighbors))

for i,k in enumerate(neighbors):
    #Setup a knn classifier with k neighbors
    knn = KNeighborsClassifier(n_neighbors=k)
    
    #Fit the model
    knn.fit(scaled_X_train_knn, y_train)
    
    #Compute accuracy on the training set
    train_accuracy[i] = knn.score(scaled_X_train_knn, y_train)
    
    #Compute accuracy on the test set
    test_accuracy[i] = knn.score(scaled_X_test_knn, y_test)     
#Generate plot
plt.title('k-NN Varying number of neighbors')
plt.plot(neighbors, test_accuracy, label='Testing Accuracy')
plt.plot(neighbors, train_accuracy, label='Training accuracy')
plt.legend()
plt.xlabel('Number of neighbors')
plt.ylabel('Accuracy')
plt.show()

knn = KNeighborsClassifier(n_neighbors=12)
knn.fit(scaled_X_train_knn,y_train)
#import confusion_matrix
from sklearn.metrics import confusion_matrix
#let us get the predictions using the classifier we had fit above
y_pred = knn.predict(scaled_X_test_knn)
confusion_matrix(y_test,y_pred)
y_pred_proba_knn = knn.predict_proba(scaled_X_test_knn)[:,1]

#print(predictions)
import sklearn.metrics as metrics
scores1=metrics.accuracy_score(y_test,y_pred)
print("KNN",scores1)  

print(metrics.confusion_matrix(y_test,y_pred))
print(metrics.classification_report(y_test,y_pred))
        
fpr1, tpr1, threshold = metrics.roc_curve(y_test, y_pred)
roc_auc1 = metrics.auc(fpr1, tpr1)
print("roc_auc_dec",roc_auc1)

"""#Fusion of two models"""

ann=predictions_annn.flatten()
mixed=ann+y_pred_proba_knn
mixed=mixed/2
mixed
rounded_mixed=mixed
rounded_mixed
for i in range(len(y_test)):
    if mixed[i]>=.5:
        rounded_mixed[i]=1
    else:
         rounded_mixed[i]=0
            
score=metrics.accuracy_score(rounded_mixed,y_test)
print(score)

print(metrics.confusion_matrix(y_test,rounded_mixed))
print(metrics.classification_report(y_test,rounded_mixed))

fpr3, tpr3, threshold = metrics.roc_curve(rounded_mixed,y_test)
roc_auc3 = metrics.auc(fpr3, tpr3)
print("roc_auc_tot",roc_auc3)

"""#ROC curve of three models"""

import matplotlib.pyplot as plt
plt.title('Receiver Operating Characteristic')
plt.plot(fpr2, tpr2, 'b', label = 'ANN = %0.2f' % roc_auc2)
plt.plot(fpr1, tpr1, 'r', label = 'KNN = %0.2f' % roc_auc1)
plt.plot(fpr3, tpr3, 'g', label = 'Combined = %0.2f' % roc_auc3)
plt.legend(loc = 'lower right')
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0, 1])
plt.ylim([0, 1])
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.show()
