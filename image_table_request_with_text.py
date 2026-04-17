import time
from multiprocessing.dummy import Pool as ThreadPool
import multiprocessing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import os
from fake_useragent import UserAgent
import pandas as pd
from tqdm import tqdm
import random
import io
from selenium.webdriver.common.action_chains import ActionChains
import sys
import json 
import threading
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import signal
signal.signal(signal.SIGCLD, signal.SIG_IGN)

pixel_value = 2 if sys.platform == "darwin" else 1
print('Thread Number:', multiprocessing.cpu_count())
# Random User-Agent
ua = UserAgent()

def is_element_fully_in_viewport(driver, element):
    """判断元素是否完全在视口内"""
    return driver.execute_script("""
        let rect = arguments[0].getBoundingClientRect();
        return (
            rect.top >= 0 && 
            rect.left >= 0 && 
            rect.bottom <= window.innerHeight && 
            rect.right <= window.innerWidth
        );
    """, element)

def is_element_fully_in_viewpage(driver, absolute_positions):
    window_size = driver.execute_script("return {height: window.innerHeight, width: window.innerWidth};")
    if window_size['height'] >= absolute_positions['height']:
        return True
    else:
        return False

def get_element_absolute_position(driver, element):
    """ 获取元素相对于整个页面（scrollPage）的坐标 """
    rect = driver.execute_script("""
        let rect = arguments[0].getBoundingClientRect();
        return {
            'absolute_x': rect.x+window.scrollX,
            'absolute_y': rect.y+window.scrollY,
            'x':rect.x,
            'y':rect.y,
            'width': rect.width,
            'height': rect.height
        };
    """, element)
    return rect
def get_viewport_size(driver):
    """ 获取视口（viewport）的宽度和高度 """
    viewport_size = driver.execute_script("""
        return {
            'innerWidth': window.innerWidth,
            'innerHeight': window.innerHeight
        };
    """)
    return viewport_size

def table_expand(driver):
    try:
        # find mw-collapsible-toggle 
        toggle_buttons = driver.find_elements(By.CLASS_NAME, "mw-collapsible-toggle")

        # 过滤出既未展开（包含 mw-collapsible-toggle-collapsed）又在表格单元格（<td> 或 <th>）中的按钮
        collapsed_buttons = []
        for btn in toggle_buttons:
            if "mw-collapsible-toggle-collapsed" in btn.get_attribute("class"):
                try:
                    # 检查按钮是否在 <td> 或 <th> 内
                    parent_table_cell = btn.find_element(By.XPATH, "./ancestor::td | ./ancestor::th")
                    if parent_table_cell:
                        collapsed_buttons.append(btn)
                except:
                    pass  # 按钮不在表格单元格内，忽略它

        if not collapsed_buttons:
            print("所有表格均已展开或没有符合条件的折叠表格")

        for btn in collapsed_buttons:
            try:
                ActionChains(driver).move_to_element(btn).click(btn).perform()
                time.sleep(random.uniform(2, 3))
            except Exception as e:
                print(f"展开失败")

    except Exception as e:
        print("没有找到折叠表格，可能已经全部展开")
        





id2text ={}
lock = threading.Lock()

def thread_safe_write(key, value):
    with lock:
        id2text[key] = value

def thread_safe_read(key):
    with lock:
        return id2text.get(key)
def write_to_file(filename, data):
    with lock:
        with open(filename, 'w') as f:
            json.dump(data,f,indent =4,ensure_ascii=False)


def parse_tables(html_content):
    all_tables_data = []

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all table elements
    tables = soup.find_all('table')

    for table in tables:
        headers = []
        data = []

        # Check if <thead> exists
        thead = table.find('thead')
        if thead:
            # Parse headers from <thead>
            header_rows = thead.find_all('tr')
            for header_row in header_rows:
                headers.extend([th.get_text(strip=True) if th.get_text(strip=True) is not None else "" for th in header_row.find_all('th')])

            # Parse data from <tbody> or directly from <tr> if <tbody> is absent
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
            else:
                rows = table.find_all('tr')

            for row in rows:
                cells = row.find_all(['th', 'td'])
                if cells:
                    data.append([cell.get_text(strip=True) if cell.get_text(strip=True) is not None else "" for cell in cells])
        else:
            # Parse headers and data from <tr> when <thead> is absent
            rows = table.find_all('tr')
            for row in rows:
                header_eles = row.find_all('th')
                cell_eles = row.find_all('td')
                if header_eles and cell_eles:
                    headers.extend([th.get_text(strip=True) if th.get_text(strip=True) is not None else "" for th in header_eles])
                    data.append([td.get_text(strip=True) if td.get_text(strip=True) is not None else "" for td in cell_eles])
                elif cell_eles:
                    headers.append('')
                    data.append([td.get_text(strip=True) if td.get_text(strip=True) is not None else "" for td in cell_eles])
                else:
                    headers.extend([th.get_text(strip=True) if th.get_text(strip=True) is not None else "" for th in header_eles])
                    data.append([''])

        all_tables_data.append({'headers':headers,'rows':data})

    return all_tables_data

def parse_table_without_thead(table):
    total_headers = []
    total_data = []

    rows = table.find_elements(By.TAG_NAME, 'tr')
    for i, row in enumerate(rows):
        header_eles = row.find_elements(By.TAG_NAME, 'th')
        cell_eles = row.find_elements(By.TAG_NAME, 'td')
        if len(header_eles) > 0 and len(cell_eles)>0:
            headers = [header_ele.text.strip()if header_ele.text.strip() else '' for header_ele in header_eles]
            cells  = [cell_ele.text.strip() if cell_ele.text.strip() else '' for cell_ele in cell_eles]
        elif len(cell_eles):
            headers = ['']
            cells  = [cell_ele.text.strip() if cell_ele.text.strip() else '' for cell_ele in cell_eles]
        else:
            headers = ['']
            cells = [header_ele.text.strip() if header_ele.text.strip() else '' for header_ele in header_eles]
        total_headers.extend(headers)
        total_data.extend(cells)

    return total_headers,total_data

def parse_table_with_thead(table):
    headers = []
    data = []
    # Find headers
    thead = table.find_element(By.TAG_NAME, 'thead')
    header_rows = thead.find_elements(By.TAG_NAME, 'tr')
    for header_row in header_rows:
        headers.extend([th.text.strip() if th.text.strip() else '' for th in header_row.find_elements(By.TAG_NAME, 'th')])
    
    # Find rows
    tbody = table.find_element(By.TAG_NAME, 'tbody')
    if tbody:
        rows = tbody.find_elements(By.TAG_NAME, 'tr')
        # print('tbody process')
    else:
        rows = table.find_elements(By.TAG_NAME, 'tr')

    for row in rows:
        cells = row.find_elements(By.XPATH, './*[self::th or self::td]')
        if cells:
            data.append([cell.text.strip() if cell.text.strip() else '' for cell in cells])
    return headers, data


def extract_text(table):
    try:
        thead = table.find_element(By.TAG_NAME, 'thead')
        headers,datas = parse_table_with_thead(table)
    except:
        # print('process_here')
        headers,datas = parse_table_without_thead(table)

    return {'headers':headers,'rows':datas}


def capture_table_screenshot(url, table_id,save_dir,save_file_name):
    print(url)
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 
    chrome_options.add_argument("--disable-gpu")

    # driver = webdriver.Chrome(options=options)
    chrome_options.add_argument('--disable-http2') 
    chrome_options.add_argument('--disable-keep-alive')
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")  # 
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # 
    user_agent = ua.random  # Random User-Agent
    chrome_options.add_argument(f"user-agent={user_agent}")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    try:
        driver.get(url)
    except: 
        driver.quit()
        return 

    time.sleep(random.uniform(2, 4))  # 随机延迟时间
    # 找到所有表格
    table_expand(driver)

    WebDriverWait(driver, 8).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "table"))
        )
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(random.uniform(1, 3))


    html_content = driver.page_source
    
    text_tables = parse_tables(html_content)

    tables = driver.find_elements(By.TAG_NAME, "table")
    assert len(text_tables) == len(tables)
    
    
    for idx, table in enumerate(tables):
        table_text = text_tables[idx]
        # table_text = extract_text(table)
        table_text['url'] = url
        # print(table_text)
        thread_safe_write(f"{table_id}_{idx}", table_text)
        # 获取表格在视口中的大小和页面中的位置
        table_image_path = os.path.join(save_dir, f"{table_id}_{idx}.png")
        time.sleep(3)  # 等待滚动完成
        # scroll_y = driver.execute_script("return window.scrollY;")
        viewpage_size = get_viewport_size(driver)
        absolute_position = get_element_absolute_position(driver, table)
        table_top = absolute_position['absolute_y']
        table_bottom = absolute_position['absolute_y'] + absolute_position['height']
        
        try:
            if is_element_fully_in_viewpage(driver,absolute_position):
                driver.execute_script("window.scrollTo(0, arguments[0]);", table_top)
                time.sleep(random.uniform(1, 3))
                table.screenshot(table_image_path)

            else:
                screenshots = []  # 存储截图

                table_x = absolute_position['x']
                table_width = absolute_position['width']
                table_y = absolute_position['absolute_y']
                table_height = absolute_position['height']

                driver.execute_script("window.scrollTo(0, arguments[0]);", table_bottom-viewpage_size['innerHeight'])
                time.sleep(random.uniform(1, 3))
                screenshot = driver.get_screenshot_as_png()
                image = Image.open(io.BytesIO(screenshot))
                screenshots.append(image.crop((table_x * pixel_value, 0, (table_x + table_width) * pixel_value, image.height)))
                
                scrolls = int(table_height / viewpage_size['innerHeight'])-1
                if table_height > scrolls*viewpage_size['innerHeight']:
                    scrolls +=1
                scrolls -=1


                if scrolls >0:
                    for i in range(scrolls):
                        # 截图当前视图
                        driver.execute_script("window.scrollBy(0, arguments[0]);", -viewpage_size['innerHeight'])
                        time.sleep(random.uniform(1, 3)) # 等待滚动完成
                        screenshot = driver.get_screenshot_as_png()
                        image = Image.open(io.BytesIO(screenshot))
                        screenshots.append(image.crop((table_x * pixel_value, 0, (table_x + table_width) * pixel_value, image.height)))

                current_scrolly = driver.execute_script("return window.scrollY;")
                driver.execute_script("window.scrollBy(0, arguments[0]);", (table_top-current_scrolly))
                time.sleep(random.uniform(1, 3))  # 等待滚动完成
                y_position = driver.execute_script("return arguments[0].getBoundingClientRect().top;", table)
                
                ##截图 裁剪
                screenshot = driver.get_screenshot_as_png()
                image = Image.open(io.BytesIO(screenshot))
                screenshots.append(image.crop((table_x*pixel_value, 0, (table_x+table_width)*pixel_value, pixel_value*(current_scrolly-table_top))))
                screenshots.reverse()

                total_width = screenshots[0].width
                total_height = sum(img.height for img in screenshots)
                stitched_image = Image.new("RGB", (total_width, total_height))
                y_offset = 0
                for img in screenshots:
                    stitched_image.paste(img, (0, y_offset))
                    y_offset += img.height
                
                stitched_image.save(table_image_path)
        except Exception as e:
            print(e)
            continue
        if len(id2text)%200 ==0:
            text_save_path = os.path.join(save_dir, save_file_name)
            write_to_file(text_save_path,id2text)
    driver.quit()

def capture_table_screenshot_with_text(url,table_id,save_dir,save_file_name):
    try:
        capture_table_screenshot(url, table_id,save_dir,save_file_name)
    except Exception  as e:
        print(e)
        return None 

def cache_check(source_dir):
    stored_tables = [] 
    files =[item for item in os.listdir(source_dir) if '.json' in item]
    for json_file in files:
        with open(os.path.join(source_dir,json_file),mode='r') as jf:
            data = json.load(jf)
            table_ids = list(data.keys())
            filter_table_ids = ['_'.join(item.split('_')[:-1]) for item in table_ids]
            filter_table_ids = list(set(filter_table_ids))
            stored_tables.extend(filter_table_ids)
    print('cache stored',len(stored_tables))
    return stored_tables

if __name__ == '__main__':

    ## example 
    capture_table_screenshot_with_text(xx,xx,xx,xx)