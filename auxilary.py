from selenium.common.exceptions import NoSuchElementException
from time import sleep
import os
import requests
import pandas as pd


def check_exists_by_link_text(webdriver, link_text):
    try:
        webdriver.find_element_by_link_text(link_text)
    except NoSuchElementException:
        return False
    return True


def check_exists_by_xpath(webdriver, xpath):
    try:
        webdriver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

def download_wait(path_to_downloads):
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < 20:
        sleep(1)
        for fname in os.listdir(path_to_downloads):
            if fname.endswith('.xls'):
                dl_wait = False
        seconds += 1
    if dl_wait:
        print("Download failed.")
        return
    print(f"Download was successful in {seconds} seconds.")

def page_load_wait(wd, xpath, threshold):
    seconds = 0
    pl_wait = True
    while pl_wait and seconds < 20:
        sleep(1)
        if len(wd.find_elements_by_xpath(xpath)) > threshold:
            pl_wait = False
        seconds += 1
    if pl_wait:
        print("Faild to load a page.")
        return
    print(f"Page loading was successful in {seconds} seconds: {xpath}")

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