# import reminder_cmd
import kivy

from kivy.app import App
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout

from reminder_lib import * # 作为库文件使用

LabelBase.register(name='Default',
                   fn_regular='STXIHEI.ttf')

from kivy.config import Config

Config.set('graphics','resizable',False) # 将窗口设为不可更改大小 #TODO 考虑不同窗口分辨率？

kivy.require("2.3.0")

class MainWindowsLayout(BoxLayout):
    def show_weather(self):
        00

class TestLayout(BoxLayout):
    pass

class ReminderWindowsApp(App):
    def on_start(self):
        pass

if __name__ == "__main__":
    app=ReminderWindowsApp()
    app.title="个性化物品提醒小助手"
    # TODO SleepDown
    app.icon="Genshin.jpg" #TODO 需要一个图标，不能用原神
    app.run()
    # https://i.sjtu.edu.cn/kbcx/xskbcx_cxXskbcxIndex.html?gnmkdm=N2151&layout=default
    