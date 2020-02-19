from get_index import BaiduIndex
import openpyxl

from config import KEYWORDS, START_DATE, END_DATE

def createSheet(table):
    sheet = table.active
    sheet.title = 'Baidu Index'
    sheet_head = ['关键词', '数据源', '日期', '地区', '指数']
    # the head of the sheet
    sheet.append(sheet_head)
    return sheet

if __name__ == "__main__":
    table = openpyxl.Workbook()
    sheet = createSheet(table)

    baidu_index = BaiduIndex(KEYWORDS, START_DATE, END_DATE)

    for index_data in baidu_index.get_index():
        data = [index_data['keyword'], index_data['type'],
                index_data['date'], index_data['area'], index_data['index']]
        sheet.append(data)
    table.save('baiduIndex.xlsx')
