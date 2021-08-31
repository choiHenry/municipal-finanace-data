# Municipal Finance Data
This repository contains web scraper for municipal finance data.

# How to use

## Prerequisites
1. Visual Studio Code: [download Visual Studio Code](https://code.visualstudio.com/download) and install it.
2. Anaconda: [download anaconda](https://www.anaconda.com/products/individual-d) and install it.
3. Download this repo

## Init conda env and install requirements
1. Go to terminal(or cmd) and type
```terminal
$ conda create -n municipal-finance-data
$ conda activate municipal-finance-data
$ pip install -r requirements.txt
```

## Set Parameters and Start Program
1. Open api_V2.py using VS Code and set PATH and Key variable 
2. On your terminal, type target year and month and day where you want to start to scrape to scrape data.
```terminal
$ python api_V2.py [year] [month] [day]
```
e.g. Below code start scraping data in 2016 from March 1st.
```terminal
$ python api_V2.py 2016 3 1
```
