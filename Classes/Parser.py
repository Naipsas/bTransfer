#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Naipsas - Btc Sources
# bTransfer
# Started on Jan 2019

from html.parser import HTMLParser

# Docs: https://docs.python.org/2.7/library/htmlparser.html?highlight=htmlparser
# Ref: https://stackoverflow.com/questions/6883049/regex-to-extract-urls-from-href-attribute-in-html-with-python
class Parser(HTMLParser):

    def __init__(self, output_list=None):
        HTMLParser.__init__(self)

        self.check = False
        self.result = ""

    def printAll(self):
        for item in self.items:
            item.printAll()

    def handle_starttag(self, tag, attrs):
        if (tag == 'b'):
            self.check = True

    def handle_endtag(self, tag):
        if ((tag == 'b') and (self.check == True)):
            self.check = False

    def handle_data(self, data):
        if self.check == True:
            if "Tu IP real es" in data:
                lines = data.split("<br>")
                for line in lines:
                    if "Tu IP real es" in line:
                        item = line.split(" ")
                        self.result = item[-1]
            else:
                pass