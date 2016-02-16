#!/usr/bin/env python
# -*- coding:utf-8 -*-

# http://www.crummy.com/software/BeautifulSoup/bs4/doc/
from bs4 import BeautifulSoup
from bs4 import Tag
import json
from datetime import datetime
import os
from allPostsUrls import fetchHTML, mkdirp


def writeContentToFile(content, fo):
    for child in content.children:
        if isinstance(child, Tag):
            if child.name == "br":
                fo.write("\n")
            else:
                writeContentToFile(child, fo)
        else:
            # http://stackoverflow.com/questions/11755208/how-to-remove-m-from-a-text-file-and-replace-it-with-the-next-line
            line = child.strip()
            if len(line) > 0:
                fo.write("  " + line.encode("utf-8") + "\n")


def saveAsRst(dt, title, category, content, oriUrl, rstpath):
    with open(rstpath, 'w') as fo:
        fo.write(title.encode("utf-8"))
        fo.write("\n")
        # https://www.google.com/search?q=python+unicode+length+in+bytes
        # http://stackoverflow.com/questions/6714826/how-can-i-determine-the-byte-length-of-a-utf-8-encoded-string-in-python
        for i in range(len(title.encode("utf-8"))):
            fo.write("#")
        fo.write("\n\n")
        fo.write(":date: " + dt.isoformat()[:-3] + "+08:00\n")
        fo.write(":tags: \n")
        fo.write(":category: " + category.encode("utf-8") + "\n")
        fo.write(":summary: \n\n\n")
        fo.write(":: \n\n")
        writeContentToFile(content, fo)

        fo.write("\n\n`Original Post on Pixnet <%s>`_" % oriUrl)


def parsePost(path):
    with open(path, 'r') as f:
        soup = BeautifulSoup(f)
        article = soup.find(id="article-box")
        #print(article.prettify())

        # parse datetime
        # http://stackoverflow.com/questions/5041008/handling-class-attribute-in-beautifulsoup
        month = article.find("span", class_="month").string.strip()
        day = article.find("span", class_="date").string.strip()
        year = article.find("span", class_="year").string.strip()
        hm = article.find("span", class_="time").string.strip()
        # https://www.google.com/search?q=python+datetime+from+string
        # https://www.google.com/search?q=python+datetime+from+string+with+timezone
        # http://stackoverflow.com/questions/466345/converting-string-into-datetime
        # https://en.wikipedia.org/wiki/List_of_time_zone_abbreviations
        tstr = month + " " + day + " " + year + " " + hm
        #print(tstr)
        # http://stackoverflow.com/questions/13182075/how-to-convert-a-timezone-aware-string-to-datetime-in-python-without-dateutil
        dt = datetime.strptime(tstr, "%b %d %Y %H:%M")
        #print(dt.isoformat())

        # parse title
        title = article.find("li", class_="title").find("a").string.strip()
        #print(title)

        # parse category
        link = soup.find("ul", class_="refer").find_all("li")[1].find("a")
        if link.get("rel"):
            category = ""
        else:
            category = link.string.strip()
        #print(category)

        # parse content
        content = soup.find("div", class_="article-content-inner")
        #print(content)

        return dt, title, category, content


def allHTMLPosts2rst(username):
    # retrieve urls of all posts in json
    jsonPath = os.path.join(username, "urls.json")
    with open(jsonPath, "r") as f:
        urls = json.load(f)

    postsDir = os.path.join(username, "posts")
    mkdirp(postsDir)

    for url in urls:
        localPath = os.path.join(postsDir, os.path.basename(url)) + ".html"
        fetchHTML(url, localPath)

        dt, title, category, content = parsePost(localPath)
        dstDir = "../content/articles/%d/%02d/%02d/" % (dt.year, dt.month, dt.day)
        mkdirp(dstDir)
        dstPath = os.path.join(dstDir, os.path.basename(url)) + "%zh.rst"
        print("writing " + dstPath + " ...")
        saveAsRst(dt, title, category, content, url, dstPath)
