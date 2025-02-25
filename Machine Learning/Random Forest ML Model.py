import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from imblearn.over_sampling import SMOTE

# Load the CSV file
file_path = "D:\BE_Project\ML MD\concatenated_file_md - Copy.csv"  # Update with the correct file path
df = pd.read_csv(file_path)

# Drop rows with NaN labels and encode categorical labels
df_labeled = df.dropna(subset=["Label"]).copy()
df_labeled["Label"] = df_labeled["Label"].astype("category").cat.codes  # Convert labels to numeric

# Features and target variable
X = df_labeled[["Time", "ADC Analog Value"]]
y = df_labeled["Label"]

# Splitting into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Handle class imbalance using SMOTE
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

# Standardize features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_resampled)
X_test_scaled = scaler.transform(X_test)

# Train a Random Forest classifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train_scaled, y_train_resampled)

# Make predictions
y_pred = clf.predict(X_test_scaled)

# Model evaluation
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

print(f"Accuracy: {accuracy:.4f}")
print("Classification Report:\n", report)

# Save the trained model and scaler
joblib.dump(clf, "random_forest_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("Model and scaler saved successfully!")
