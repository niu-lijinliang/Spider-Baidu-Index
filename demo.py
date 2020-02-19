from get_index import BaiduIndex
import openpyxl

from config import KEYWORDS, START_DATE, END_DATE


if __name__ == "__main__":
    table = openpyxl.Workbook()
    sheet = table.active
    sheet.title = 'Baidu Index'
    sheet['A1'] = '关键词'
    sheet['B1'] = '数据源'
    sheet['C1'] = '日期'
    sheet['D1'] = '地区'
    sheet['E1'] = '指数'

    baidu_index = BaiduIndex(KEYWORDS, START_DATE, END_DATE)

    for index_data in baidu_index.get_index():
        data = [index_data['keyword'], index_data['type'],
                index_data['date'], index_data['area'], index_data['index']]
        sheet.append(data)
    table.save('baiduIndex.xlsx')
