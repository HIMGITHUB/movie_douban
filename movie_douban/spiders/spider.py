#encoding:utf-8
__author__ = 'Xdtherion'
import scrapy
from lxml import etree
from movie_douban.items import movie_doubanItem,get_trItem
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from scrapy.selector import Selector
import csv
from scrapy import FormRequest
from selenium import webdriver
import time
import re
# import webkit
class movie_douban(CrawlSpider):
    u'''
    获取豆瓣排行前250名的电影名称,并存入csv文件
    '''
    name = "movie_douban"
    allowed_domains = ['movie.douban.com']
    start_urls = ['http://movie.douban.com/top250']
    base_url = 'http://movie.douban.com/top250'
    u'''
    伪装浏览器头
    '''
    headers={
        "accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "accept-encoding":"gzip,deflate,sdch",
        "accept-language":"zh-CN,zh;q=0.8,en;q=0.6",
        "cache-control":"max-age=0",
        "upgrade-insecure-requests":"1",
        "user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36",
        "referer":"https://movie.douban.com/top250"
    }

    cookies = {
        'bid': '"lxDDkObREFY"',
        'll': '"118371"',
        '__utma': '30149280.2113389534.1458011110.1461490522.1461576903.19',
        '__utmc': '30149280',
        '__utmz': '30149280.1460125455.14.6.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided)',
        '__utma': '223695111.2019279675.1458011110.1461490522.1461576903.14',
        '__utmc': '223695111',
        # '__utmz': '223695111.1458011110.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
        '_pk_id.100001.4cf6':'fe72f4b21c2bc3ea.1458011110.14.1461577160.1461490522.'
    }
    u'''
    手动发起第一次请求，目的是加载headers，不写这个start_requests函数会直接请求start_urls里的网址，不会附加headers和cookies
    '''

    def start_requests(self):
        return [Request("https://movie.douban.com/top250",headers=self.headers)]

    u'''
    默认处理返回报文response的函数，在这里，通过分析返回报文，从而进一步处理报文中的链接和内容
    '''
    def parse(self, response):
        item = movie_doubanItem()
        selector = Selector(response)
        u'''
        使用xpath，解析返回的HTML内容，获取所有class为info的div标签，包含了标签内所有内容，所有可以在后续的for循环中继续处理每一段div标签
        '''
        Movies = selector.xpath('//div[@class="info"]')
        for eachMovie in Movies:
            u'''
            每一段div标签依然是HTML，故可以继续使用xpath对其进行解析
            这里span[1]，表示a标签下第一个span标签，并不是所有该类标签的数组，顾而可以直接使用
            若不标记[1],则会将所有span存入数组返回。
            '''
            item['title'] = eachMovie.xpath('div[@class="hd"]/a/span[1]/text()').extract()[0]
            movieInfos = eachMovie.xpath('div[@class="bd"]/p/text()').extract()
            u'''
            将movieInfos数组组合成字符串，用；分割
            '''
            movieInfo = ";".join(movieInfos)
            u'''
            去除字符串里的所的双空格，目的是减少空格，但不删除分割用的单个空格
            '''
            movieInfo = movieInfo.replace("  ","")
            u'''
            ！！！！！！！！！！！！！！清除字符串中的空格！！！！！！！！！！！
            将movieinfo按照空格拆分成字符串数组，再将数组重新组合成字符串按照
            ！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
            '''
            item['movieInfo'] = "".join(movieInfo.split())
            item['star'] = eachMovie.xpath('div[@class="bd"]/div/span[@class="rating_num"]/text()').extract()[0]
            quotes = eachMovie.xpath('div[@class="bd"]/p[2]/span/text()').extract()
            if quotes:
                quote = quotes[0]
            else:
                quote = ''
            item['quote'] = quote
            item['quo_num'] = eachMovie.xpath('div[@class="bd"]/div/span[4]/text()').extract()[0]
            yield item
        nextLink = selector.xpath('//span[@class="next"]/link/@href').extract()
        if nextLink:
            nextLink = nextLink[0]
            u'''
            递归调用解析函数parse
            '''
            yield Request(self.base_url+nextLink, callback=self.parse, headers=self.headers)

class get_tr(CrawlSpider):
    u'''
    从csv文件里获取电影名称，并登陆另一个网站，模拟搜索电影下载链接
    '''
    name = "movie_gettr"
    allowd_domains = ['www.dy2018.com']
    start_urls = ['http://www.dy2018.com']
    base_url = 'http://www.dy2018.com'

    def parse(self, response):
        u'''
        使用csv空间，读取存有电影名称的csv文件，
        每取到一个电影名称都去另一个网站查询电影
        :param response:
        :return:
        '''
        csvfile = file('./output/movies_info1.csv','rb')
        reader = csv.reader(csvfile)
        u'''
        观察得出，每一行的第三列是电影名称
        '''
        for rows in reader:
            name = rows[2]
            if name != 'title':
                # print name.decode('utf-8')
                u'''
                1.这里执行请求页面需要提交表单，所以使用FormRequest
                2.由于request的回调函数只支持一个参数，如有额外参数需要传送给回调函数的话，
                一个比较简单的方法是在request里使用meta参数，将需要额外传给回调函数的参数以字典的形式发送给服务器，再在毁掉函数中使用response.meta来调取使用
                （应该是发送给服务器，然后服务器将meta不处理直接返回在response里，未验证！）
                3.formdata则是提交的表单数据，可能需要解码
                '''
                yield FormRequest.from_response(response,self.base_url,meta={'name':name}, formdata={'keyboard': name.decode('utf-8')}, callback=self.further_parse)
        csvfile.close()
        # print 'csvfile.close()'
    pass

    def further_parse(self, response):
        '''
        二级解析函数，继续解析上一级parse函数爬取的网址，主要是将所有查询结果中的链接打开，继续深层次爬取其中的内容
        :param response:
        :return:
        '''
        selector = Selector(response)
        Movies = selector.xpath('//a[@class="ulink"]/@href').extract()
        name = response.meta["name"]
        if Movies:
            for movie in Movies:
                yield Request(self.base_url+movie,meta={'name':name}, callback=self.further_parse2)
        pass

    def clean_strlist(self, strlist):
        for str in strlist:
            str = str.replace(" ", "")
            while str.find("\r\n\r\n") != -1:
                str = str.replace("\r\n\r\n","\r\n")
            if not str.split():
                strlist.remove(str)
        return strlist

    def further_parse2(self, response):
        '''
        三级解析函数，将结果页面的下载链接抽出
        1.由于scrapy本身不能处理javascript，所以页面中JS相关的数据都不会有，需要执行JS才能变成最终的页面。
        这里使用selenium，调用浏览器执行返回的html源码，顺带执行其中的JS，从而的到最终的页面。
        2.从最终的页面获取下载标签和地址，由于标签名是使用JS随机生成的，所以xpath暂时无法使用。
        这里使用正则表达式，按照下载链接开头格式处理，获得所有的下载链接以及文件名。
        :param response:
        :return:
        '''
        name = response.meta["name"]
        print name
        item = get_trItem()
        self.browser = webdriver.Firefox()
        self.browser.get(response.url)
        u'''
        正则表达式获取下载链接
        '''
        tx = self.browser.page_source
        self.browser.close()
        tre = r'"thunder://.*?"'
        exere = re.compile(tre, flags=re.S)
        source_links = exere.findall(tx)
        u'''
        xpath获取文件名
        '''
        file_names = self.browser.find_elements_by_xpath(u"//a[@title='迅雷专用高速下载']")
        base = []
        for nms in file_names:
            print nms.text
            base.append(nms.text)
        i = 0
        for s_link in source_links:
            item['name'] = name
            item['source_name'] = file_names[i].text
            item['source_thunder_link'] = s_link
            i += 1
            yield item
        pass