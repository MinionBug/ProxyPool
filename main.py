import asyncio, aiohttp
import time
import requests
import json
from bs4 import BeautifulSoup
#####################
proxies_url = {'http://www.xicidaili.com/wt/','https://www.kuaidaili.com/free/inha/'}
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko/20100101 Firefox/60.0', \
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', \
           'Accept - Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2', \
           'Accept - Encoding': 'gzip, deflate', \
           'Connection': 'keep-alive', \
           'Upgrade-Insecure-Requests': '1'}
tasks = []
raw_proxys ={}
verify_url='http://www.baidu.com'
maxSem= 40

def proxy_loader():
    try:
        with open('agents.json', 'r') as f:
            raw_proxys.update(json.load(f))
            print ('Load File')
    except Exception as e:
        print(e)

def proxy_saver():
    try:
        with open('agents.json', 'w') as f:
            json.dump(raw_proxys, f)
    except Exception as e:
        print (e)

async def proxy_verifier(ip,port,sem):
    verify_headers = {'user_agent':'Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko/20100101 Firefox/60.0'}
    p = 'http://%s:%s' %(ip,port)
    with (await sem):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request('get',verify_url, headers= verify_headers,proxy= p,timeout =5,verify_ssl=False) as resp: #t/i
                    r = await resp.text()
                    if  '11000002000001' in r:  # 备案号
                        print(ip, port, 'OK')
                    else:
                        print(ip, port, 'No')
                        del raw_proxys[ip]
        except Exception as e:
            print(ip, port, 'error',e)
            del raw_proxys[ip]


class ProxyCollector(): #代理们的url在这个地方,应该拿出来,放在配置文件当中。类也要拿出去。
    '''从网络上收集proxy'''
    def __init__(self,page_num):
        self.page_num= page_num
        self.headers =  {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko/20100101 Firefox/60.0', \
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', \
           'Accept - Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2', \
           'Accept - Encoding': 'gzip, deflate', \
           'Connection': 'keep-alive', \
           'Upgrade-Insecure-Requests': '1'}
        self.proxys = {}
        self.urls ={
            'xici':'http://www.xicidaili.com/wt/',\
            'kuai':'https://www.kuaidaili.com/free/inha/',\
            'ip66':'http://www.66ip.cn/'\
        }

    def get_page(self,url):
        time.sleep(3)  # 防止网站反爬虫
        try:
            r = requests.get(url, headers=self.headers)
            return BeautifulSoup(r.text, 'html.parser')
        except Exception as e:
            print(e)

    def get_parser(self,key):
        parser_name = key + '_parser'
        self.parser = getattr(self, parser_name)

    def kuai_parser(self,soup):
        tds = soup.find_all('td')
        ips = [td.contents[0] for td in tds if td['data-title'] == 'IP']
        ports = [td.contents[0] for td in tds if td['data-title'] == 'PORT']
        self.proxys.update(dict(zip(ips, ports)))
        print (ips,ports)

    def xici_parser(self,soup):
        odds = soup.find_all('tr', class_='odd')
        for odd in odds:
            td = odd.find_all('td')
            ip = td[1].text # 去掉<td>121.205.17.101</td> 外面的外壳
            port = td[2].text
            self.proxys.update({ip:port})
            print(ip, port)

    def ip66_parser(self,soup):
        table = soup.find_all('table')[2]
        trs = table.find_all('tr')
        for tr in trs:
            td = tr.find_all('td')
            ip = td[0].text # 去掉<td>121.205.17.101</td> 外面的外壳
            port = td[1].text
            if not ip =='ip':
                self.proxys.update({ip:port})
                print(ip, port)

    def do_it(self):
        for key in self.urls:
            for i in range(1,1+self.page_num):
                url = self.urls[key]+str(i)
                print (url)
                try:
                    soup = self.get_page(url)
                    self.get_parser(key)
                    self.parser(soup)
                except Exception as e:
                    print(e)

        #运行所有包含parser的方法
        print ('Total:',len(self.proxys))
        return self.proxys


class API():
    '''提供API接口,暂时只提供get_all这一个功能'''
    def get_all(self):
        return raw_proxys

def main(page):
    start = time.time()
    sem = asyncio.Semaphore(maxSem)  # 最大同步数量
    # 1. load from db
    proxy_loader()
    #2. collect from source
    collector = ProxyCollector(page)
    raw_proxys.update(collector.do_it())
    #3. verify proxy
    for ip,port in raw_proxys.items():
        tasks.append(proxy_verifier(ip,port,sem))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    # 4. save the update
    proxy_saver()
    print ('Total time: ',time.time()-start)

def new():
    main(5)

def maintain():
    main(2)

if __name__ == '__main__':
    new()