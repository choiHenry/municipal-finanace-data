from time import sleep
import os
import requests
import pandas as pd

def erase_all_with_extension(path, ext):
    files_in_directory = os.listdir(path)
    filtered_files = [file for file in files_in_directory if file.endswith(ext)]
    for file in filtered_files:
        path_to_file = os.path.join(path, file)
        os.remove(path_to_file)

def download(url, file_name):
    seconds = 0

    with open(file_name, "wb") as file:
        while True:
            try:
                response = requests.get(url)
                file.write(response.content)
                break
            except requests.exceptions.ConnectionError:
                seconds += 1
                print(f"Connection refused. Try download for each second. Passed {seconds} seconds.")
                sleep(1)
            finally:   
                if seconds > 20:
                    raise ConnectionError("Connection refused over 20 seconds. Shutting down the program...")

def read_xml(url, path, filename):
    seconds = 0
    
    while True:
        sleep(1)
        try:
            df = pd.read_xml(path+filename)
            return df
        except ValueError:
            print(f"Value error occurred. Sleep 30 seconds. Passed {seconds} seconds.")
            sleep(30)
            seconds += 30
        finally:
            download(url, filename)
            if seconds > 600:
                raise ValueError(f"Value")
