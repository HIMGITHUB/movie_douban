# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class movie_doubanItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = Field()
    movieInfo = Field()
    star = Field()
    quote = Field()
    quo_num = Field()

class get_trItem(Item):
    # tr_link = Field()
    source_thunder_link = Field()
    # movie_info = Field()
    # Chinese_name = Field()
    name = Field()
    source_name = Field()
    # country = Field()
    # Director = Field()
    # Actors = Field()

