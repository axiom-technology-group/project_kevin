#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2019-06-29 09:34:19
# Project: 19lou

from pyspider.libs.base_handler import *
import os
##���������
import io
##����������ʽ
import re
##����ϵͳĬ�ϱ��뼯
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class Handler(BaseHandler):
    crawl_config = {
        'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36 LBBROWSER'
        },'itag': 'v244'
    }
    
    ##���û��������ļ��е�ַ
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
        ##��ȡ���±���
        for title in response.doc("title").items():
            all_title = title.text()
            print all_title
            titles = all_title.split("-")[::-1]
            sub_dir = "F:/19lou"
            for subtitle in titles:
                sub_dir = sub_dir+"/"+subtitle
                if not os.path.exists(sub_dir):
                    os.mkdir(sub_dir)
            ##һ�������������µ��ļ��о���sub_dir        
            artical_dir = sub_dir
        
        print artical_dir
        
        context = ""
        ##�ж��Ƿ���img�ӱ�ǩ�����⡰�ղء�����
        for text_div in response.doc(".post-cont>div>div").items():
            if not text_div.children("img"):
                context += text_div.text()+"\n"
        
        ##����������д���ļ�
        with io.open(artical_dir+"/"+all_title+".txt","w+",encoding="utf-8") as f:
            f.write(context.decode("utf-8"))
            f.flush()
        
        ##��ȡ�����е�ͼƬ��������
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