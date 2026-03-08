import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import joblib

data = pd.read_csv("final_device_care_dataset.csv")

X = data[[
"baseline_current",
"current_rms",
"delta_current_ratio",
"current_std",
"spike_count",
"onoff_transitions",
"duty_cycle",
"temp_max"
]]

y = data["label"]

model = DecisionTreeClassifier()

model.fit(X, y)

joblib.dump(model, "fault_model.pkl")

print("✅ Fault prediction model trained successfully")