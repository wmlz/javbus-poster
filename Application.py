import re
import urllib.request
import os
import urllib.error
import threading
import configparser


# ------ 获取网页源代码的方法 ---
def getHtml(url):
    req = urllib.request.Request(url)
    req.add_header('User-Agent',
                   'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25')
    page = urllib.request.urlopen(req)
    html = page.read()
    return html


# ------ 获取帖子内所有图片地址的方法 ------
def getImg(html):
    reg = r'src="([.*\S].*cover.*\.jpg)"'
    imgre = re.compile(reg);
    imglist = re.findall(imgre, html)
    return imglist


# ------ 获取path下所有视频文件的文件名
def getCode(path):
    codes = []
    for dirpath, dirs, files in os.walk(path):
        print(files)
        for filename in files:
            if os.path.splitext(filename)[1] in suffixs:
                codes.append(os.path.splitext(filename)[0])
        # for dir in dirs:
        #     codes.append(dir)
    print('共扫描到以下' + str(len(codes)) + '个番号：')
    print(codes)
    return codes


# ------- 根据番号code下载封面
def download(code):
    html = None
    try:
        html = getHtml(javurl + '/' + code)
    except urllib.error.HTTPError as reason:
        print(str(code) + ' 不存在')

    if html is not None:
        html = html.decode('UTF-8')
        imgList = getImg(html)
        for imgPath in imgList:
            try:
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-agent',
                                      'Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10')]
                urllib.request.install_opener(opener)
                urllib.request.urlretrieve(imgPath, destdir + '/' + code + '.jpg')
                print(code + '.jpg 下载成功')
            except urllib.error.HTTPError as reason:
                print(code + '找不到')


class myThread(threading.Thread):
    def __init__(self, threadID, name, codelist, threadAmount):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.codelist = codelist
        self.threadAmount = threadAmount

    def run(self):
        for i in range(len(self.codelist)):
            if i % self.threadAmount == self.threadID:
                download(self.codelist[i])


if __name__ == '__main__':
    cp = configparser.ConfigParser()
    cp.read('./config.cfg', 'utf8')
    cfgitems = cp.items('default')
    print('配置如下：')
    for item in cfgitems:
        print(item[0] + ': ' + item[1])

    srcdir = cp.get('default', 'srcdir')
    destdir = cp.get('default', 'destdir')
    threadnum = cp.getint('default', 'threadnum')
    javurl = cp.get('default', 'javbus')
    suffix = cp.get('default', 'suffix').split(',')
    suffixs = []
    for i in suffix:
        suffixs.append('.' + i)

    codes = getCode(srcdir)
    for i in range(threadnum):
        myThread(i, "Thread-" + str(i), codes, threadnum).start()
