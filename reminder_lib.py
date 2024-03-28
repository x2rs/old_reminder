import copy
import json
import datetime
from colorama import Fore, Style
import plyer
import requests
import os
import pyttsx4 # 语音播报模块

user_data={}
time_intervals=[("","")]*15 # index starts with 1

start_date=datetime.date(2024,2,19) # Monday

for i in range(1,14,2):
    time_intervals[i]=(f"{i+7}:00",f"{i+7}:45")
    time_intervals[i+1]=(f"{i+7}:55",f"{i+8}:40")

with open("data.json",mode="r",encoding="utf-8") as f:
    user_data=json.load(f)

#! 从kivy启动开始，不再使用控制台的Fore Style等颜色，所有输出格式均匹配kivy

def color(text,color:str):
    return f'[color={color}]{text}[/color]'

class Item:
    name:str
    color:str
    lesson:dict
    def __init__(self,name,color:str="",lesson:dict={}) -> None: # The color can be #000000
        self.name=name
        self.color=color
        self.lesson=lesson
    def to_kivy_text(self) -> str:
        if self.color:
            return color(self.name,self.color)
        return self.name
    def reason(self):
        if self.lesson:
            # TODO 重写reason，用color，设置一下默认色，让用户能修改颜色
            return f"您在"+\
                color(f"{time_intervals[self.lesson['start_time']][0]}-{time_intervals[self.lesson['end_time']][1]}","FFFF00")+\
                f"有{color(self.lesson['name'],'00FFFF')}，地点：{color(self.lesson['place'],'0000FF')}"
        return f"这是您每天要带的。"

def format_weather(weather:dict)->str:
    today=weather["data"]["forecast"][0] # TODO 如果我0点来看呢，怎么会事呢；应该是获取要带物品当天的天气！
    return f'{today["ymd"]} {today["high"]} {today["low"]} {today["type"]}'

class Inventory:
    items:list[Item]
    date:datetime.date
    weather:dict
    def __init__(self,items,date) -> None:
        
        self.items=copy.deepcopy(items)
        self.date=date
        self.weather=get_weather()

    def to_kivy_text(self,show_numbers=True,detailed=False):
        lines=[]
        # TODO 天气无论detailed都会输出
        lines.append(format_weather(self.weather))

        lines.append(f"在{color(self.date,'FFFF00')}您需要带{color(len(self.items),'FF0000')}个物品：") #TODO 两个默认色
        for i in range(len(self.items)):
            item=self.items[i]
            text=""
            if show_numbers:
                text+=f"{i+1}."
            text+=item.to_kivy_text()
            if detailed:
                text+="，因为"+item.reason()
            lines.append(text)
        return "\n".join(lines)


def get_inventory(day:datetime.date) -> Inventory:
    day_lessons=[] # 这一天要上的课
    items=[] # 这一天要带的物品

    # 优先考虑先装个伞
    

    # 先装上每天要带的
    for item in user_data["global"]:
        items.append(Item(item,"00FF00")) #TODO 每天要带的默认颜色

    week_id=(day-start_date).days//7+1; # 第几周，e.g. 2024-03-13: week_id == 4
    for lesson in user_data["lessons"]:
        if lesson["day_of_week"] == (day.weekday()+1)%7 and week_id in lesson["week"]: #lesson["day_of_week"] Monday == 1; Sunday == 0
            # e.g. lesson["week"]==[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
            day_lessons.append(lesson)
            
            # print(lesson["name"], start, end)

            # 添加课本
            for item in user_data["lesson_items"][lesson["name"]]:
                items.append(Item(item,"FF00FF",lesson)) #TODO 课本默认颜色
    return Inventory(items,day)

# TODO提醒

# plyer.notification.notify(title=f"提醒{datetime.date.today()}",message=notify_items(datetime.date.today()),timeout=5)

def _request_weather() -> dict: # 天气信息的获取上限是每分钟300次，超过会禁用一小时，数据每8小时更新一次
    res = requests.get(url="http://t.weather.sojson.com/api/weather/city/101020200") #TODO 默认为闵行区
    res.encoding = "utf-8"
    weather_dict=res.json()
    return weather_dict

def get_weather() -> dict: # 格式见weather_example.json
    if not os.path.exists("weather.json"):
        weather_dict = _request_weather()
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
        new_weather_dict = _request_weather()
        if new_weather_dict["status"] == 200: # 如果字典的 status == 200，则请求成功；否则status会变为错误代码，如404
            with open("weather.json", mode="w",encoding="utf-8") as f:
                json.dump(new_weather_dict,f) # 保存
            return new_weather_dict
    return weather_dict

# TODO 安卓端是否可以运行？

def say(text:str): # 语音播报
    engine = pyttsx4.init()
    engine.say(text)
    engine.runAndWait()
    # TODO 这可能会使线程终止，考虑多线程？

class Schedule:
    
    start_date:datetime.datetime
    courses:dict[tuple[int,int],str]
    arrangement:list[dict]

    def __init__(self) -> None:
        self = None #??????!!!!!!
 

    @staticmethod
    def from_wakeup(path:str): #! 默认为SJTU课表
        with open(path,mode="r",encoding="utf-8") as f:
            _str=f.read()
        # 括号栈算法
        _cnt=0
        _start=0
        _data=[]
        for i in range(len(_str)): 
            if _str[i] in ['[','{']:
                _cnt+=1
            elif _str[i] in [']','}']:
                _cnt-=1
                if _cnt == 0:
                    _data.append(_str[_start:i+1])
                    _start=i+1
        assert len(_data) == 5 #! 默认.wakeup_schedule格式正确
        global_schedule_settings=json.loads(_data[0])
        interval_settings=json.loads(_data[1])
        appearance_settings=json.loads(_data[2])
        courses=json.loads(_data[3])
        arrangement=json.loads(_data[4]) # course 的安排

        _schedule=Schedule()
        _date=appearance_settings["startDate"].split('-') #! 不是isoformat; e.g. 2024-2-19
        _schedule.start_date=datetime.date(int(_date[0]),int(_date[1]),int(_date[2]))

        #TODO 什么是tableId ?
        _course_dict:dict[tuple[int,int],str]={} # (tableId, id) ---> courseName #? 用这个格式为了在O(1)内获取数据
        for course in courses:
            name = course["courseName"]
            last = len(name) - 1
            if name[last] in ['◇','●','○','★','▲','☆']: #? 你交特色 ◇-理论●-实验○-实习★-上机▲-其他☆-课程设计
                name=name[:last] # TODO 是否一定要删除？
            _course_dict[(course["tableId"],course["id"])] = name
        _schedule.courses=_course_dict

        
        #? These attributes are neglected:
        #? startTime, endTime, ownTime may be combined; in SJTU schedule, they may be unnecessary.
        #? for all "level" == 0
        #? 

        _arrangement_list=[]
        for lesson in arrangement:
            _arrangement_content={
                "ids":(lesson["tableId"],lesson["id"]), # id的元组，用于获取courses
                "day":lesson["day"], # Monday == 1, Saturday == 6, #TODO #? Sunday == 0 or 7 ???? 
                "startWeek":lesson["startWeek"],
                "endWeek":lesson["endWeek"],
                "startNode":lesson["startNode"], # 第几节课开始上课，从1开始
                "step":lesson["step"], # 上几节课
                "type":lesson["type"], # 0: 全部，1: 单周，2: 双周
                "teacher":lesson["teacher"]
            }
            _arrangement_list.append(_arrangement_content)
        
        _schedule.arrangement = _arrangement_list

        return _schedule
    
    def to_json_dict(self):
        courses=[]
        for ids in self.courses:
            courses.append({
                "tableId": ids[0],
                "id": ids[1],
                "name": self.courses[ids]
            })
        return {
            "start_date":self.start_date.isoformat(),
            "courses":courses,
            "arrangement":self.arrangement
        }
    
class Data:
    global_items:list
    color_settings:list
    lesson_items:dict[str,list]
    virtual_lessons:list
    schedule:Schedule
    def __init__(self) -> None:
        self.global_items=[]
        self.lesson_items={
            "大学英语":["英语书"],
            "数学分析":["数分书"],
            "大学物理":["物理书"],
            "程序设计思想与方法":["C++书","电脑"],
            "概率统计":["概统书"],
            "思想道德与法治":[""],
            "工程学导论":["电脑"],
            "形势与政策":[""],
            "攀岩":["水"]
        }# default lesson items
        self.color_settings={}# default color
        self.virtual_lessons=["新时代社会认知实践"] #? only for sjtu; e.g. 新时代社会认知实践; will be neglected
        self.schedule = Schedule()

    def from_wakeup(self,path):
        self.schedule = Schedule.from_wakeup(path)

    def to_json_dict(self):
        return {
            "global_items": self.global_items,
            "color_settings": self.color_settings,
            "lesson_items": self.lesson_items,
            "virtual_lessons": self.virtual_lessons,
            "schedule": self.schedule.to_json_dict(),
        }

# TODO:: get canvas -ddl

_data=Data()
_data.from_wakeup("example.wakeup_schedule")
with open("__data.json",mode="w",encoding="utf-8") as f:
    json.dump(_data.to_json_dict(),f,ensure_ascii=False)