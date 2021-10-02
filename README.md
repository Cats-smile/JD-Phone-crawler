# JD-Phone-crawler

一个爬取京东手机页面的爬虫，包括价格，厂家，品牌，型号，评论等


# Middleware.py

下载中间件，用selenium爬取

class JdSpiderMiddleware(object):

    def __init__(self):
        print('打开了google浏览器')

        # Chrome浏览器
        options = webdriver.ChromeOptions()
        # 设置中文
        options.add_argument('lang=zh_CN.UTF-8')
        # 设置无图加载 1 允许所有图片; 2 阻止所有图片; 3 阻止第三方服务器图片
        prefs = {
            'profile.default_content_setting_values': {
                'images': 2
            }
        }
        options.add_experimental_option('prefs', prefs)
        # 设置无头浏览器
        options.add_argument('--headless')
        self.browser = webdriver.Chrome(chrome_options=options)
        # 设置等待请求网页时间最大为self.timeout
        self.wait = WebDriverWait(self.browser,timeout=20)


    def __del__(self):
        print('关闭Chrome')
        # 爬虫结束后，关闭浏览器
        self.browser.close()

    def process_request(self, request, spider):
        page = request.meta.get('page', 1)
        try:
            print('Selenium启动解析')
            self.browser.get(request.url)
            # 滚动条下拉到底
            self.browser.execute_script("document.documentElement.scrollTop=10000")
            # 等待网页加载完毕
            time.sleep(2)
            # 如果传过来的page不是第一页就需要在最下面的输入页码处，输入page,并按确定键跳转到指定页面
            if page > 1:
                input = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, './/span[@class="p-skip"]/input')))  # 获取输入页面数框
                submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, './/span[@class="p-skip"]/a')))  # 获取确定按钮
                input.clear()
                input.send_keys(page)
                submit.click()
                # 滚动条下拉到底
                self.browser.execute_script('window.scrollTo(0,document.body.scrollHeight)')
                time.sleep(2)
            # 如果当 str(page),即当前页码出现在高亮文本的时候，就代表页面成功跳转
            self.wait.until(
                EC.text_to_be_present_in_element((By.XPATH, './/span[@class="p-num"]/a[@class="curr"]'), str(page)))

            # 等待加载完所有的商品list 然后进一步解析
            self.wait.until(EC.element_to_be_clickable((By.XPATH, './/span[@class="p-skip"]/a')))
            # self.wait.until(EC.presence_of_element_located((By.XPATH,'.//ul[@class="gl-warp clearfix"]/li')))
            time.sleep(1)
            body = self.browser.page_source
            print('selenium开始访问第' + str(page) + '页')
            # 将selenium得到的网页数据返回给parse解析
            return HtmlResponse(url=request.url, body=body, encoding='utf-8', request=request)

        except Exception as E:
            print(str(E))
            return HtmlResponse(url=request.url, status=500, request=request)

# Pipeline.py

将爬取到的数据存到mongodb中

    def __init__(self):
        self.client = pymongo.MongoClient('localhost', 27017)
        scrapy_db = self.client['jd']  # 创建数据库
        self.coll = scrapy_db['scrapyphone']  # 创建数据库中的表格
    def process_item(self, item, spider):
        self.coll.insert_one(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()
