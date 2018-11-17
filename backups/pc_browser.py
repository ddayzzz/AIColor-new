
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from pyvirtualdisplay import Display
import requests
import time


_display = None
_driver = None


def start_pc_browser():
    time.sleep(10)

    global _display, _driver
    _display = Display(visible=0, size=(800, 600))
    _display.start()
    _driver = webdriver.Firefox()
    _driver.get('http://localhost:8000/')

def upload_file(filename):

    upload = _driver.find_element_by_id('load_line_file')
    upload.send_keys(filename)  # send_keys
    # upload.send_keys('/home/shu/桌面/壁纸/psb (4).jpeg')
    upload.get_attribute('value')  # check value


def colorize():
    colo_btn = _driver.find_element_by_id('submit')
    colo_btn.click()

def read_result():
    ret = None
    # 超时时间 20s
    # output_img_url = driver.find_element_by_id('output').get_attribute('src')
    # print(output_img_url)
    try:
        element = WebDriverWait(driver=_driver, timeout=20).until(
            EC.invisibility_of_element_located((By.ID, 'painting_status'))
        )
    except TimeoutException as e:
        print('Timeout')
    finally:
        output_img_url = _driver.find_element_by_id('output').get_attribute('src')
        ret = output_img_url
    return ret


def close_browser():
    _driver.quit()
    _display.stop()