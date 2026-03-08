import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import joblib

# load dataset
data = pd.read_csv("device_suggestion_dataset.csv")

# features
X = data[[
"avg_current",
"peak_current",
"duty_cycle",
"onoff_rate",
"usage_duration"
]]

# label
y = data["device_type"]

# model
model = DecisionTreeClassifier()

model.fit(X, y)

joblib.dump(model, "device_model.pkl")

print("✅ Device detection model trained successfully")