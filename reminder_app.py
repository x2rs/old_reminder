# import reminder_cmd
import kivy

from kivy.app import App
from kivy.uix.label import Label
from kivy.core.text import LabelBase

LabelBase.register(name='Default',
                   fn_regular='STXIHEI.ttf')

kivy.require("2.3.0")


class ReminderWindowsApp(App):
    pass

if __name__ == "__main__":
    app=ReminderWindowsApp()
    app.title="个性化物品提醒小助手"
    app.icon="Genshin.jpg" #TODO 需要一个图标，不能用原神
    app.run()