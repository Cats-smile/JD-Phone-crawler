import scrapy
from scrapy import cmdline

name = 'jingdong -o jingdong.csv'
cmd = 'scrapy crawl {0}'.format(name)
cmdline.execute(cmd.split())
