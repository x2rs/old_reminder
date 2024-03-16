import copy
import json
import datetime
from colorama import Fore, Style
import plyer
import requests
import os

_data={}
time_intervals=[("","")]*15 # index starts with 1

start_date=datetime.date(2024,2,19) # Monday

for i in range(1,14,2):
    time_intervals[i]=(f"{i+7}:00",f"{i+7}:45")
    time_intervals[i+1]=(f"{i+7}:55",f"{i+8}:40")

with open("data.json",mode="r",encoding="utf-8") as f:
    _data=json.load(f)

class Item:
    name:str
    lesson:dict
    def __init__(self,name,lesson:dict={}) -> None:
        self.name=name
        self.lesson=lesson
    def reason(self):
        if self.lesson:
            return f"您在{Fore.YELLOW}{time_intervals[self.lesson['start_time']][0]}-{time_intervals[self.lesson['end_time']][1]}{Fore.RESET}有{Fore.CYAN}{self.lesson['name']}{Fore.RESET}，地点：{Fore.BLUE}{self.lesson['place']}{Fore.RESET}"
        return f"这是您每天要带的。"

def write_items(day:datetime.date,detailed=False):
    day_lessons=[] # 这一天要上的课
    items=[] # 这一天要带的物品
    # 先装上每天要带的
    for item in _data["global"]:
        items.append(Item(Fore.GREEN+item+Fore.RESET))

    week_id=(day-start_date).days//7+1; # 第几周，e.g. 2024-03-13: week_id == 4
    for lesson in _data["lessons"]:
        if lesson["day_of_week"] == (day.weekday()+1)%7 and week_id in lesson["week"]: #lesson["day_of_week"] Monday == 1; Sunday == 0
            # e.g. lesson["week"]==[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
            day_lessons.append(lesson)
            
            # print(lesson["name"], start, end)

            # 添加课本，要上色
            for item in _data["lesson_items"][lesson["name"]]:
                items.append(Item(Fore.MAGENTA+item+Fore.RESET,lesson))
    print(f"在{Fore.BLUE}{day}{Fore.RESET}您需要带{Fore.RED}{len(items)}{Fore.RESET}个物品：") # 日期
    
    for i in range(len(items)):
        if detailed:
            print(f"{i+1}.{items[i].name}，因为{items[i].reason()}")
        else:
            print(f"{i+1}.{items[i].name}")
    

def notify_items(day:datetime.date):
    day_lessons=[] # 这一天要上的课
    items=[] # 这一天要带的物品
    # 先装上每天要带的
    for item in _data["global"]:
        items.append(Item(item))

    week_id=(day-start_date).days//7+1; # 第几周，e.g. 2024-03-13: week_id == 4
    for lesson in _data["lessons"]:
        if lesson["day_of_week"] == (day.weekday()+1)%7 and week_id in lesson["week"]: #lesson["day_of_week"] Monday == 1; Sunday == 0
            # e.g. lesson["week"]==[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
            day_lessons.append(lesson)
            
            # print(lesson["name"], start, end)

            # 添加课本，要上色
            for item in _data["lesson_items"][lesson["name"]]:
                items.append(Item(item))
    
    return "，".join([item.name for item in items])

# write_items(datetime.date.today()) # 显示今天要带的东西

# write_items(datetime.date.today(),True) # 查看详情

# 提醒

# plyer.notification.notify(title=f"提醒{datetime.date.today()}",message=notify_items(datetime.date.today()),timeout=5)

# r^2bv

def request_weather() -> dict: # 天气信息的获取上限是每分钟300次，超过会禁用一小时，数据每8小时更新一次
    res = requests.get(url="http://t.weather.sojson.com/api/weather/city/101020200") #TODO 默认为闵行区
    res.encoding = "utf-8"
    weather_dict=res.json()
    print("!Requested")
    return weather_dict

def get_weather() -> dict: # 格式见weather_example.json
    if not os.path.exists("weather.json"):
        weather_dict = request_weather()
        if weather_dict["status"] == 200: # 如果字典的 status == 200，则请求成功；否则status会变为错误代码，如404
            with open("weather.json", mode="w",encoding="utf-8") as f:
                json.dump(weather_dict,f) # 保存
            return weather_dict
        else:
            # 此时没有任何天气数据
            return {}
    # 有缓存
    with open("weather.json",mode="r",encoding="utf-8") as f:
        weather_dict=json.load(f)
    date_str=weather_dict["date"]
    time=datetime.datetime.fromisoformat(date_str[0:4]+"-"+date_str[4:6]+"-"+date_str[6:8]+" "+weather_dict["cityInfo"]["updateTime"]) # 转换为datetime格式
    now=datetime.datetime.now()
    if now-time>datetime.timedelta(hours=8): # > 8 hours, 请求！
        new_weather_dict = request_weather()
        if new_weather_dict["status"] == 200: # 如果字典的 status == 200，则请求成功；否则status会变为错误代码，如404
            with open("weather.json", mode="w",encoding="utf-8") as f:
                json.dump(new_weather_dict,f) # 保存
            return new_weather_dict
    return weather_dict


weather_dict=get_weather()

print(weather_dict["cityInfo"]["updateTime"], "湿度", weather_dict["data"]["shidu"],"温度", weather_dict["data"]["wendu"])



# TODO 安卓端是否可以运行？
# 工具模块
import pyttsx4 #导入
#创建  初始化
engine = pyttsx4.init()
#说话
items=notify_items(datetime.date.today())
cnt=len(items.split("，"))
# engine.say(f"在{datetime.date.today()}您需要带{cnt}个物品："+notify_items(datetime.date.today()))
#运行
# engine.runAndWait()

# TODO 解决一下代码重复的问题