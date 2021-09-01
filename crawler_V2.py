import time
from time import sleep
import os
import numpy as np
import pandas as pd
import glob

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from auxilary import check_exists_by_link_text, check_exists_by_xpath, download_wait, page_load_wait, erase_all_with_extension
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException

# set PATH
PATH = '/home/henry/enara-manager/subsidy/'

# set ext and erase all files in PATH with ext
ext = '.xls'
erase_all_with_extension(PATH, ext)

options = Options()
options.add_experimental_option("prefs",
                                {"download.default_directory":  r"/home/henry/enara-manager/subsidy",
                                 "download.prompt_for_download": False,
                                 "download.directory_upgrade": True,
                                 "safebrowsing.enabled": True}
                                 )
driver = webdriver.Chrome('./chromedriver', options=options)
driver.implicitly_wait(3)
driver.maximize_window()
driver.get('https://opn.gosims.go.kr/opn/ih/ih001/getIH001002QView.do')

sleep(2)

# set page_size
page_size = '50'
view = Select(driver.find_element_by_id('IH001002Q_changenPageSize'))
view.select_by_value(page_size)

# set start year to target_year
target_year = '2017'
start = Select(driver.find_element_by_id("IH001002QFrmSrch_fromFsyr"))
start.select_by_value(target_year)
sleep(1)

# make 중앙부처 dictionary to loop through. This should be scraped after setting years.
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="IH001002QFrmSrch_jrsdCode"]/option')))
dps = driver.find_elements_by_xpath('//*[@id="IH001002QFrmSrch_jrsdCode"]/option')
dct_dps = dict()
for dp in dps[19:]: # exclude '전체' option
    dct_dps[dp.get_attribute('value')] = dp.text

# make exmk dictionary
dct_exmk = {'민간이전': '9', '자치단체이전': '10'}

for dp in dct_dps:

    start = time.time()

    # set 중앙부처
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'IH001002QFrmSrch_jrsdCode')))
    select_dp = Select(driver.find_element_by_id('IH001002QFrmSrch_jrsdCode'))
    select_dp.select_by_value(dp)

    # set 지출목 to '자치단체이전'
    exmk = dct_exmk['자치단체이전']
    exmk_select = Select(driver.find_element_by_id('IH001002QFrmSrch_exmkId'))
    exmk_select.select_by_value(exmk)

    # click '검색'
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'btnRetrieveAsbzDdtlbzStdCsts')))
    search_btn = driver.find_element_by_id('btnRetrieveAsbzDdtlbzStdCsts')
    driver.execute_script("arguments[0].click();", search_btn)

    # wait until search list table is loaded
    sleep(3)

    # data structure to save data
    df_dprtmnt = pd.DataFrame()

    # if '조회된 결과가 없습니다' for '중앙부처' then continue
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="SBHE_DATAGRID_WHOLE_TBODY_IH001002QMainGridObj"]/tr')))
    n_rows = len(driver.find_elements_by_xpath('//*[@id="SBHE_DATAGRID_WHOLE_TBODY_IH001002QMainGridObj"]/tr'))
    if n_rows <= 1:
        print(f"[{dct_dps[dp]}, {target_year}, 자치단체이전]: 조회된 결과가 없습니다.")
        continue

    # below are 중앙부처 which granted subsidies in target_year
    # iterate through 'page next' button
    while True:

        # iterate through pages
        page_load_wait(driver, '//*[@id="sbGridPaging"]/ol/li', 0)
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(
            (By.XPATH, '//*[@id="sbGridPaging"]/ol/li')
        ))
        n_pgs = len(driver.find_elements_by_xpath('//*[@id="sbGridPaging"]/ol/li'))
        print(f"{n_pgs} 개의 페이지가 확인되었습니다.")
        cur_pg = 0

        while True:
            
            print(f"페이지 {cur_pg+1}의 데이터를 수집합니다.")
            
            # iterate through rows
            page_load_wait(driver, '//*[@id="SBHE_DATAGRID_WHOLE_TBODY_IH001002QMainGridObj"]/tr', 1)
            n_rows = len(driver.find_elements_by_xpath('//*[@id="SBHE_DATAGRID_WHOLE_TBODY_IH001002QMainGridObj"]/tr'))
            print(f"현재 페이지에서 {n_rows - 1}개의 내역사업이 확인되었습니다.")

            for i in range(1, n_rows):

                # click a next row
                row = driver.find_elements_by_xpath('//*[@id="SBHE_DATAGRID_WHOLE_TBODY_IH001002QMainGridObj"]/tr')[i]
                try:
                    row.click()
                except ElementClickInterceptedException as Exception:
                    print('ElementClickInterceptedException while trying to click a row, trying to find element again')
                    page_load_wait(driver, '//*[@id="SBHE_DATAGRID_WHOLE_TBODY_IH001002QMainGridObj"]/tr', 1)
                    row = driver.find_elements_by_xpath('//*[@id="SBHE_DATAGRID_WHOLE_TBODY_IH001002QMainGridObj"]/tr')[i]
                    row.click()

                # make sample data for each row and append it to the whole data

                # make row data
                df_row = pd.DataFrame(row.text.split('\n'))
                df_row = df_row.T
                df_row.columns = ['순번', '회계연도', '내역사업', '지출세목', '예산현액', '중앙부처']

                WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(
                    (By.XPATH, '//*[@id="SBHE_DATAGRID_WHOLE_TBODY_IH001002QSubGridObj"]')
                ))

                n_subrows = len(driver.find_elements_by_xpath('//*[@id="SBHE_DATAGRID_WHOLE_TBODY_IH001002QSubGridObj"]/tr')) - 2
                if n_subrows <= 0:
                    df_subrow = pd.DataFrame([np.nan] * 9).T
                    df_subrow.columns = ['NO', '보조사업', '보조사업차수', 
                    '보조사업자', '(사업비)국고보조금(단위:천원)', '(사업비)지자체부담금(단위:천원)', 
                    '(사업비)자기부담금(단위:천원)', '(사업비)기타부담금(단위:천원)','(사업비)합계(단위:천원)'
                    ]
                    df_sample = pd.concat([df_row, df_subrow], axis=1)
                    df_dprtmnt = pd.concat([df_dprtmnt, df_sample])
                    continue

                # download txt file and read as a DataFrame
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btnFiledownAsbzDdtlbzStdCsts2"]')))
                dwnld_btn = driver.find_element_by_xpath('//*[@id="btnFiledownAsbzDdtlbzStdCsts2"]')
                driver.execute_script("arguments[0].click();", dwnld_btn)
                download_wait(PATH)

                # if popups
                sleep(1)
                if check_exists_by_xpath(driver, '//*[@id="body"]/div[5]/section/footer/button[1]'):
                    driver.find_element_by_xpath('//*[@id="body"]/div[5]/section/footer/button[1]').click()
                sleep(1)

                # list_of_files = glob.glob('~/Downloads/*.txt')  # * means all if need specific format then *.csv
                # latest_file = max(list_of_files, key=os.path.getctime)
                fname = glob.glob(PATH+"*.xls")[0]
                
                try:
                    # df_subrow = pd.read_csv(latest_file)
                    df_subrow = pd.read_excel(fname, header=1)
                except FileNotFoundError:
                    fname = glob.glob("/home/henry/enara-manager/subsidy/*.xls")[0]
                    df_subrow = pd.read_excel(fname, header=1)
                    # df_subrow = pd.read_csv(latest_file)

                # replicate row data to match subrow data
                if len(df_subrow) > 1:
                    df_row = df_row.append([df_row]*(len(df_subrow) - 1), ignore_index=True)

                # concat row data and subrow data and append
                df_sample = pd.concat([df_row, df_subrow], axis=1)
                df_dprtmnt = pd.concat([df_dprtmnt, df_sample])

                os.remove(fname)
            
            cur_pg += 1

            if cur_pg >= n_pgs:
                print("다음 페이지가 존재하지 않습니다.")
                break

            WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(
                (By.XPATH, '//*[@id="sbGridPaging"]/ol/li')
            ))
            next_pg = driver.find_elements_by_xpath('//*[@id="sbGridPaging"]/ol/li')[cur_pg]
            next_pg_btn = next_pg.find_element_by_xpath('button')

            driver.execute_script("arguments[0].click();", next_pg_btn)

            print(f"{dct_dps[dp]}_{target_year}_자치단체이전.csv 파일을 임시로 저장합니다...")
            df_dprtmnt.to_csv(f"{dct_dps[dp]}_{target_year}_자치단체이전.csv")

        ftr = driver.find_element_by_id('sbGridPaging')
        if not check_exists_by_link_text(ftr, '다음 페이지로'):
            break

        pg_next = ftr.find_element_by_link_text("다음 페이지로")
        driver.execute_script("arguments[0].click();", pg_next)

        print(f"{dct_dps[dp]}_{target_year}_자치단체이전.csv 파일을 임시로 저장합니다...")
        df_dprtmnt.to_csv(f"{dct_dps[dp]}_{target_year}_자치단체이전.csv")
        print("다음 10개의 페이지로")

    end = time.time()
    print(f"Collecting subsidy data for {dct_dps[dp]} completed. It took {end-start} seconds.")
    print(f"{dct_dps[dp]}_{target_year}_자치단체이전.csv 파일을 저장합니다...")
    df_dprtmnt.to_csv(f"{dct_dps[dp]}_{target_year}_자치단체이전.csv")