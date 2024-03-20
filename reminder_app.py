# import reminder_cmd
import kivy

from kivy.app import App
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout

from reminder_cmd import * # 作为库文件使用

LabelBase.register(name='Default',
                   fn_regular='STXIHEI.ttf')

kivy.require("2.3.0")

class MyLayout(BoxLayout):
    def print_result(self):
        inv=get_inventory(datetime.date.today())
        self.ids.main_label.text=inv.to_kivy_text()

class ReminderWindowsApp(App):
    pass


if __name__ == "__main__":
    app=ReminderWindowsApp()
    app.title="个性化物品提醒小助手"
    app.icon="Genshin.jpg" #TODO 需要一个图标，不能用原神
    app.run()