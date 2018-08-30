import requests
from  bs4 import BeautifulSoup
from tqdm import tqdm
import time
import os
import random
import json
import re

ID=''
DIR=ID#微博id
url='https://weibo.cn/'+ID
imgBox=[]#图片链接
fileName=[]#文件名
name={}#标题与链接对应的字典

headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}
#需要自己登陆账号获取cookie,对应填入即可
cookies={'Cookie':'_T_WM= ;'
                  'M_WEIBOCN_PARAMS= ;'
                  'MLOGIN=1;'
                  'SCF= ;'
                  'SSOLoginState= ;'
                  'SUB= ;'
                  'SUHB= '}
def getHTMLText(url):
    global code
    try:
        r=requests.get(url,timeout=30,headers=headers,cookies=cookies)
        r.encoding='utf-8'
        code=r.status_code
        return r.content
    except:
        return 'error'
def getMaxPage(url):
    global pageNum
    html = getHTMLText(url + '/profile?hasori=1&haspic=1&advancedfilter=1')
    soup = BeautifulSoup(html, 'html.parser')
    page = soup.find_all('div', attrs={'id': 'pagelist'})
    for i in page:
        pageNum=(re.findall(r'[0-9]+', i.text)[1])
    return int(pageNum)

def getPhotoBox(url):
    html = getHTMLText(url)
    soup = BeautifulSoup(html, 'html.parser')
    img = soup.find_all('div',attrs={'class':"c"})
    for i in img:
        if str(i.get('id')).replace('M_','') == 'None':
            continue
        imgList='https://weibo.cn/mblog/picAll/'+str(i.get('id')).replace('M_','')+'?rl=0'
        fileName.append(i.text[:20])
        if imgList in imgBox:
            continue
        else:
            imgBox.append(imgList)

def namePic():#链接与标题对应
    for i in range(len(fileName)):
        name[fileName[i]]=imgBox[i]

def downloadPic(url):
    global downloadLink
    downloadLink = []  # 原图下载链接
    html = getHTMLText(url)
    soup = BeautifulSoup(html, 'html.parser')
    original=soup.find_all('a')
    for i in original:
        if str(i.text)== '原图':
            img='https://weibo.cn'+str(i.get('href'))
            downloadLink.append(img)
    return downloadLink

def download(section):
    global name2
    count=0
    name2=section.copy()
    for i in section.keys():
        global picName
        picName=i
        downloadPic(section[i])
        if count !=0:
            if count %20 ==0:
                time.sleep(60*random.random())

        for k in tqdm(range(len(downloadLink))):
            image=getHTMLText(downloadLink[k])
            if code!=200:
                saveLog(name2)
                print('\nThe IP is dead,hold process\n')
                time.sleep(600)
                downloadContinue()
                exit()
            filename=(str(picName)+str(k)+'.jpg').replace('/',' ')
            try:
                with open(os.path.join(DIR, filename),'wb') as fd:
                    fd.write(image)
            except:
                print('error')

        name2.pop(i)
        count+=1

def saveLog(log):
    jsonLog=json.dumps(log)
    with open(os.path.join(DIR,'weiboLog.json'),'w') as fd:
        fd.write(jsonLog)

def downloadContinue():
    with open(os.path.join(DIR,'weiboLog.json'), 'r',encoding='utf-8') as fd:
        log=json.loads(fd.read())
    section_remain=log
    download(section_remain)



if __name__ == '__main__':
    if not os.path.exists(DIR):
        os.makedirs(DIR)
    for num in range(1,getMaxPage(url)+1):#默认最大页数
        getPhotoBox(url+'/profile?hasori=1&haspic=1&advancedfilter=1&page='+str(num))
        print('Ready to get page%d'%num)
        time.sleep(6)
    namePic()
    print(name)
    download(name)

