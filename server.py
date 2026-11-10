#!/usr/bin/env python3
"""Run: pip install requests beautifulsoup4 ; python server.py"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urljoin
from datetime import datetime
import json, re, time
import requests
from bs4 import BeautifulSoup
BASE='https://www.eventernote.com/users/htmlkarin/events'
CACHE=None; LAST=0
ROOT=Path(__file__).resolve().parent

def fetch_events():
    global CACHE,LAST
    if CACHE is not None and time.time()-LAST<300:return CACHE
    found={}
    sess=requests.Session();sess.headers['User-Agent']='Mozilla/5.0 (compatible; PersonalEventViewer/1.0)'
    for page in range(1,10):
        url=BASE if page==1 else BASE+'?page='+str(page)
        response=sess.get(url,timeout=12);response.raise_for_status()
        soup=BeautifulSoup(response.text,'html.parser')
        # Each event has a date followed by a linked event title. Extract using a text-order walk.
        body=soup.select_one('main') or soup.select_one('#main') or soup.body or soup
        date=None;added=0
        for node in body.find_all(string=True):
            raw=' '.join(str(node).split())
            m=re.search(r'(?<!\d)(20\d\d-\d\d-\d\d)(?!\d)',raw)
            if m:date=m.group(1)
            if not date:continue
            parent=node.parent
            if not parent or parent.name not in ('a','h3','h4'):continue
            a=parent if parent.name=='a' else parent.find('a')
            if not a or not a.get('href'):continue
            href=urljoin(BASE,a['href'])
            if not re.search(r'/events/\d+',href):continue
            title=a.get_text(' ',strip=True)
            if not title:continue
            # Nearby content often contains the venue and showtime.
            container=a.find_parent(['li','article']) or a.find_parent('div') or a.parent
            raw_block=container.get_text(' ',strip=True) if container else ''
            time_match=re.search(r'(?:開演|시작)\s*(\d{1,2}:\d{2})',raw_block)
            venue=''
            if container:
                venue_anchor=next((x for x in container.find_all('a') if '/places/' in x.get('href','')),None)
                if venue_anchor:venue=venue_anchor.get_text(' ',strip=True)
            found[href]={'date':date,'title':title,'venue':venue,'time':time_match.group(1) if time_match else '', 'url':href}
            added+=1
        if added==0:break
    if not found:raise RuntimeError('Eventernote page layout changed or access blocked')
    CACHE=list(found.values());LAST=time.time();return CACHE

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
    def do_GET(self):
        if self.path.split('?')[0]=='/api/events':
            try:
                result={'events':fetch_events()};data=json.dumps(result,ensure_ascii=False).encode()
                self.send_response(200)
            except Exception as e:
                data=json.dumps({'error':str(e)},ensure_ascii=False).encode();self.send_response(502)
            self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
        else:super().do_GET()

if __name__=='__main__':
    print('Open http://localhost:8765/my_oneui_contacts_website.html')
    ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
