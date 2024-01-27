import requests
import os
import urllib
import pandas as pd
from jsonsearch import JsonSearch
import traceback

areas = [
    {"name": "上海", "code": 310100},
    {"name": "杭州", "code": 330100},
    {"name": "苏州", "code": 320500},
    {"name": "北京", "code": 110100},
    {"name": "丽水", "code": 331100},
    {"name": "广州", "code": 440100},
    {"name": "合肥", "code": 340100},
    {"name": "南宁", "code": 450100},
    {"name": "江西", "code": 360000}
]  # 想搜其他城市的话，去浏览器页面找到对应的 code，填过来

typeLists = ["展览", "演出", "本地生活", "全部类型"]
pageNum = 4  # 默认搜集 4 页，可以自己灵活调整
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 SLBrowser/8.0.0.9231 SLBChan/105",
    "Cookie": "HMACCOUNT_BFESS=46935071688D78C1; BDUSS_BFESS=l1SU5nNXJhem5NUUtuUGF3M0tUZFh5V356bE43d3lCc2FQT3dKYThTU1VRMVpqRVFBQUFBJCQAAAAAAAAAAAEAAAACCeP-tv60ztSq1q7N6NfTAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJS2LmOUti5jSW; BAIDUID_BFESS=ADBC15F9539AC3DC4E2B4357892C6338:FG=1; ZFY=0tSY2YREU0sWPj7omdNG8nhw:AMIBJMcSjpUUKTA0:BvE:C; H_PS_PSSID=",
}

resultFolder = "漫展信息/"


def DF2Excel(data_path, data_list):
    if os.path.exists(data_path):
        os.remove(data_path)
    write = pd.ExcelWriter(data_path)
    for da, sh_name in zip(data_list, typeLists):
        da.to_excel(write, sheet_name=sh_name, header=None)
    write._save()


def getAllInfo():
    if not os.path.isdir(resultFolder):
        os.mkdir(resultFolder)

    for area in areas:
        try:
            areaResultList = collectEachArea(area)
            DF2Excel(resultFolder + area.get("name") + "-漫展信息.xlsx", areaResultList)
        except Exception:
            print(traceback.format_exc())


def collectEachArea(area):
    print("正在搜集 " + area.get("name") + " 的漫展信息...")
    return [collectEachType(area, type) for type in typeLists]


def collectEachType(area, type):
    resultList = []
    for page in range(1, pageNum):
        pageResult = collectEachPage(area, type, page)
        if len(pageResult) == 0:
            break
        resultList.extend(pageResult)
    resultList.sort()
    columnHeader = [
        "开始时间",
        "名称",
        "地点",
        "具体时间范围",
        "想去人数",
        "最低票价",
        "Link",
        "Cover",
    ]
    print(" - " + type + ": 共 " + str(len(resultList)) + " 条数据")
    return pd.DataFrame([columnHeader] + resultList)


def collectEachPage(area, type, page):
    url = (
        "https://show.bilibili.com/api/ticket/project/listV2?version=134&page={}&pagesize=16&area={}&filter=&platform=web&p_type={}"
    ).format(page, area.get("code"), urllib.parse.quote(type))
    source = requests.get(url=url, headers=headers).content.decode("utf-8")
    activities = JsonSearch(object=source, mode="s").search_first_value(key="result")
    return [getActivityInfo(activity) for activity in activities]


def getActivityInfo(activity):
    try:
        projectName = activity["project_name"]
        sale_flag_number = activity["sale_flag_number"]
        saleFlag = activity["sale_flag"]
        priceLow = activity["price_low"]/100
        startTime = activity["start_time"]
        id = str(activity["id"])
        activityUrl = f"https://show.bilibili.com/platform/detail.html?id={id}"

        url = f"https://show.bilibili.com/api/ticket/project/getV2?version=134&id={id}&project_id={id}&requestSource=pc-new"
        details = requests.get(url=url, headers=headers).content.decode("utf-8")
        details = JsonSearch(object=details, mode="s")
        wantToCount = details.search_first_value("wish_info")["count"]
        timeRange = details.search_first_value("project_label")
        venue_info = details.search_first_value("venue_info")["name"]
        addressDetail = details.search_first_value("address_detail") + " " + venue_info
        coverUrl = details.search_first_value("cover")
    except Exception:
        print(traceback.format_exc())

    return [
        startTime,
        projectName,
        addressDetail,
        timeRange,
        wantToCount,
        (priceLow if sale_flag_number < 3 else saleFlag),
        activityUrl,
        coverUrl,
    ]

if __name__ == "__main__":
    getAllInfo()
