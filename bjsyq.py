#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2019-06-28 22:39:25
# Project: bjsyqw

from pyspider.libs.base_handler import *
import os
##���������
import io
##����������ʽ
import re
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
    base_dir = "F:/bjsyq"
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    ##����������ڷ���
    def on_start(self):
        for num in range(1,21):
            self.crawl('http://www.bjsyqw.com/qiche/'+str(num)+'.shtml', callback=self.index_page,validate_cert=False)
            
    def index_page(self,response):
        for info_a in response.doc(".list-point > li.item > a").items():
            print info_a.attr.href
            self.crawl(info_a.attr.href,fetch_type='js',callback=self.detail_page,validate_cert=False)
            
    def detail_page(self,response):
        ##��ȡ������Ϣ������ΪUnicode��ʽ
        title = response.doc(".article-title").text().decode("utf-8")
        date = response.doc(".date").text().decode("utf-8")
        source = response.doc(".source").text().decode("utf-8")
        editor = response.doc(".editors").text().decode("utf-8")
        context = ""
        for context_p in response.doc(".BSHARE_POP > p").items():
            text = context_p.text()
            if text:
                context = context+text+"\n"
            
        if not editor:
            editor = "".decode("utf-8")
        
        title = re.sub(r'[\\/:*"?|<>]','',title)
        
        ##����������Ϣ�ļ���
        info_dir = self.base_dir+"/"+title+"/"
        if not os.path.exists(info_dir):
            os.mkdir(info_dir)
            
        ##������Ϣд���ļ�
        with io.open(info_dir+title+".txt","w+",encoding="utf-8") as f:
            f.write(title+"\n")
            f.write(date+"\n")
            f.write(source+"\n")
            f.write(editor+"\n")
            f.write(context.decode("utf-8"))
            f.flush()
            
        ##����ͼƬ�ļ���
        img_dir = info_dir+"/img"
        if not os.path.exists(img_dir):
            os.mkdir(img_dir)
        
        ##��ȡ����ͼƬ
        img_num = 1
        for img in response.doc(".bshare-image2share > .BSHARE_IMAGE").items():
            img_src = img.attr.src
            self.crawl(img_src,callback=self.down_page,validate_cert=False,save={"img_dir":img_dir,"img_num":img_num})
            img_num += 1
            
    ##����ͼƬ
    def down_page(self,response):
        img_data = response.content
        with io.open(response.save["img_dir"]+"/"+str(response.save["img_num"])+".jpg","wb+") as photo_file:
            photo_file.write(img_data)
            photo_file.flush()
            