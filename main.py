from comun import *
from features_extraction import *
import datetime

# These variables are used to store the directory paths, MQTT broker host and port, topic, and time check interval.
RECORDS_DIRECTORY = ''
CSV_DIRECTORY = ''
HOST = ""
PORT = 1883  # or 8883
TOPIC = "topic12345"
TIME_CHECK = 60  # Checking directory size every 60s

# These variables are used to keep track of the last time the instant data was sent and the last update time stamp.
previous_millis_update = 0  # Last update time stamp
previous_millis_send = 0  # Timestamp of the last sending of instant data


# This function is the main loop that runs continuously.
def main():
    global previous_millis_send

    while True:
        # This block checks if the specified time interval has elapsed since the last instant data was sent.
        if time.time() - previous_millis_send >= TIME_CHECK:
            print("Checking directory size at {}".format(datetime.datetime.now()))
            previous_millis_send = time.time()
            # This block checks the file size of the specified directory and reads data from a CSV file in that directory.
            check_file_size(RECORDS_DIRECTORY, CSV_DIRECTORY)
            if os.path.getsize('') > 0:
                data = read_from_csv(CSV_DIRECTORY)
                # This block sends the data to an MQTT broker and clears the CSV file if the data was sent successfully.
                is_sent = mqtt_request(HOST, PORT, TOPIC, str(data))
                print("Topic is: " + TOPIC)
                if is_sent:
                    clear_csv(CSV_DIRECTORY)


# This block runs the main function if the script is being run directly.
if __name__ == '__main__':
    main()
