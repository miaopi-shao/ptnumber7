# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 20:38:10 2025

@author: User
"""

import requests
from bs4 import BeautifulSoup

classes = ["play","eat","foreign","hot"]

url = "https://travel.yam.com/"

for c in classes:
    r = requests.get(url+"/info/"+c)
        
    if r.status_code == 200:
            # print(r.text)
            soup = BeautifulSoup(r.text,'html.parser')
            # print(soup.title.string)
            titles = soup.find_all('h2')
            times = soup.find_all('p',class_="artcle_author_info")
            for title,time in zip(titles,times):
                # print(type(title))
                soup2 = BeautifulSoup(str(title),'html.parser')
                # links = soup2.find_all("a")
                # for link in links:
                    # print(link.get("href"))
                # print(title.text,title.get("href"),time.text,"https://travel.yam.com"+soup2.find("a").get("href"))
                print(title.text,title.get("href"),time.text,"https://travel.yam.com"+title.a.get("href"))
                print()