import pandas as pd
import joblib
import tkinter as tk
from tkinter import filedialog, messagebox
from ttkthemes import ThemedTk
from tkinter import ttk

# Load the trained model and scaler
model = joblib.load("random_forest_model.pkl")
scaler = joblib.load("scaler.pkl")

def show_prediction_window(predicted_label):
    result_window = ThemedTk(theme="radiance")
    result_window.title("Prediction Result")
    result_window.state("zoomed")  # Open in full-screen mode
    result_window.configure(bg="#1A1A2E")
    
    # Title label
    title_label = tk.Label(result_window, text="SKN INTERNS - 2025", font=("Arial", 80, "bold"), fg="#FFDD44", bg="#1A1A2E", relief="solid", borderwidth=5, padx=20, pady=10, highlightbackground="#FFC947", highlightthickness=3)
    title_label.pack(pady=50)
    
    result_frame = tk.Frame(result_window, bg="#16213E", padx=50, pady=50, relief="raised", bd=10, highlightbackground="#FFC947", highlightthickness=3)
    result_frame.place(relx=0.5, rely=0.6, anchor="center")
    
    label = tk.Label(result_frame, text="Predicted Breathing Pattern", font=("Arial", 22, "bold"), fg="#F8F8F8", bg="#16213E")
    label.pack(pady=20)
    
    result_label = tk.Label(result_frame, text=predicted_label, font=("Arial", 28, "bold"), fg="#FFDD44", bg="#16213E", padx=20, pady=10, relief="solid", borderwidth=5)
    result_label.pack(pady=30)
    
    close_button = tk.Button(result_frame, text="Close", command=result_window.destroy, font=("Arial", 18, "bold"), bg="#E94560", fg="white", padx=20, pady=10, relief="raised", borderwidth=5, activebackground="#C70039", highlightbackground="#FFC947", highlightthickness=2, cursor="hand2")
    close_button.pack(pady=20)
    
    result_window.mainloop()

def make_prediction():
    try:
        file_path = filedialog.askopenfilename(title="Select CSV file", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            new_data = pd.read_csv(file_path)
            X_new = new_data[["Time", "ADC Analog Value"]]
            X_new_scaled = scaler.transform(X_new)
            prediction = model.predict(X_new_scaled)
            label_mapping = {0: "Normal Breathing", 1: "Deep Breathing", 2: "Workout/Exercise Breathing"}
            predicted_label = label_mapping[prediction[0]]
            show_prediction_window(predicted_label)
        else:
            messagebox.showwarning("No file selected", "Please select a CSV file to proceed.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Main Window Setup
root = ThemedTk(theme="radiance")
root.title("Breathing Pattern Prediction")
root.state("zoomed")  # Open in full-screen mode
root.configure(bg="#1A1A2E")  # Dark blue-gray background for a modern look

# Title label
title_label = tk.Label(root, text="SKN INTERNS - 2025", font=("Arial", 80, "bold"), fg="#FFDD44", bg="#1A1A2E", relief="solid", borderwidth=5, padx=20, pady=10, highlightbackground="#FFC947", highlightthickness=3)
title_label.pack(pady=50)

# UI Elements placed at the center with a modern design
frame = tk.Frame(root, bg="#16213E", padx=45, pady=45, relief="raised", bd=10, highlightbackground="#FFC947", highlightthickness=3)
frame.place(relx=0.5, rely=0.6, anchor="center")  # Shifted slightly down

label = tk.Label(frame, text="Breathing Pattern Prediction", font=("Arial", 26, "bold"), fg="#F8F8F8", bg="#16213E")
label.pack(pady=20)

predict_button = tk.Button(frame, text="Select CSV File and Predict", command=make_prediction, font=("Arial", 22, "bold"), bg="#E94560", fg="white", padx=25, pady=14, relief="raised", borderwidth=5, activebackground="#C70039", highlightbackground="#FFC947", highlightthickness=2, cursor="hand2")
predict_button.pack(pady=35)

# Run the GUI Event Loop
root.mainloop()
