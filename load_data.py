from sklearn.model_selection import train_test_split
import pandas as pd

df = pd.read_csv("data/full_ie_set.csv", encoding="latin-1")



X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=0)