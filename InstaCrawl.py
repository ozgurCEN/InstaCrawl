#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 22 09:51:58 2019

@author: ozgur
"""

#pip install bs4
#pip install selenium
#pip install requests
#pip install json
#chrome driver download: https://chromedriver.storage.googleapis.com/index.html?path=2.45/
#set executable path for chrome driver in mainPage() and singlePost() initializations

from bs4 import BeautifulSoup 
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import requests
import json
import os 
import time
from pandas import DataFrame
import re
from datetime import datetime


class mainPage():
    
    def __init__(self, url, chrome_path='/home/ozgur/Desktop/chromedriver'):
        r = requests.get(url)
        soup = BeautifulSoup(r.content)
        scripts = soup.find('script', attrs={'type':"text/javascript"}, text=re.compile('window._sharedData'))
        stringified_json = scripts.get_text().replace('window._sharedData = ', '')[:-1]
        try:
            string=json.loads(stringified_json)['entry_data']['ProfilePage'][0]['graphql']['user']
            self.dict_ = string
            self.url_ = url
            self.chrome_path = chrome_path
        except:
            raise Exception("This is not a main page of a user")
    """
    def get_raw_dict(self):
        dict_=self.dict_
        return dict_
    """
    
    #Returns basic demographic information about the account
    def basic_information(self):
        dict_=self.dict_
        info_dict={}
        info_dict.update({'full_name':dict_['full_name']})
        info_dict.update({'is_private':dict_['is_private']})
        info_dict.update({'following':dict_['edge_follow']['count']})
        info_dict.update({'followed_by':dict_['edge_followed_by']['count']})
        info_dict.update({'num_of_post':dict_['edge_owner_to_timeline_media']['count']})
        return info_dict
    
    #Creates dict for first 12 post and their publish times
    def initial_post_list(self):
        dict_=self.dict_['edge_owner_to_timeline_media']['edges']
        post_list={}
        for i in dict_:
            post_list.update({i['node']['shortcode']:datetime.utcfromtimestamp(i['node']['taken_at_timestamp']).strftime('%Y-%m-%dT%H:%M:%SZ')})
        return post_list
    
    #Directly loads given post page and its methods
    #Instagram initially shows 24 post. So if older post is wanted, web rendering operation with 
    #Selenium will be initiated.
    def jump_to_post(self, post_num=1):
        if post_num <= 24:
            post_list=list(self.initial_post_list().keys())
            url='https://www.instagram.com/p/'+post_list[post_num-1]+'/'
            return singlePost(url,chrome_path=self.chrome_path)
        elif 24 <= post_num <= self.dict_['edge_owner_to_timeline_media']['count']:
            options = Options()
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument('--headless')
            browser = Chrome(executable_path=self.chrome_path, options = options)
            browser.get(self.url_)
            
            scroll_amount = round(post_num/12)-1
            for i in range(scroll_amount):
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)
            time.sleep(1)
            soup = BeautifulSoup(browser.page_source)
            current_post_list = soup.find_all('div', attrs={'class':'v1Nh3 kIKUG _bz0w'})
            post_url_part = current_post_list[current_post_list.__len__()-post_num%12-1].find('a')['href']
            url='https://www.instagram.com'+post_url_part
            return singlePost(url)
        else:
            raise Exception('There are only '+str(self.dict_['edge_owner_to_timeline_media']['count'])+' posts.')
            

class singlePost():

    def __init__(self, url, chrome_path="/home/ozgur/Desktop/chromedriver"): 
        options = Options()
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--headless')
        browser = Chrome(executable_path=chrome_path, options = options)
        browser.get(url)
        soup = BeautifulSoup(browser.page_source)
        try:
            scripts = soup.find('script', attrs={'type':"text/javascript"}, text=re.compile('window._sharedData'))
            stringified_json = scripts.get_text().replace('window._sharedData = ', '')[:-1]
            json.loads(stringified_json)['entry_data']['PostPage']
        except:
            raise Exception('This is not a post page of a user')
        tag = soup.find('a', class_='FPmhX notranslate nJAzx')['title']
        self.url = url
        self.browser = browser
        self.tag = tag

    #(Internal Usage) Checks whether the post is video or not. 
    def check_video(self):
        soup = BeautifulSoup(self.browser.page_source)
        if soup.find('span', class_='vcOH2') != None:
            return True
        else:
            return False

    #Returns "like" count if post is a picture, "like" & "view" counts if post is a video
    def likes_and_views(self):
        if self.check_video():
            self.browser.find_element_by_class_name('vcOH2').click()
            soup = BeautifulSoup(self.browser.page_source)
            for view in soup.find_all('span', class_='vcOH2'):
                view_text = view.text
            for like in soup.find_all('div', class_='vJRqr'):
                like_text = like.text
            self.browser.find_element_by_class_name('Kj7h1').click()
            return [view_text, like_text]
        else:
            soup = BeautifulSoup(self.browser.page_source)
            for like in soup.find_all('a', class_='zV_Nj'):
                return like.text
    
    #Returns publish time of the post
    def publish_time(self):
        soup = BeautifulSoup(self.browser.page_source)
        time=soup.find('time', class_='_1o9PC Nzb55')
        date=time.get('datetime').replace('T', ' ')[:19]
        return date
    
    #Returns the info that user entered with the post
    def post_descr(self):
        soup = BeautifulSoup(self.browser.page_source)
        descr = soup.find('div', class_='C4VMK')
        descr = descr.find('span')
        return descr.text
    
    #Downloads the post to the current working directory
    def download_post(self):
        soup = BeautifulSoup(self.browser.page_source)
        if self.check_video() == 1:
            content = soup.find('video', class_='tWeCl')
            url=content['src']
            r = requests.get(url)
            open(str(self.tag)+'.mp4','wb').write(r.content)
            print('item downloaded at '+str(os.getcwd()+'/'+str(self.tag)))
        else:
            content = soup.find('img', class_='FFVAD')
            url=content['src']
            r = requests.get(url)
            open(str(self.tag)+'.jpeg', 'wb').write(r.content)
            print('item downloaded at '+str(os.getcwd()+'/'+str(self.tag)))
    
    #(Internal Usage) Loads json of the page
    def root_info(self):
        soup = BeautifulSoup(self.browser.page_source)
        scripts = soup.find('script', attrs={'type':"text/javascript"}, text=re.compile('window._sharedData'))
        stringified_json = scripts.get_text().replace('window._sharedData = ', '')[:-1]
        string=json.loads(stringified_json)['entry_data']['PostPage'][0]['graphql']['shortcode_media']
        return string
        
    #Returns number of comments done to the post
    def number_of_comments(self):
        dict_=self.root_info()
        dict_['edge_media_to_comment']['count']
        return dict_['edge_media_to_comment']['count']
    
    #Instagram initially shows last 24 messages on a post page. 
    #This method gets last n comments and dumps them into a data frame 
    #with each comment's userid information.
    def last_n_comments_to_DF(self, n_comments=24):
        df=DataFrame(columns=['user', 'comment'])
        if n_comments <= 24:
            soup = BeautifulSoup(self.browser.page_source)
            comments = soup.find_all('li', attrs={'class':'gElp9'})
            if len(comments)-1<=n_comments:
                for comment in comments[1:]:
                    user = comment.find_all('a')
                    user_text = user[0].text
                    script = comment.find_all('span')
                    script_text = script[0].text
                    df.at[len(df)+1,'user']=str(user_text)
                    df.at[len(df),'comment']=str(script_text)
            else:
                for comment in comments[-n_comments:]:
                    user = comment.find_all('a')
                    user_text = user[0].text
                    script = comment.find_all('span')
                    script_text = script[0].text
                    df.at[len(df)+1,'user']=str(user_text)
                    df.at[len(df),'comment']=str(script_text)
        else:
            try:
                num_page_load=round(n_comments/24)
                for i in range(num_page_load):
                    self.browser.find_element_by_css_selector("button[class='Z4IfV _0mzm- sqdOP yWX7d        ']").click()
                    time.sleep(1)
                time.sleep(1)
                soup = BeautifulSoup(self.browser.page_source)
                comments = soup.find_all('li', attrs={'class':'gElp9'})
                for comment in comments[-n_comments:]:
                    user = comment.find_all('a')
                    user_text = user[0].text
                    script = comment.find_all('span')
                    script_text = script[0].text
                    df.at[len(df)+1,'user']=str(user_text)
                    df.at[len(df),'comment']=str(script_text)
            except:
                raise Exception('There is not more than 24 comments.')
        df.reset_index(inplace=True, drop=True)
        return df           