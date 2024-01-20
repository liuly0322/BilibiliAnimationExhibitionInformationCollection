import requests
import os
import threading
import urllib
import pandas as pd  # 用于数据输出
from jsonsearch import JsonSearch

areas = [
    {"name": "上海", "code": 310100},
    {"name": "杭州", "code": 330100},
    {"name": "苏州", "code": 320500},
    {"name": "北京", "code": 110100},
    {"name": "丽水", "code": 331100},
    {"name": "广州", "code": 440100},
    {"name": "合肥", "code": 340100},
    {"name": "南宁", "code": 450100}
] # 想搜其他城市的话，去浏览器页面找到对应的 code，填过来

typeLists = ['展览', '演出', '本地生活', '全部类型']
pageNum = 4 # 默认搜集 4 页，可以自己灵活调整

resultFolder = '漫展信息/'


def DF2Excel(data_path, data_list, sheet_name_list):
    if (os.path.exists(data_path)):
        os.remove(data_path)
    write = pd.ExcelWriter(data_path)
    for da, sh_name in zip(data_list, sheet_name_list):
        da.to_excel(write, sheet_name=sh_name, header=None)
    write._save()


def getAllInfo():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 SLBrowser/8.0.0.9231 SLBChan/105',
        'Cookie': 'HMACCOUNT_BFESS=46935071688D78C1; BDUSS_BFESS=l1SU5nNXJhem5NUUtuUGF3M0tUZFh5V356bE43d3lCc2FQT3dKYThTU1VRMVpqRVFBQUFBJCQAAAAAAAAAAAEAAAACCeP-tv60ztSq1q7N6NfTAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJS2LmOUti5jSW; BAIDUID_BFESS=ADBC15F9539AC3DC4E2B4357892C6338:FG=1; ZFY=0tSY2YREU0sWPj7omdNG8nhw:AMIBJMcSjpUUKTA0:BvE:C; H_PS_PSSID='
    }
    if not os.path.isdir(resultFolder):  # 判断是否为目录
        os.mkdir(resultFolder)  # 创建一级目录

    for area in areas:
        totalResultList = []
        collectEachAreaInfo(area, headers, totalResultList)
        DF2Excel(resultFolder + area.get("name") + "-漫展信息.xlsx", totalResultList, typeLists)


def collectEachAreaInfo(area, headers, totalResultList):
    print("开始搜集：" + area.get("name"))
    for type in typeLists:
        resultList = []
        for page in range(1, pageNum):
            url = ("https://show.bilibili.com/api/ticket/project/listV2?version=134&page={}&pagesize=16&area={}&filter=&platform=web&p_type={}").format(
                page, area.get("code"), urllib.parse.quote(type))
            pageContent = requests.get(url=url, headers=headers).content.decode('utf-8')
            activities = JsonSearch(object=pageContent, mode='s').search_first_value(key='result')
            if len(activities) == 0:
                break
            collectEachPage(headers, activities, resultList)
        resultList.sort()
        columnHeader = ['开始时间', '名称', '地点', '具体时间范围', '想去人数', '最低票价', '是否有舞台（字符串匹配）',
                        'Link', 'Cover']
        resultList.insert(0, columnHeader)
        totalResultList.append(pd.DataFrame(resultList))
        print(" - " + type + ": 共 " + str(len(resultList) - 1) + " 条数据")


def collectEachPage(headers, activities, resultList):
    for activity in activities:
        project_name = activity['project_name']
        price_low = activity['price_low']
        price_high = activity['price_high']
        startTime = activity['start_time']
        id = str(activity['id'])
        activityUrl = "https://show.bilibili.com/platform/detail.html?id=" + id

        url = (("https://show.bilibili.com/api/ticket/project/getV2?version=134&id={}&project_id={}&requestSource=pc-new").format(
            id, id))
        details = requests.get(url=url, headers=headers).content.decode('utf-8')
        hasDancing = details.__contains__("舞")
        jsondata = JsonSearch(object=details, mode='s')
        wantToCount = JsonSearch(object=jsondata.search_first_value(key='wish_info'),
                                 mode='j').search_first_value(key='count')
        timeRange = jsondata.search_first_value('project_label')
        venue_info = JsonSearch(jsondata.search_first_value('venue_info'), mode='j').search_first_value('name')
        addressDetail = jsondata.search_first_value('address_detail')  + ' ' + venue_info
        sale_flag = JsonSearch(jsondata.search_first_value('sale_flag'), mode='j').search_first_value('display_name')
        cover_url = jsondata.search_first_value('cover')

        list = [startTime, project_name, addressDetail, timeRange, wantToCount,
                (price_low if price_low != "" else sale_flag), hasDancing, activityUrl, cover_url]
        resultList.append(list)

if __name__ == '__main__':
    getAllInfo()
