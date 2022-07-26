#!/usr/bin/env python3

import argparse
import logging
import sys
import time
from typing import Generator, Iterable
import youtube_dl

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.expected_conditions import *
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager


def get_channel_name(url: str):
    return url.split("/")[-1]


def channel_scan(url: str) -> Generator:
    """Use selenium to scan whole channel videos section for urls"""

    driver.get(url)

    # Go to videos tab
    video_button: WebElement = wait.until(
        presence_of_element_located(
            (By.XPATH, '//tp-yt-paper-tab/div[text()[contains(., "Videos")]]')
        )
    )
    video_button.click()
    logging.debug("Clicking into 'Videos' tab...")
    driver.implicitly_wait(2)

    # scroll to bottom of page
    logging.info("Scanning for videos...")
    while True:
        scroll_height = 3000
        document_height_before = driver.execute_script(
            "return document.documentElement.scrollHeight"
        )
        driver.execute_script(
            f"window.scrollTo(0, {document_height_before + scroll_height});"
        )
        time.sleep(10)
        document_height_after = driver.execute_script(
            "return document.documentElement.scrollHeight"
        )
        if document_height_after == document_height_before:
            break

    # get list of video urls on the page
    elements: list[WebElement] = wait.until(
        presence_of_all_elements_located((By.XPATH, '//a[@id="video-title"]'))
    )
    logging.info(f"Num identified videos: {len(elements)}")

    main_dict = (
        {
            "title": element.get_attribute("title").replace(",", " "),
            "url": element.get_attribute("href"),
        }
        for element in elements
    )

    return main_dict


def print_data(data_structure: Iterable):
    """Print the collected datastructure of youtube metadata to the specified format to stdout"""

    logging.info("Outputting to stdout")
    pd.DataFrame(
        list(data_structure),
        columns=["title", "url"],
    ).to_csv(sys.stdout)


def main():

    # argument parsing handler
    parser = argparse.ArgumentParser(
        description="Inputting a channel url into the program, search that entire channel for videos and return a csv of title, description, and url for later download/storage"
    )

    # data scraping command 
    parser.add_argument(
        "channel_url",
        help="The URL of the channel that will be scraped",
        type=str,
    )

    # extra commands
    parser.add_argument(
        "-v", "--verbose", help="Print more info to console", default=False, type=bool
    )


    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    # scan for videos and output formatted data to stdout
    from selenium.webdriver.firefox.options import Options

    logging.debug("Downloading firefox geckodriver...")
    options = Options()
    options.headless = True
    global driver
    driver = webdriver.Firefox(
        service=FirefoxService(GeckoDriverManager().install()), options=options
    )
    global wait
    wait = WebDriverWait(driver, 15)
    print_data(channel_scan(args.channel_url))
    driver.close()

if __name__ == "__main__":
    main()
