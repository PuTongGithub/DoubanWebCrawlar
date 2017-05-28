import requests
from lxml import etree
import re
import time

class Douban:
    def __init__(self):
        self.list_sleep_time = 0.5
        self.data_sleep_time = 0.5
        self.main_url = 'https://movie.douban.com'
        self.list_path = '/tag'
        self.list_next_page_query = '?start={0}&type=T'
        self.main_headers = {
            'Host': 'movie.douban.com',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:53.0) Gecko/20100101 Firefox/53.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://movie.douban.com/tag/',
            'Cookie': 'viewed="5905439"; bid=NBloB1Us9f8; gr_user_id=37fbc163-03d1-4020-88ed-3f2d8e443923; __utma=30149280.182428951.1495358969.1495695690.1495780958.4; __utmz=30149280.1495695690.3.3.utmcsr=bing|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); ll="118371"; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1495780954%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_id.100001.4cf6=715798761c2b9040.1495358976.3.1495781310.1495701649.; __utma=223695111.1138780141.1495358976.1495695429.1495780958.3; __utmz=223695111.1495695429.2.2.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __yadk_uid=kJJnBOxUR4E0EZGqdjmVuQgRExMgLRmI; ap=1; _vwo_uuid_v2=00155C1FC5702A31286CF5A87975D698|3ef9749a4fa85cf859df89d7a67e2253; _pk_ses.100001.4cf6=*; __utmb=30149280.0.10.1495780958; __utmc=30149280; __utmb=223695111.7.10.1495780958; __utmc=223695111; __utmt=1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.cookie_key = '__ads_session'
        self.cookie_value = ''
        set_file = open('set.dat')
        set = set_file.readlines()
        self.lists_first = int(set[0])
        self.lists_last = int(set[1])
        set_file.close()

    def res_cookie(self, cookie):
        strs = cookie.split('; ')
        return [(x + ';') for x in strs if (self.cookie_key in x)][0]

    def get_list(self, tag):
        list_url = self.main_url + self.list_path + '/' + str(tag)
        list_r = requests.get(list_url, headers = self.main_headers)
        page_count = 0
        while True:
            #save cookie value
            self.cookie_value = self.res_cookie(list_r.headers['Set-Cookie'])
            #return url list
            list_t = etree.HTML(list_r.text)
            list = list_t.xpath('//a[@class=""]/@href')
            if len(list) > 0:
                yield list
                page_count += 1
                #get next page
                next_url = list_url + self.list_next_page_query.format(page_count * 20)
                list_r = requests.get(next_url, headers = self.main_headers)
                time.sleep(self.list_sleep_time)
            else: break

    def get_str(self, strs):
        if len(strs) > 0:
            return strs[0]
        else:
            return ''

    def get_data(self, url, data_headers):
        data_r = requests.get(url, headers = data_headers)
        data = {}
        if data_r.status_code != 200: return data
        data['douban_id'] = url.split('/')[-2]
        data_t = etree.HTML(data_r.text)
        titles = data_t.xpath('//span[@property="v:itemreviewed"]/text()')[0]
        space_pos = titles.find(' ')
        data['title'] = titles[0:space_pos]
        data['original_title'] = titles[0] if space_pos == -1 else titles[space_pos:-1] 
        data['poster_url'] = data_t.xpath('//img[@rel="v:image"]/@src')[0]
        datas = str(data_t.xpath('string(//div[@id="info"])'))
        data['director'] = self.get_str(re.findall(pattern = '导演: (.*?)\n', string = datas))
        data['writers'] = self.get_str(re.findall(pattern = '编剧: (.*?)\n', string = datas))
        data['actors'] = self.get_str(re.findall(pattern = '主演: (.*?)\n', string = datas))
        data['producer_area'] = self.get_str(re.findall(pattern = '制片国家/地区: (.*?)\n', string = datas))
        data['language'] = self.get_str(re.findall(pattern = '语言: (.*?)\n', string = datas))
        data['release_data'] = self.get_str(re.findall(pattern = '上映日期: (.*?)\n', string = datas))
        data['film_length'] = self.get_str(re.findall(pattern = '片长: (.*?)\n', string = datas))
        data['other_title'] = self.get_str(re.findall(pattern = '又名: (.*?)\n', string = datas))
        data['imdb_id'] = self.get_str(re.findall(pattern = 'IMDb链接: (.*?)\n', string = datas))
        score = data_t.xpath('//strong[@class="ll rating_num"]/text()')
        data['douban_score'] = 'none' if len(score) == 0 else score[0]
        plots_data = data_t.xpath('string(//span[@property="v:summary"])')
        plots = re.findall(pattern = '\u3000\u3000(.*?)\n', string = plots_data)
        plot = ''
        for s in plots: plot += (s + '\n')
        data['plot'] = plot
        return data

    def get_datas(self, url_list):
        data_headers = self.main_headers.copy()
        data_headers['Cookie'] += self.cookie_value
        for url in url_list:
            yield self.get_data(url, data_headers)
            time.sleep(self.data_sleep_time)

    def get_all_datas(self):
        for tag in range(self.lists_first, self.lists_last):
            for list in self.get_list(tag):
                for data in self.get_datas(list):
                    yield data
                set_file = open('set.dat', 'w')
                set_file.write(str(tag + 1) + '\n')
                set_file.write(str(self.lists_last))
                set_file.close()