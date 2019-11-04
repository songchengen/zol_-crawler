# -*- coding: UTF-8 -*-
import xlwt
from urllib import request
from bs4 import BeautifulSoup, NavigableString
import re
import time

domain = 'http://detail.zol.com.cn/'

basic_url =  domain + 'cell_phone_advSearch/subcate57_1_s8237-s528_9_1__'

# page_number = 1
# max_page_number = 0

# 爬取的参数，目前不需要爬取详情页面即可满足
columns = [
  u'名称', u'4G网络',u'CPU型号', u'CPU频率', u'出厂系统', u'主屏尺寸', u'电池容量', u'RAM容量', u'ROM容量', u'价格'
]
data = []

# 加载页面
def load_page(url):
  print('当前处理url：' + url)
  res = request.urlopen(url)
  code = res.getcode();
  if code != 200:
    return True
  return parse_basic_content(res.read().decode('GBK'))

# 处理手机列表页面
def parse_basic_content(content):
  soup = BeautifulSoup(content, 'html.parser')
  
  next_page_p = soup.find('p',class_='page_order')
  next_page_btn = next_page_p.find('a', title='下一页')
  
  content = soup.find('ul', class_='result_list')
  if content == None:
    return False

  for result in content.children:
    if isinstance(result, NavigableString):
      continue

    detail = {}
    detail[u'名称'] = result.find('a', id=re.compile('^proName_')).text;
    print(detail[u'名称'])
    #
    detail[u'价格'] = result.find('span', class_='price').text
    for d in result.find('div', class_='clearfix').find_all('li'):
      # 根据页面结构，只有有title属性的li才是我们想要的参数
      if d.get('title', default=None) == None or isinstance(d, NavigableString):
        continue

      # 清除超链接如更多参数超链接
      if d.find('a'):
        d.find('a').clear()
      
      [label, value] = d.text.split('：', 1)
      
      if label not in columns:
        continue
      
      detail[label] = value
    data.append(detail)
    # print(result.find('a', id=re.compile('^proName_')).text)

  # 如果没有下一页按钮说明为最后一页，则不在递归
  if next_page_btn == None:
    return False
  return True

#  将数据写入新文件
def data_write(file_path, datas):
    f = xlwt.Workbook(encoding='utf8')
    sheet1 = f.add_sheet(u'手机参数表', cell_overwrite_ok=True)  # 创建sheet
    
    # 写表头
    for i in range(0, len(columns)):
      sheet1.write(0, i, columns[i])
    row_index = 1

    # 写数据
    for data in datas:
        for j in range(len(columns)):
            sheet1.write(row_index,j, data.get(columns[j], None))
        row_index += 1
        
    f.save(file_path) #保存文件

# 处理详情页面
def parse_info_content(content):
  pass

def endpointer(page_number):
  url = basic_url + str(page_number) + '.html#showc'
  label = load_page(url)
  # 最多拉取140页数据，按照实际需要修改
  if label and page_number < 140: 
    endpointer(page_number + 1)
  
endpointer(1)

data_write(str(time.time()) + '.xls', data)