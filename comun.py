import csv
import os
import time
from datetime import datetime
import uuid
import paho.mqtt.client as mqtt
import pandas as pd
import subprocess

from features_extraction import *


def turn_off_wifi():
    """
    Turns off the Wi-Fi module on the Raspberry Pi
    """
    subprocess.run(["sudo", "ifconfig", "wlan0", "down"])


def turn_on_wifi():
    """
    Turns on the Wi-Fi module on the Raspberry Pi
    """
    subprocess.run(["sudo", "ifconfig", "wlan0", "up"])



def get_mac_address():
    """
    Returns the MAC address of the device as a string in lowercase and without colons
    """
    mac = hex(uuid.getnode())[2:].zfill(12)
    return mac.lower()


# Get the current UTC date and time in timestamp format
def current_timestamp() -> str:
    """
    Get the current UTC date and time in timestamp format

    Returns:
        str: Timestamp in the format 'YYYY-MM-DD HH:MM:SS'
    """
    timestamp = datetime.utcnow()
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')


# Get the current UTC date and time in UnixTime format
def current_unix_time() -> int:
    """
    Get the current UTC date and time in UnixTime format

    Returns:
        int: UnixTime
    """
    unix_time = int(time())
    return unix_time


# Extract audio features from the given audio file
def extract_audio_features(filename: str) -> list:
    """
    Extract audio features from the given audio file

    Args:
        filename (str): Name of the audio file to extract features from

    Returns:
        list: List of audio features extracted from the audio file
    """
    # Code to extract audio features goes here
    pass


# Extract data from audio files in a given directory and save it to a CSV file
def dir_data_extraction(data_directory: str, csv_path: str) -> None:
    """
    Extract data from audio files in a given directory and save it to a CSV file

    Args:
        data_directory (str): Path of the directory containing audio files to extract data from
        csv_path (str): Path of the CSV file to save the extracted data to

    Returns:
        None
    """
    for filename in os.listdir(data_directory):
        f = os.path.join(data_directory, filename)
        if os.path.isfile(f):
            data = extract_audio_features(f)
            print(filename + " || Feature extraction: " + str(data))
            save_into_csv(data, csv_path)
            os.remove(f)
            print("File removed successfully")


# Check the size of files in a given directory and extract data if the size limit is exceeded
def check_file_size(data_directory: str, csv_path: str) -> None:
    """
    Check the size of files in a given directory and extract data if the size limit is exceeded

    Args:
        data_directory (str): Path of the directory to check the size of files in
        csv_path (str): Path of the CSV file to save the extracted data to

    Returns:
        None
    """
    size = 0
    for ele in os.scandir(data_directory):
        size += os.path.getsize(ele)
    print("Current folder size: {}".format(size))
    if size > 1e+8:
        print("Size limit detected. Extracting data features...")
        dir_data_extraction(data_directory, csv_path)


# Read data from a CSV file and convert it to a string
def read_from_csv(path_csv: str) -> str:
    """
    Read data from a CSV file and convert it to a string

    Args:
        path_csv (str): Path of the CSV file to read data from

    Returns:
        str: Data from the CSV file converted to a string
    """
    df = pd.read_csv(path_csv, index_col=0)
    step = 35
    output = []
    for i in range(0, len(df), step):
        data = df[i:i + step].to_string()
        data_correction = "[" + data[36:] + "]"
        final_data = data


# Adds the payload to the csv file (No connection case)
def save_into_csv(payload, path):
    """Adds the payload to the specified csv file.

    Args:
        payload: A string that contains the data to be saved into the csv file.
        path: A string that contains the file path where the data is to be saved.

    Returns:
        None
    """
    with open(path, 'a', newline='') as outfile:
        writer = csv.writer(outfile)  # Return a writer object
        writer.writerow([payload])  # Write the data


# Clear csv file
def clear_csv(path_csv):
    """Clears the specified csv file.

    Args:
        path_csv: A string that contains the file path to be cleared.

    Returns:
        None
    """
    # opening the file with w+ mode truncates the file
    f = open(path_csv, "w+")
    f.close()


# Check return code. Already defined in the paho mqtt packet
def on_connect(client, userdata, flags, return_code):
    """Function that runs when the MQTT client connects or disconnects from the broker.

    Args:
        client: The client instance that initiated this callback.
        userdata: User data of any type that is passed as parameter to the callback.
        flags: Response flags sent by the broker.
        return_code: The connection result.

    Returns:
        The connection result.
    """
    if return_code == 0:
        client.connected_flag = True  # set flag
        print("Connected successfully, sending data to server")
    else:
        client.connected_flag = False
        print("Connection error. Returned code = ", return_code)

    return return_code


# Publish message
def mqtt_request(host: str, port: int, topic: str = None, payload: str = None):
    """Publishes data to the specified MQTT broker.

    Args:
        host: A string that contains the IP address of the MQTT broker.
        port: An integer that contains the port number of the MQTT broker.
        topic: A string that contains the topic where the data is to be published.
        payload: A string that contains the data to be published.

    Returns:
        A boolean that represents the status of the connection.
    """
    try:
        client = mqtt.Client()  # Create new instance
        client.connected_flag = False
        if port == 8883:
            client.tls_set("") # Path to certificate
        client.on_connect = on_connect  # Bind callback function
        client.loop_start()
        try:
            client.connect(host, port, 60)  # Connect to broker
        except Exception as msg:
            print("No es posible conectar con el servidor: {}".format(msg))
        time.sleep(2)  # Necesario para establecer conexión, otorgar un cierto tiempo al servidor para que responda.
        while not client.connected_flag:  # Wait in loop
            print("Client flag is false")
            for i in range(10):
                if i < 10:
                    i += 1
                else:
                    break
        client.publish(topic, payload)  # Publicamos datos al broker
        client.disconnect()  # disconnect
        client.loop_stop()
        return client.connected_flag
    except Exception as e:
        print("Error: {} ".format(e))
