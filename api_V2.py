from auxilary import download, erase_all_with_extension, read_xml
import pandas as pd
from calendar import monthrange
import os
import requests
from time import time
from datetime import date
import sys

def download_expenditure_data(api_key, path, year, m=1, d=1):
    ext = '.xml'
    erase_all_with_extension(path, ext)
    
    base_url = 'https://lofin.mois.go.kr/HUB/QWGJK/'
    Key = api_key
    Type = 'XML'
    pSize = '1000'
    accnut_year = str(year)

    for month in range(1, 13):

        if month < m:
            continue

        for day in range(1, monthrange(year, month)[1] + 1):
            if month <= m and day < d:
                continue

            start = time()
            excut_de = date(year, month, day).strftime('%Y%m%d')
            print(f"Start collecting data for {excut_de}.")
            pIndex = '1'
            url = base_url + "?key=" + Key + "&Type=" + Type + "&pIndex=" + pIndex + "&pSize=" + pSize + "&accnut_year=" + accnut_year + "&excut_de=" + excut_de
            print(url)
            filename = f'{excut_de}_{pIndex}.xml'
            download(url, filename)
            df = pd.read_xml(path+filename)
            n_points = int(df.iloc[0, 0])
            n_pages = n_points // 1000 + 1

            lst_dfs = [df]

            print(f'{n_points} found for {excut_de}. Downloading {n_pages} files...')

            for pIndex in range(1, n_pages+1):

                url = base_url + "?key=" + Key + "&Type=" + Type + "&pIndex=" + str(pIndex) + "&pSize=" + pSize + "&accnut_year=" + accnut_year + "&excut_de=" + excut_de 
                filename = f'{excut_de}_{pIndex}.xml'
                download(url, filename)
                print(f"Download Complete: {pIndex} / {n_pages} [{excut_de}]")
                df = read_xml(url, path, filename)
                lst_dfs.append(df)

            df = pd.concat(lst_dfs)
            df.to_csv(f'{excut_de}_concatenated.csv')

            erase_all_with_extension(path, ext)

            end = time()
            print(f"Collecting data for {excut_de} took {end-start} seconds.")

print(__name__)

if __name__ == '__main__':
    
    PATH = '/home/henry/enara-manager/subsidy/'
    ext = '.xml'
    erase_all_with_extension(PATH, ext)
    Key = 'SVKYD1000214620210829043226DOVGD'
    download_expenditure_data(Key, PATH, int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))