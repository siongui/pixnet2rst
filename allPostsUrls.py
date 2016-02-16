#!/usr/bin/env python
# -*- coding:utf-8 -*-

# http://www.crummy.com/software/BeautifulSoup/bs4/doc/
from bs4 import BeautifulSoup
import json
import urllib2
import os


def mkdirp(dirpath):
    # https://www.google.com/search?q=python+mkdir+p
    # http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)


def parseListallHTML(path):
    urls = []
    with open(path, 'r') as f:
        soup = BeautifulSoup(f)
        div_id_content = soup.find(id="content")
        table = div_id_content.find("table")
        for link in table.find_all("a"):
            url = link.get("href")
            #print(url)
            urls.append(url)

    return urls


def fetchHTML(url, outpath):
    if not os.path.exists(outpath):
        print("fetching %s ..." % url)
        response = urllib2.urlopen(url)
        with open(outpath, "w") as f:
            f.write(response.read())


def getListallsHTML(username):
    baseurl = "http://%s.pixnet.net/blog/listall/1" % username
    #print(baseurl)

    listallDir = os.path.join(username, "listall")
    mkdirp(listallDir)

    localPath = os.path.join(listallDir, os.path.basename(baseurl)) + ".html"
    #print(localPath)

    fetchHTML(baseurl, localPath)
    # parse HTML to see if there are any listall page
    with open(localPath, "r") as f:
        soup = BeautifulSoup(f)
        listalls = soup.find("div", class_="page").find_all("a")
        last = listalls[-2]
        lastPageNumber = int(last.string.strip())

        for i in range(lastPageNumber):
            targetUrl = "http://%s.pixnet.net/blog/listall/%d" % (username, i+1)
            #print(targetUrl)
            lp = os.path.join(listallDir, os.path.basename(targetUrl)) + ".html"
            fetchHTML(targetUrl, lp)


def getAllPostsUrl(username):
    getListallsHTML(username)

    listallDir = os.path.join(username, "listall")
    # https://www.google.com/search?q=python+list+all+files+in+directory
    urls = []
    for filename in os.listdir(listallDir):
        print("retrieving urls of post in %s ..." % filename)
        urls.extend( parseListallHTML( os.path.join(listallDir, filename) ) )

    print(urls)
    print("number of urls: %d" % len(urls))

    # save urls of all posts in json
    jsonPath = os.path.join(username, "urls.json")
    with open(jsonPath, 'w') as fo:
        fo.write(json.dumps(urls))
