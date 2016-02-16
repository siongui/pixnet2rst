#!/usr/bin/env python
# -*- coding:utf-8 -*-

from allPostsUrls import getAllPostsUrl
from html2rst import allHTMLPosts2rst

if __name__ == '__main__':
    pixnet_name = "nanomi"

    getAllPostsUrl(pixnet_name)
    allHTMLPosts2rst(pixnet_name)
