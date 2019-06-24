这是一个pyspdier项目，用于爬取www.xcar.com.cn

pyspider是一个通过web UI界面来操作的python爬虫框架。

使用步骤：
1.安装python2.7或python3.5
2.下载phantomjs，通过pip安装pyspider
3.打开浏览器进入localhost：5000登陆webui
4.创建项目，复制TXT文件中的代码粘贴在右侧的代码区并保存
5.运行

实现情况：
1.在该版本的代码中，已实现将所有车系及其下的所有车型的基本信息爬取并保存到mysql数据库中，包括基本参数以及用户口碑评分
2.将汽车各个方位的照片爬取并下载到指定的文件路径下
