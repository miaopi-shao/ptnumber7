# -*- coding: utf-8 -*-
"""
Created on Fri Mar 28 19:29:34 2025

@author: User
"""

import requests
from bs4 import BeautifulSoup

classes = ["fashion","beauty","entertainment","lifestyle","luxury","video"]

url = "https://www.vogue.com.tw/"

for c in classes:
    r = requests.get(url+c)
        
    if r.status_code == 200:
            # print(r.text)
            soup = BeautifulSoup(r.text,'html.parser')
            # print(soup.title.string)
            titles = soup.find_all('h2', class_="SummaryItemHedBase-hiFYpQ eLtvVr summary-item__hed")
            times = soup.find_all('time', class_="BaseWrap-sc-gjQpdd BaseText-ewhhUZ SummaryItemBylinePublishDate-ctLSIQ iUEiRd ipBjLL kiqveE summary-item__publish-date")
            links = soup.find_all("a", attrs={"class":"SummaryItemHedLink-civMjp jRfyII summary-item-tracking__hed-link summary-item__hed-link"})
            for title,time,link in zip(titles,times,links):
                print(title.text,time.text,"https://www.vogue.com.tw"+link.get("href"))
                print()
