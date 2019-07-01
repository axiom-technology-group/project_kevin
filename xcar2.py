#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2019-06-21
# Project: xcar4

from pyspider.libs.base_handler import *
import os
##引入输出流
import io
##引入正则表达式
import re
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import MySQLdb



class Handler(BaseHandler):
    crawl_config = {
        'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36 LBBROWSER'
        },'itag': 'v244'
    }
    
    ##设置基础数据文件夹地址
    base_dir = "F:/xcar3"
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    
        
    

    ##整体程序的入口方法
    def on_start(self):
        for num in range(1,3):
            self.crawl('http://newcar.xcar.com.cn/car/0-0-0-0-0-0-0-0-0-0-0-'+str(num)+'/', callback=self.index_page,validate_cert=False)
    
    
    carpage_url = "";
    ##取到微型车的a标签的地址，并依次爬取    
    def index_page(self, response):
        for carpage_a in response.doc(".txt_list > .title > a").items():
            carpage_url = carpage_a.attr.href
            self.crawl(carpage_url,callback=self.maincar_page,validate_cert=False,save={"carpage_url":carpage_url})
    
    
    
    ##爬取每款汽车的首页信息
    def maincar_page(self, response):
        ##获取汽车系列名
        bigtitle = response.doc(".lt_f1").text()
        smalltitle = response.doc("h1").text()
        title = bigtitle + smalltitle
        
        ##使用正则表达式，将Windows中不能放在文件夹中的字符都删除掉,删除横杠
        bigtitle = re.sub(r'[\\/:*"?|<>]','',bigtitle)
        bigtitle = bigtitle[:len(bigtitle)-1]
        title = re.sub(r'[\\/:*"?|<>]','',title)
        smalltitle = re.sub(r'[\\/:*"?|<>]','',smalltitle)
        
        print bigtitle
        print title
        
        ##创建汽车品牌文件夹
        car_bigdir = self.base_dir+'/'+bigtitle
        if not os.path.exists(car_bigdir):
            os.mkdir(car_bigdir)
        
        ##创建单个车系文件夹
        car_smalldir = car_bigdir+'/'+title
        if not os.path.exists(car_smalldir):
            os.mkdir(car_smalldir)
            
        ##厂家指导价
        price = response.doc(".ref_gd a").text()
        print price
        arr = price.split("-")
        if len(arr)>=2:
            low_price = float(arr[0])
            high_price = float(arr[1])
        
        
        ##主要指标
        info1_items = response.doc(".w163").items()
        flag = 1
        level = ""
        oil_wear = ""
        guarantee = ""
        for info in info1_items:
            info_txt = info.text().split("：")[1]
            if flag==1:
                level = info_txt
            if flag==2:
                oil_wear = info_txt
            else:
                guarantee = info_txt
            flag+=1
                
                
        info2_items = response.doc(".w220").items()
        flag = 1
        structure = ""
        displacement = ""
        gearbox = ""
        for info in info2_items:
            print info.text()
            info_txt = info.text().split("： ")[1]
            if flag==1:
                structure = info_txt
            if flag==2:
                displacement = info_txt
            else:
                gearbox = info_txt
            flag+=1
                
        
        ## 打开数据库连接
        db = MySQLdb.connect("localhost", "root", "root", "xcar", charset='utf8' )
        db.autocommit(1)
        # 使用cursor()方法获取操作游标 
        cursor = db.cursor()
        # SQL 插入语句
        sql = "INSERT INTO car_series(brand,series,level,structure,low_price,high_price,oil_wear,guarantee,displacement,gearbox) VALUES('%s', '%s', '%s', '%s', %s, %s, '%s', '%s', '%s', '%s')" % (bigtitle, smalltitle, level, structure, low_price, high_price, oil_wear, guarantee, displacement, gearbox)
        print sql
        # 执行sql语句
        cursor.execute(sql)
        
        
        
        
        ##获取车型信息并写入
        type_info = ""
        
        types_a = response.doc("td > p > a").items()
        types_hot = response.doc(".no_td > .heat > div").items()
        list_a = []
        for a in types_a:
            title = a.attr.title
            if title is not None:
                list_a.append(title)
                
        print(list_a)
            
        types_hot = list(types_hot)
        
        num = len(list_a)
        print num
        for i in range(0,num):
            type_name = list_a[i]
            type_hot = types_hot[i].attr.style.split(": ")[1]
            type_hot = re.sub(r'%','',type_hot)
            type_hot = int(type_hot)
            sql = "INSERT INTO car_type(name,hot) VALUES ('%s','%s')" % (type_name,type_hot)
            print sql
            # 执行sql语句
            cursor.execute(sql)
        
        # 关闭数据库连接
        db.close()

            
        ##爬取用户口碑数据，并写入数据库
        self.crawl(response.save["carpage_url"]+"/review.htm",callback=self.review_page,validate_cert=False,save={"series": smalltitle})
           
        
        ##创建汽车照片文件夹
        car_imagedir = car_smalldir+'/imgs'
        if not os.path.exists(car_imagedir):
            os.mkdir(car_imagedir)
        
        
        ##保存汽车简介照片
        photos = response.doc(".a_img > img").items()
        photo_num = 1
        for photo in photos:
            photo_src = photo.attr.src
            self.crawl(photo_src,callback=self.down_page,validate_cert=False,save={"car_dir":car_imagedir,"photo_num":photo_num})
            photo_num += 1
          
        
        
        
        
    
    ##爬取每款汽车的口碑页
    def review_page(self, response):
        
        ##综合评分
        main_info = response.doc(".synthesis > p").text()
        if main_info:
            all_score = float(main_info[5:9])
            print all_score

            appear_score =0
            inner_ornament_score =0
            space_score =0
            confort_score =0
            oilwear_score =0
            power_score =0
            control_score =0
            cost_perform_score =0
            
            ##获取单项特性评分
            scores = response.doc(".column div > div").items()
            
            flag = 1
            for aaa in scores:
                strr = aaa.text()[0:4]
                if flag==1:
                    appear_score = float(strr)
                if flag==2:
                    inner_ornament_score = float(strr)
                if flag==3:
                    space_score = float(strr)
                if flag==4:
                    confort_score = float(strr)
                if flag==5:
                    oilwear_score = float(strr)
                if flag==6:
                    power_score = float(strr)
                if flag==7:
                    control_score = float(strr)
                if flag==8:
                    cost_perform_score = float(strr)
                flag+=1
                
                
            ## 打开数据库连接
            db = MySQLdb.connect("localhost", "root", "root", "xcar", charset='utf8' )
            db.autocommit(1)
            # 使用cursor()方法获取操作游标 
            cursor = db.cursor()
            # SQL 插入语句
            sql = "UPDATE car_series SET all_score ='%s',appear_score ='%s',inner_ornament_score ='%s',space_score ='%s',confort_score ='%s',oilwear_score ='%s',power_score ='%s',control_score ='%s',cost_perform_score ='%s' WHERE series ='%s'" % (all_score,appear_score,inner_ornament_score,space_score,confort_score,oilwear_score,power_score,control_score,cost_perform_score,response.save["series"])
            print sql
            # 执行sql语句
            cursor.execute(sql)
            # 关闭数据库连接
            db.close()

    
    ##下载图片
    def down_page(self,response):
        photo_data = response.content
        with io.open(response.save["car_dir"]+"/"+str(response.save["photo_num"])+".jpg","wb+") as photo_file:
            photo_file.write(photo_data)
            photo_file.flush()