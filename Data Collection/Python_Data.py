import serial
import csv
import time
import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd
from peakutils import indexes

serial_port = 'COM9'  # Change this to your actual port
baud_rate = 115200
timeout = 1  # Increased timeout for serial read

# Function to get valid breathing pattern input
def get_breathing_pattern():
    while True:
        pattern_input = input("Enter the breathing pattern (n for normal, d for deep, w for workout): ").strip().lower()
        if pattern_input in ['n', 'd', 'w']:
            return {'n': 'normal', 'd': 'deep', 'w': 'workout'}[pattern_input]
        else:
            print("Invalid input. Please enter 'n' for normal, 'd' for deep, or 'w' for workout.")

breathing_pattern = get_breathing_pattern()

output_directory = os.path.expanduser('~\\Desktop\\arduino_data')
os.makedirs(output_directory, exist_ok=True)

# Generate a unique filename based on timestamp and breathing pattern
timestamp = time.strftime('%Y%m%d_%H%M%S')
csv_file_path = os.path.join(output_directory, f'{breathing_pattern}_arduino_output_{timestamp}.csv')

# Ensure the port is closed before opening
try:
    ser = serial.Serial(serial_port, baud_rate, timeout=timeout)
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    exit()

x_vals = []
analogValue_data = []

def read_and_process_data(csv_writer):
    line = ser.readline().decode('utf-8').strip()
    if line.startswith('ADC analog value'):
        analog_value = int(line.split('=')[1].strip())
        elapsed_time = time.time() - start_time
        x_vals.append(elapsed_time)
        analogValue_data.append(analog_value)
        csv_writer.writerow([elapsed_time, analog_value])
        print(f'Time: {elapsed_time}, ADC Analog Value: {analog_value}')

def update_plot(frame, csv_writer):
    read_and_process_data(csv_writer)
    plt.cla()
    plt.plot(x_vals, analogValue_data, label='ADC Analog Value')
    plt.xlabel('Time')
    plt.ylabel('ADC Analog Value')
    plt.legend()
    
    # Stop the animation after 60 seconds
    if time.time() - start_time >= 60:
       plt.close()

def on_close(event):
    ser.close()
    print(f"CSV file saved at {csv_file_path}.")

with open(csv_file_path, mode='w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Time', 'ADC Analog Value'])

    print(f"Data capture will start after a 5-second delay...")
    time.sleep(5)  # Add a delay of 5 seconds

    print(f"Data capture started. Saving to {csv_file_path}...")

    start_time = time.time()
    fig, ax = plt.subplots()
    fig.canvas.mpl_connect('close_event', on_close)
    ani = FuncAnimation(fig, update_plot, fargs=(csv_writer,), interval=100, cache_frame_data=False)
    plt.show()

# Ensure the port is closed after the script ends
ser.close()

# Post-processing the data
df = pd.read_csv(csv_file_path)

plt.plot(df['Time'], df['ADC Analog Value'], 'k-')

# Remove noise using a rolling average
df['ADC Analog Value'] = df['ADC Analog Value'].rolling(window=4).mean()

# Fill NaN values using backward fill
df['ADC Analog Value']=df['ADC Analog Value'].bfill()

output_directory1 = os.path.expanduser('~\\Desktop\\filtered_data')
os.makedirs(output_directory1, exist_ok=True)

filtered_csv_file_path = os.path.join(output_directory1, f'{breathing_pattern}_Filtered_output_{timestamp}.csv')

with open(filtered_csv_file_path, mode='w', newline='') as csv_file:
    filtered_csv_writer = csv.writer(csv_file)
    filtered_csv_writer.writerow(['Time', 'ADC Analog Value'])
    # Write filtered data to CSV
    for index, row in df.iterrows():
        filtered_csv_writer.writerow([row['Time'], row['ADC Analog Value']])

print(f"Filtered data saved at {filtered_csv_file_path}.")

# Replot the data
plt.plot(df['Time'], df['ADC Analog Value'], 'b-')

# Find peaks using peakutils
peaks_indexes = indexes(df['ADC Analog Value'], thres=0.3, min_dist=25)
peaks = df['ADC Analog Value'].iloc[peaks_indexes]

# Plot the data again and mark the peaks
plt.plot(df['Time'], df['ADC Analog Value'], 'b-')
plt.plot(df['Time'].iloc[peaks_indexes], peaks, 'ro')

plt.xlabel('Time')
plt.ylabel('ADC Analog Value')
plt.title(f'Breath per Minute \n Number of Peaks: {len(peaks)}')

plt.show()
