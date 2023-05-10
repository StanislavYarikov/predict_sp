#write a python code for finding best parameters of sklearn GBR model via crossvalidation on "train_X" pandas datafrane with "train_y" pandas series target values  with 10 folds, saving the best model and function to predict target pandas series from "pred_X" pandas dataframe

import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
import pickle

from insert_facts import get_train_test

# Load the data
def train_ml_model():
    train_X, train_y, pred_X, pred_y = get_train_test()
    # Define the model and parameter grid for cross-validation
    gbr = GradientBoostingRegressor()
    #gbr = RandomForestRegressor()
    param_grid = {
        'n_estimators': [5, 10, 50],
        'max_depth': [3, 4, 5, 6, 7, 10],
        'learning_rate': [10, 5, 2, 1, 0.5, 0.25, 0.1, 0.05],
        'subsample': [0.25, 0.5, 0.75, 1],
        #'min_samples_leaf': [1, 2, 3, 5],
        #'min_samples_split': [2, 3, 4],
        #'loss': ['squared_error', 'absolute_error', 'huber', 'quantile'],
    }

    # Perform cross-validation to find the best parameters
    gbr_cv = GridSearchCV(gbr, param_grid, cv=10)
    gbr_cv.fit(train_X, train_y)

    # Print the best parameters and score
    print("Best parameters:", gbr_cv.best_params_)
    print("Best score:", gbr_cv.best_score_)

    # Save the best model to a file
    best_gbr = gbr_cv.best_estimator_
    with open('best_gbr_model.pkl', 'wb') as f:
        pickle.dump(best_gbr, f)

# Use the best model to make predictions on a new dataset
def get_predict(pred_X):
    with open('best_gbr_model.pkl', 'rb') as f:
        saved_gbr = pickle.load(f)
        return pd.Series(saved_gbr.predict(pred_X),index=pred_X.index).to_dict()
    #pred_y = best_gbr.predict(pred_X)