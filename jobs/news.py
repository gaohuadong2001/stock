#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"提取同花顺app新闻"
#
#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
#


import requests
import random
import time
import bs4
import re
import json
import time
import akshare as ak
import pandas as pd
import libs.common as common

#headers = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
#headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
headers = {'User-Agent': 'platform=gphone&version=G037.08.588.1.32'}

#"数据结构"
#"日期 代码 名称 数量 新闻"
#数量是新闻数量
#"新闻数据结构"
#时间 来源 标题 链接地址




class News(object):
    def __init__(self):
        self.__m_url = "https://m.0033.com/listv4/hs/"
        self.data = pd.DataFrame()
        self.block_code_list = {}
        self.subcodeCount = ""
        self.__stock_column = ['date','code','name','news']
        self.stock_board_concep_or_industry_cons_ths_df = pd.DataFrame()
        self.stock_board_concep_or_industry_name_ths_df = pd.DataFrame()
            
    def __get_single_code_news_url(self,name):
        pn = 1
        if self.block_code_list.get(name):
#            print('code name', name)
            code = self.block_code_list[name]
            self.url = self.__m_url + code + '_' + str(pn) + ".json"            
        else:
            print("该股票代码不存在！")  

    
    def __get_single_code_news_list(self, name):
        self.__get_single_code_news_url(name)
#        print(self.url, headers)
        r = requests.get(self.url, headers=headers)
#        print(r)
        code = self.block_code_list[name]
#        print(r.text)
        if r.status_code == 403:
            print("Too fast, Forbidden!")
            time.sleep(1234)
            self.__get_single_code_news_list(name)
        else:
            jsonData = r.text
            try:
                text = json.loads(jsonData)
            except IndexError:
                time.sleep(random.uniform(0.57, 1.08))
                self.__get_single_code_news_list(name)
            pageitem = text['data']['pageItems']
            for p in pageitem:                           
                t = p['ctime']         
                tt = int(t)
                ttt = time.localtime(tt)
                datetime_str = time.strftime("%Y-%m-%d",ttt)    #时间戳转换正常时间
                datetime_int = time.strftime("%Y%m%d",ttt)
                new = pd.DataFrame({'date':datetime_int,'code':code,'name':name,'source':p['source'],'news':p['title'],'url':p['url']},index = [0])
                self.data=self.data.append(new,ignore_index=True)   # ignore_index=True,表示不按原来的索引，从0开始自动递增
                
    def __get_board_news_list(self):
        s = "+"
        for n in self.block_code_list:
            print(s, end="\r")
            s = s + "+"
            try:
                self.__get_single_code_news_list(n)
            except IndexError as e:
                print("error :", e)
            finally:
                time.sleep(random.uniform(0.57, 1.08))
                pass
        print("+", end="\n")


    def __get_block_code_count(self):
 #       self.url = "http://m.10jqka.com.cn/hq/rank/concept.html#885934"
        self.url = "http://d.10jqka.com.cn/v2/blockrank/885934/199112/d15.js"
        print(self.url, headers)
        r = requests.get(self.url, headers=headers)
        if r.status_code == 403:
            print("Too fast, Forbidden!")
            time.sleep(1234) 
            self.__get_block_code_count()            
        else:
            jsonData = r.text
            #获取到js数据不标准，需要简单处理            
            jsonData = jsonData.lstrip("quotebridge_v2_blockrank_885934_199112_d15(")
            jsonData = jsonData.rstrip(")")
            text = json.loads(jsonData)                       
            count = text['block']['subcodeCount']
            self.subcodeCount = str(count)
            print(count)
            time.sleep(random.uniform(0.57, 1.08))
 
    def __get_block_code_list(self):
        self.__get_block_code_count()
        self.url = "http://d.10jqka.com.cn/v2/blockrank/885934/199112/d" + self.subcodeCount + ".js"
#        print(self.url, headers)    
        r = requests.get(self.url, headers=headers)
        if r.status_code == 403:
            print("Too fast, Forbidden!")            
            time.sleep(1234)     
            self.__get_block_code_list()
        else:
            jsonData = r.text
            #获取到js数据不标准，需要简单处理 
            jsonData = jsonData.lstrip("quotebridge_v2_blockrank_885934_199112_d")
            jsonData = jsonData.lstrip(self.subcodeCount)
            jsonData = jsonData.lstrip("(")
            jsonData = jsonData.rstrip(")")
            text = json.loads(jsonData)                       
            items = text['items']
            #把获取到的股票名称 和代码 放入列表
            for i in items:
                name = i['55']
                self.block_code_list[name] = i['5']
            print(self.block_code_list)
            time.sleep(random.uniform(0.57, 1.08))   
   

    def __get_board_code_list_from_akshare(self):
        df = self.stock_board_concep_or_industry_cons_ths_df
        print(df.shape[0])
        j = 0
        for i in df['名称']:
            self.block_code_list[i] = df.at[j,'代码']
            j = j+1
#        print(self.block_code_list,j)

   
    def __store_to_sql(self,symbol):
        try:
            my_private_stock = self.data
            if symbol == "元宇宙":
                block_name = 'stock_concep_yuanyuzhou'
            elif symbol == "中药":
                block_name = 'stock_concep_zhongyao'
            else:
                block_name = 'stock_concep_none'
            common.insert_db(my_private_stock, block_name , True, "`date`,`code`,`news`")
        except Exception as e:
            print("error :", e)
        return       
        
    def __read_from_sql(self):
        return
    
    def get_data(self,symbol):
        datetime_str = time.strftime("%Y-%m-%d_%H-%M-%S")    #时间戳转换正常时间
        print(datetime_str)
        self.data = pd.DataFrame()
        self.block_code_list = {}
        try:
            self.stock_board_concep_or_industry_cons_ths_df = ak.stock_board_concept_cons_ths(symbol=symbol)
        except Exception as e:
            print("error :", e)
            self.stock_board_concep_or_industry_cons_ths_df = ak.stock_board_industry_cons_ths(symbol=symbol)
#        print(self.stock_board_concep_or_industry_cons_ths_df)
        self.__get_board_code_list_from_akshare()
        self.__get_board_news_list()
        self.__store_to_sql(symbol)
        print("news sizes:",self.data.size)
        print("stock totals:",len(self.block_code_list))
        name = '/data/logs/excel/'+ symbol + '-' + datetime_str + '.xlsx'
        self.data.to_excel(name,index = False)
        print(name,"saved")
        return self.data

    def get_concep_and_industry_name(self):
        datetime_str = time.strftime("%Y-%m-%d_%H-%M-%S")
        self.stock_board_concep_or_industry_name_ths_df = ak.stock_board_concept_name_ths()
        self.stock_board_concep_or_industry_name_ths_df.columns = ['date', 'name', 'number', 'url', 'code']
        try:
            my_private_stock = self.stock_board_concep_or_industry_name_ths_df
            block_name = 'stock_board_concept_name'
            common.insert_db(my_private_stock, block_name , True, "`date`,`name`")
        except Exception as e:
            print("error :", e)
        name = '/data/logs/excel/board_concept_'+ datetime_str + '.xlsx'
        self.stock_board_concep_or_industry_name_ths_df.to_excel(name,index = False)
        self.stock_board_concep_or_industry_name_ths_df = ak.stock_board_industry_name_ths()
        name = '/data/logs/excel/board_industry_'+ datetime_str + '.xlsx'
        self.stock_board_concep_or_industry_name_ths_df.to_excel(name,index = False)

def main():
    global end_time, thread_num
    end_time = "2021-01-01 00:00:00"
    n = News()
    n.get_concep_and_industry_name()
    n.get_data('元宇宙')
  #  n.get_data('中药')
    print('done')



if __name__ == '__main__':
    main()
