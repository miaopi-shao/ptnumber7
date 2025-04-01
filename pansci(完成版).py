# -*- coding: utf-8 -*-
"""
Created on Fri Mar 28 20:28:42 2025

@author: User
"""

import requests
from bs4 import BeautifulSoup

classes = ["humanbeing","earth","space","文明足跡","environment","lifescience"]

url = "https://pansci.asia/"

for c in classes:
    r = requests.get(url+"/archives/category/type/"+c)
        
    if r.status_code == 200:
            # print(r.text)
            soup = BeautifulSoup(r.text,'html.parser')
            # print(soup.title.string)
            titles = soup.find_all('a', class_="post-title ga_track")
            times = soup.find_all('span', class_="post-text-light")
            for title,time in zip(titles,times):
                 print(title.text,time.text,title.get("href"))
                 print()