#!/usr/bin/env python3
# coding=utf-8

import logging.handlers
import os
import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

log_filename = "log/output.log"
logger = logging.getLogger("logger")
handler1 = logging.StreamHandler()
handler2 = logging.FileHandler(filename=log_filename, mode='w')

logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
handler1.setFormatter(formatter)
handler2.setFormatter(formatter)

logger.addHandler(handler1)
logger.addHandler(handler2)

filename = "output/output.out"
tmpFilename = "output/output.tmp.out"

host = "https://www.mxj.com.cn"


def checkFile(filename):
    if os.path.isfile(filename):
        os.remove(filename)


def getDriver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def is_not_empty(element):
    return element != ""


def handleOutput(filename, tmpFilename, url):
    with open(tmpFilename, "r+", encoding="GBK") as fout:
        lines = fout.readlines()
        stripLines = list(map(lambda x: x.strip(), lines))
        outputLines = list(filter(is_not_empty, stripLines))
        logger.info(outputLines)

    with open(filename, "a+")as fout:
        for line in outputLines:
            fout.write(line + "\n")
        fout.write(url + "\n")
        fout.write("==============================" + "\n")


def main():
    checkFile(filename)
    classUrl = "https://www.mxj.com.cn/brands/cyqita/"
    for brandUrl in getBrandUrls(classUrl):
        handleBrand(brandUrl)
    nextPage = getPageUrl(classUrl)
    while nextPage is not None:
        for brandUrl in getBrandUrls(str(nextPage)):
            handleBrand(brandUrl)
        nextPage = getPageUrl(nextPage)


def getPageUrl(classUrl):
    driver = getDriver()
    driver.get(classUrl)
    bsObj = BeautifulSoup(driver.page_source, "lxml")
    page = bsObj.find("div", {"class": "comment-page pages"})
    if page.find("a", text="下一页") is None:
        return
    nextPage = host + page.find("a", text="下一页")["href"]
    logger.info("Next Page URL: " + nextPage)
    driver.close()
    return nextPage


def getBrandUrls(pageUrl):
    driver = getDriver()
    driver.get(pageUrl)
    bsObj = BeautifulSoup(driver.page_source, "lxml")
    brandUrls = []
    for element in bsObj.findAll("div", {"class": "pro-img"}):
        brandUrl = element.find("a", {"href": re.compile(".*")})["href"]
        logger.info("Brand URL: " + brandUrl)
        brandUrls.append(brandUrl)
    driver.close()
    return brandUrls


def handleBrand(brandUrl):
    logger.info("Handle URL: " + brandUrl)
    driver = getDriver()
    driver.get(brandUrl)
    bsObj = BeautifulSoup(driver.page_source, "lxml")
    checkFile(tmpFilename)
    with open(tmpFilename, "a+", encoding="GBK") as fout:
        hObj = bsObj.find("h1")
        if hObj is None:
            hObj = bsObj.find("h3")
        logger.info(hObj.getText().strip())
        fout.write(hObj.getText().strip() + "\n")

        iObj = bsObj.find("div", {"class": "bik-li"})
        if iObj is None:
            iObj = bsObj.find("div", {"class": "info"})
        logger.info(iObj.getText().strip())
        fout.write(iObj.getText().strip() + "\n")

        no_yh = bsObj.find("p", {"class": "no-yh"})
        if no_yh is not None:
            logger.info(no_yh.getText().strip())
            fout.write(no_yh.getText().strip() + "\n")

        bik_list = bsObj.find("div", {"class": "bik-list"})
        if bik_list is not None:
            logger.info(bik_list.getText().strip())
            fout.write(bik_list.getText().strip() + "\n")

    handleOutput(filename, tmpFilename, brandUrl)
    driver.close()


if __name__ == '__main__':
    main()
