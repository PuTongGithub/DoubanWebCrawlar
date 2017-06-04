import requests
from lxml import etree
import re
import time
from url_check import D_tree

class Douban:
    def __init__(self):
        self.list_sleep_time = 0.2
        self.data_sleep_time = 0.3
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
            'Cookie': 'll="118371"; bid=z4GRBn7NmTI; __ads_session=T3814has6gjrafsAfgA=; _pk_id.100001.4cf6=3f2624e8d8e5cadf.1495968834.1.1495968848.1495968834.; _pk_ses.100001.4cf6=*; __utma=30149280.646039394.1495968834.1495968834.1495968834.1; __utmb=30149280.0.10.1495968834; __utmc=30149280; __utmz=30149280.1495968834.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utma=223695111.1871929650.1495968834.1495968834.1495968834.1; __utmb=223695111.0.10.1495968834; __utmc=223695111; __utmz=223695111.1495968834.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __yadk_uid=FbGIKgjVvhE4MufTvhIPodZNarSemX7P',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.cookie_key = '__ads_session'
        self.cookie_value = ''
        #get bad connection url from file
        self.check_tree = D_tree()
        url_pool_file = open('bad_connection.dat')
        self.url_pool = []
        for url in url_pool_file.readlines():
            self.url_pool.append(url.strip())
        url_pool_file.close()
        #get lists key value from file
        set_file = open('set.dat')
        set = set_file.readlines()
        if len(set) < 2:
            self.lists_first = 1880
            self.lists_last = 2025
        else:
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
            if 'Set-Cookie' in list_r.headers.keys():
                self.cookie_value = self.res_cookie(list_r.headers['Set-Cookie'])
            #return url list
            list_t = etree.HTML(list_r.text)
            list = list_t.xpath('//a[@class=""]/@href')
            if len(list) > 0:
                print(page_count) #test output
                yield list
                page_count += 1
                #get next page
                next_url = list_url + self.list_next_page_query.format(page_count * 20)
                list_r = requests.get(next_url, headers = self.main_headers)
                time.sleep(self.list_sleep_time)
            else: break

    def rm_quote(self, s):
        while True:
            pos = s.find('"')
            if pos == -1: break
            s = s[:pos] + ' ' + s[pos+1:]
        return s

    def get_str(self, strs):
        if len(strs) > 0:
            s = self.rm_quote(strs[0])
            if len(s) > 255:
                return s[0:255]
            else:
                return s
        else:
            return ''

    def get_data(self, url, data_headers):
        data_r = requests.get(url, headers = data_headers)
        data = {}
        if data_r.status_code != 200:
            self.url_pool.append(url)
            url_pool_file = open('bad_connection.dat', 'w+')
            url_pool_file.write(url)
            url_pool_file.close()
            return data
        data['douban_id'] = url.split('/')[-2]
        data_t = etree.HTML(data_r.text)
        data['title'] = self.rm_quote(data_t.xpath('//title/text()')[0].strip().rstrip('(豆瓣)'))
        data['original_title'] = self.get_str(data_t.xpath('//span[@property="v:itemreviewed"]/text()'))
        data['poster_url'] = data_t.xpath('//img[@rel="v:image"]/@src')[0]
        datas = str(data_t.xpath('string(//div[@id="info"])'))
        data['director'] = self.get_str(re.findall(pattern = '导演: (.*?)\n', string = datas))
        data['writers'] = self.get_str(re.findall(pattern = '编剧: (.*?)\n', string = datas))
        data['actors'] = self.get_str(re.findall(pattern = '主演: (.*?)\n', string = datas))
        data['type'] = self.get_str(re.findall(pattern = '类型: (.*?)\n', string = datas))
        data['producer_area'] = self.get_str(re.findall(pattern = '制片国家/地区: (.*?)\n', string = datas))
        data['language'] = self.get_str(re.findall(pattern = '语言: (.*?)\n', string = datas))
        data['release_data'] = self.get_str(re.findall(pattern = '上映日期: (.*?)\n', string = datas))
        data['film_length'] = self.get_str(re.findall(pattern = '片长: (.*?)\n', string = datas))
        data['other_title'] = self.get_str(re.findall(pattern = '又名: (.*?)\n', string = datas))
        data['imdb_id'] = self.get_str(re.findall(pattern = 'IMDb链接: (.*?)\n', string = datas))
        score = data_t.xpath('//strong[@class="ll rating_num"]/text()')
        data['douban_score'] = 'none' if len(score) == 0 else score[0]
        plots_data = self.rm_quote(data_t.xpath('string(//span[@property="v:summary"])'))
        plots = re.findall(pattern = '\u3000\u3000(.*?)\n', string = plots_data)
        plot = ''
        for s in plots: plot += (s + '\n')
        data['plot'] = plot
        return data

    def get_datas(self, url_list):
        data_headers = self.main_headers.copy()
        data_headers['Cookie'] += self.cookie_value
        for url in url_list:
            strs = url.split('/')
            if len(strs) < 2: continue
            if not self.check_tree.check(strs[-2]):
                yield self.get_data(url, data_headers)
                time.sleep(self.data_sleep_time)

    def get_bad_connect_data(self):
        url_pool_file = open('bad_connection.dat', 'w')
        url_pool_file.write('')
        url_pool_file.close()
        for url in self.url_pool:
            strs = url.split('/')
            if len(strs) < 2: continue
            if not self.check_tree.check(strs[-2]):
                yield self.get_data(url, self.main_headers)
                time.sleep(self.data_sleep_time)

    def get_all_datas(self):
        for tag in range(self.lists_first, self.lists_last):
            print(tag)  #test output
            for list in self.get_list(tag):
                for data in self.get_datas(list):
                    yield data
            set_file = open('set.dat', 'w')
            set_file.write(str(tag + 1) + '\n')
            set_file.write(str(self.lists_last))
            set_file.close()
