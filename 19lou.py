#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2019-06-29 09:34:19
# Project: 19lou

from pyspider.libs.base_handler import *
import os
##引入输出流
import io
##引入正则表达式
import re
##重置系统默认编码集
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class Handler(BaseHandler):
    crawl_config = {
        'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36 LBBROWSER'
        },'itag': 'v244'
    }
    
    ##设置基础数据文件夹地址
    base_dir = "F:/19lou"
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)


    def on_start(self):
        for num in range(1,501):
            self.crawl('https://www.19lou.com/forum-5-'+str(num)+'.html', callback=self.index_page,validate_cert=False)
    

    def index_page(self, response):
        for artical_a in response.doc(".title a").items():
            self.crawl(artical_a.attr.href,fetch_type='js',callback=self.artical_page,validate_cert=False)
    
    def artical_page(self,response):
        artical_dir = ""
        all_title = ""
        ##获取文章标题
        for title in response.doc("title").items():
            all_title = title.text()
            print all_title
            titles = all_title.split("-")[::-1]
            sub_dir = "F:/19lou"
            for subtitle in titles:
                sub_dir = sub_dir+"/"+subtitle
                if not os.path.exists(sub_dir):
                    os.mkdir(sub_dir)
            ##一轮下来最终文章的文件夹就是sub_dir        
            artical_dir = sub_dir
        
        print artical_dir
        
        context = ""
        ##判断是否有img子标签，避免“收藏”字样
        for text_div in response.doc(".post-cont>div>div").items():
            if not text_div.children("img"):
                context += text_div.text()+"\n"
        
        ##将文章正文写入文件
        with io.open(artical_dir+"/"+all_title+".txt","w+",encoding="utf-8") as f:
            f.write(context.decode("utf-8"))
            f.flush()
        
        ##爬取文章中的图片，并保存
        num = 1
        for text_img in response.doc(".post-cont img").items():
            print text_img.attr.src
            self.crawl(text_img.attr.src,callback=self.img_page,validate_cert=False,save={"artical_dir":artical_dir,"photo_num":num})
            num+=1
            
    def img_page(self,response):
        photo_data = response.content
        with io.open(response.save["artical_dir"]+"/"+str(response.save["photo_num"])+".jpg","wb+") as photo_file:
            photo_file.write(photo_data)
            photo_file.flush()