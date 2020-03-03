# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Crawler1020BagItem(scrapy.Item):
    # define the fields for your item here like:
    item_urls = scrapy.Field()
    title = scrapy.Field()
    item_name = scrapy.Field()
    item_price = scrapy.Field()
    product_code = scrapy.Field()
    country = scrapy.Field()
    company = scrapy.Field()
    options = scrapy.Field()
    category_code = scrapy.Field()
    category_name = scrapy.Field()
    image_urls = scrapy.Field()

    pass
