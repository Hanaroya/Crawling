import scrapy
import logging
import datetime
import csv
import requests
from ..items import Crawler1020BagItem
from scrapy.http import FormRequest
from scrapy.utils.response import open_in_browser

logging.getLogger().addHandler(logging.StreamHandler())

class Spider_1020bag(scrapy.Spider):
    name = 'bag1020'
    items = Crawler1020BagItem()
    user_id = ''
    user_password = ''
    url_page_number = 2
    url_item_number = 0
    url_item_count = 0
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    host = 'http://1020bag.com'
    start_urls = [
        'http://1020bag.com/'
    ]
    item_urls = []
    item_details = {
        'url': [],
        'title': [],
        'price': [],
        'product_code': [],
        'country': [],
        'company': [],
        'options': [],
        'category_code': [],
        'category_name': [],
        'image_urls': [],
    }

    @staticmethod
    def str_remove(str_in):
        r_str = str(str_in).replace('[', '')
        r_str = r_str.replace(']', '')
        r_str = r_str.replace('\'', '')
        return r_str

    @staticmethod
    def tab_newline_remove(str_in):
        r_str = str(str_in).replace('\t', '')
        r_str = r_str.replace('\n', '')
        r_str = r_str.replace(' ', '')
        return r_str

    def csv_file_writer(self, response):
        items_details = [
            'url',
            'title',
            'price',
            'product_code',
            'country',
            'company',
            'options',
            'category_code',
            'category_name',
            'image_urls',
        ]
        test = []
        with open('1020_bag.csv', 'w', newline='') as new_file:
            csv_writer = csv.DictWriter(new_file, fieldnames=items_details, dialect='excel',
                                        quoting=csv.QUOTE_NONNUMERIC)
            csv_writer.writeheader()
            for data in self.item_details:
                print("Length of lists: " + str(len(self.item_details[data])))
                test.append(self.item_details[data])
            i = 0
            for each in test[0]:
                csv_writer.writerow({'url': test[0][i], 'title': test[1][i], 'price': test[2][i],
                                     'product_code': test[3][i], 'country': test[4][i], 'company': test[5][i],
                                     'options': test[6][i], 'category_code': test[7][i],
                                     'category_name': test[8][i], 'image_urls': test[9][i], })
                i += 1

    def start_requests(self):
        self.user_id = 'chanhee83'
        self.user_password = 'pw110326**'

        return [FormRequest(url='http://1020bag.com/member/login_ps.php',
                            formdata={
                                'returnUrl': 'http://1020bag.com/',
                                'loginId': self.user_id,
                                'loginPwd': self.user_password,
                                },
                            callback=self.after_login
                            )]

    def after_login(self, response):
        return scrapy.Request(url='http://1020bag.com/goods/goods_list.php?page=1&cateCd=001',
                              callback=self.parse_list,
                              meta={'page': 1, 'update': self.today})
        # return scrapy.Request(url='http://1020bag.com/goods/goods_view.php?goodsNo=6884',
        #                       callback=self.parse_item,
        #                       meta={'page': 1, 'update': self.today})

    def parse_list(self, response):
        item_url = response.css('div.item_link a::attr(href)').extract()
        item_url_sold_out = response.css('div.item_cont a::attr(href)').extract()

        self.items['item_urls'] = item_url
        self.items['item_urls'] = item_url_sold_out
        self.items['item_urls'] = list(dict.fromkeys(self.items['item_urls']))
        self.item_urls.extend(self.items['item_urls'])

        if self.url_page_number <= 10:
           # print("HERE IS UPDATING PAGE NUMBER: " + str(self.url_page_number))
            url_start = 'http://1020bag.com/goods/goods_list.php?page='
            url_end = '&cateCd=001'
            next_url = url_start + str(self.url_page_number) + url_end
            self.url_page_number += 1
            yield scrapy.Request(next_url, callback = self.parse_list,
                                  meta={'page': self.url_page_number, 'update': self.today})
        elif self.url_page_number >= 10:
            self.url_item_count = 0
            self.url_item_number = len(self.item_urls)
            item = self.item_urls[self.url_item_count]
            item = str(item).replace('..', '')
            item = self.host + item
            self.url_item_count += 1
            print("리스트 길이: " + str(self.url_item_number))
            yield scrapy.Request(item, callback=self.parse_item,
                                 meta={'page': 1, 'update': self.today})

    def parse_item(self, response):
        item_detail = {
                        'title': '',
                        'product_code': '',
                        'company': '',
                        'price': '',
                        'country': '',
                        'options': [],
                        'category_code': [],
                        'category_name': [],
                        'image_urls': [],
                        'url': response.url
                       }
        cate_names = []

        title = str(response.css('div.item_detail_tit h3::text').extract())
        title = self.str_remove(title)

        product_code = str(response.css('div.item_detail_list dl:nth-child(1) dd::text').extract_first())
        product_code = self.str_remove(product_code)

        short_explain = str(response.css('div.item_detail_list dl:nth-child(2) dt::text').extract_first())

        css_input = ''
        css_input2 = ''
        if short_explain == "짧은설명":
            css_input = 'div.item_detail_list dl:nth-child(4) dd::text'
            css_input2 = 'div.item_detail_list dl:nth-child(7) dd::text'
        else:
            css_input = 'div.item_detail_list dl:nth-child(3) dd::text'
            css_input2 = 'div.item_detail_list dl:nth-child(6) dd::text'

        company = str(response.css(css_input).extract())
        company = self.str_remove(company)
        company = self.tab_newline_remove(company)

        price = str(response.css('div.item_detail_list dl.item_price dd strong::text').extract())
        price = self.str_remove(price)

        country = str(response.css(css_input2).extract())
        country = self.str_remove(country)
        country = self.tab_newline_remove(country)

        options = response.css('select[name="optionSnoInput"] option::text').extract()

        category_name = response.css('div.location_tit span::text').extract()

        category_code = response.css('div.location_select li a::attr(href)').extract()
        category_code_check = response.css('div.location_select li span::text').extract()

        image_url = response.css('div.item_photo_big span.img_photo_big img::attr(src)').extract_first()

        item_detail['title'] = title
        item_detail['product_code'] = product_code
        item_detail['company'] = company
        item_detail['price'] = price
        item_detail['country'] = country

        n_options = []
        for option in options:
            n_options.append(self.tab_newline_remove(str(option)))
        item_detail['options'] = n_options[1:]

        for cate_name in category_name:
            cate_names.append(str(cate_name))
        item_detail['category_name'] = category_name

        n_cate_code = []
        i = 0
        for cate in category_code:
            cate = str(cate).split('=')[1]
            if str(category_code_check[i]) in cate_names:
                n_cate_code.append(cate)
            i += 1
        item_detail['category_code'] = n_cate_code

        image_url_con = self.host + str(image_url)
        item_detail['image_urls'] = image_url_con

        self.item_details['url'].append(item_detail['url'])
        self.item_details['title'].append(item_detail['title'])
        self.item_details['product_code'].append(item_detail['product_code'])
        self.item_details['company'].append(item_detail['company'])
        self.item_details['price'].append(item_detail['price'])
        self.item_details['country'].append(item_detail['country'])
        self.item_details['options'].append(item_detail['options'])
        self.item_details['category_name'].append(item_detail['category_name'])
        self.item_details['category_code'].append(item_detail['category_code'])
        self.item_details['image_urls'].append(item_detail['image_urls'])

        if self.url_item_count < self.url_item_number:
            item = self.item_urls[self.url_item_count]
            item = str(item).replace('..', '')
            item = self.host + item
            self.url_item_count += 1
            #print(str(self.url_item_count) + " " + str(self.url_item_number))
            yield scrapy.Request(item, callback=self.parse_item,
                                  meta={'page': 1, 'update': self.today})
        else:
            yield response.follow('http://1020bag.com/', callback=self.csv_file_writer,
                                  meta={'page': self.url_page_number, 'update': self.today})

        # print("HERE IS UPDATING PAGE NUMBER: " + str(self.url_page_number))
        # url_start = 'http://1020bag.com/goods/goods_list.php?page='
        # url_end = '&cateCd=001'
        # next_url = url_start + str(self.url_page_number) + url_end
        # self.url_page_number += 1
