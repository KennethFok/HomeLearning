import os
from os import (listdir)
from os.path import (isfile,join)
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.carousel import Carousel
from kivy.core.text import LabelBase
from kivy.properties import (ObjectProperty, NumericProperty, OptionProperty,
                             BooleanProperty, StringProperty, ListProperty)
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import (FocusBehavior, ButtonBehavior)
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.clock import Clock
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.widget import Widget
from kivy.uix.videoplayer import VideoPlayer
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.config import Config

# Gets current python dir then add the KV dir
kv_path = os.getcwd() + '/kv/'
kv_load_list = [f for f in listdir(kv_path) if isfile(join(kv_path, f))]

icon_folder = 'res\icons8-folder-500.png'
icon_file = 'res\icons8-file-500.png'
icon_video = 'res\icons8-cinema-film-play-500.png'

# Loads all KV file
for file in kv_load_list:
    if file.endswith('.kv'):
        Builder.load_file(kv_path + file)

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''

class Item(ButtonBehavior, BoxLayout):
    def change_location(self):
        if self.type == 'folder':
            App.get_running_app().folder_path = self.path
            App.get_running_app().current_lv = self.lv + 1
            App.get_running_app().root.screen_main.ids.FileList.data = getFileList(App.get_running_app().file_list, self.path)
        elif self.type == 'video':
            #self.parent.parent.parent.parent.parent.screen_video.video_file = self.path
            App.get_running_app().root.screen_video.video_file = self.path
            App.get_running_app().root.screen_video.set_video(self.path)
            App.get_running_app().root.current = 'Video Screen'

class SelectableItem(RecycleDataViewBehavior, Item):
    ''' Add selection support to the Item '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableItem, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableItem, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
            
        else:
            print("selection removed for {0}".format(rv.data[index]))

class VideoScreen(Screen):
    def __init__(self, *args, **kwargs):
        super(VideoScreen, self).__init__(*args, **kwargs)

    def set_video(self, video_file):
        #self.video_file = video_file
        #self.remove_widget(self.player)
        #self.player = VideoPlayer(size_hint=(1.0, 0.9), pos_hint={'x':0, 'y': 0}, source=video_file, state='play', options={'allow_stretch': True, 'fullscreen': True})
        #self.add_widget(self.player)
        #self.player.source = video_file
        print(video_file)

    def do_exit(self):
        self.player.state = 'stop'
        App.get_running_app().root.current = 'Main Screen'
        
    def on_leave(self):
        self.player.state = 'stop'
    
    def state_change(instance, value):
        print("Enter state_change")
        if value == 'stop' and self.player.duration ==self.player.position:
            App.get_running_app().root.current = 'Main Screen'

class MainScreen(Screen):
    def gotoRootFolder(self):
        if App.get_running_app().current_lv == 0:
            return
        templist = getFileListByLv(App.get_running_app().file_list, 0)
        if (len(templist) > 0):
            App.get_running_app().folder_path = templist[0]['rootpath']
            App.get_running_app().current_lv = 0
            self.ids.FileList.data = getFileList(App.get_running_app().file_list, App.get_running_app().folder_path)
    
    def gotoPrevFolder(self):
        if App.get_running_app().current_lv == 0:
            return
        templist = getFileListByPath(App.get_running_app().file_list, App.get_running_app().folder_path)
        if (len(templist) > 0):
            App.get_running_app().folder_path = templist[0]['rootpath']
            App.get_running_app().current_lv = int(templist[0]['lv'])
            self.ids.FileList.data = getFileList(App.get_running_app().file_list, App.get_running_app().folder_path)

class ScManager(ScreenManager):
    transition = NoTransition()
    screen_main = ObjectProperty(None)
    screen_video = ObjectProperty(None)
    screen_setting = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(ScManager, self).__init__(*args, **kwargs)

class HomeLearningApp(App):
    folder_path = StringProperty('D:\\')
    file_list = ListProperty()
    current_lv = NumericProperty(0)
    def get_application_config(self):
        return super(HomeLearningApp, self).get_application_config(
            'config/%(appname)s.ini')

    def build_config(self, config):
        config.setdefaults('HomeLearning', {})

    def build(self):
        config = self.config
        self.folder_path = config.get('HomeLearning','Path')
        sm = ScManager()
        #main = m.ids.MainContent
        #m.ids.FileList.data = [{'text': str(x), 'type':('folder','video')[x%2==0], 'source':('res\iconfinder_folder_299060.png','res\iconfinder_play_1055007.png')[x%2==0]} for x in range(100)]
        self.file_list = loadFileList(self.folder_path)
        sm.screen_main.ids.FileList.data = getFileList(self.file_list, self.folder_path)

        return sm

    def build_settings(self, settings):
        settings.add_json_panel('HomeLearning', self.config, 'config\settings.json')


def getFileList(file_list, path):
    return list(filter(lambda x: x['rootpath'] == path, file_list))

def getFileListByLv(file_list, lv):
    return list(filter(lambda x: x['lv'] == lv, file_list))

def getFileListByPath(file_list, path):
    return list(filter(lambda x: x['path'] == path, file_list))

def loadFileList(folder_path):
    #print(folder_path)
    file_list = []
    filter_prefix = ('_', '$')
    filter_fileext= ('ini', 'sys')
    video_fileext= ('mp4')
    lv_set = {}
    lv = 0
    lv_set[folder_path] = 0
    for root, dirs, files in os.walk(folder_path):
        if root.startswith(filter_prefix):
                continue

        if root in lv_set:
            lv = lv_set[root]

        #print("lv({}): {}".format(lv,root))
        #print(files)
        for name in dirs:
            if name.startswith(filter_prefix):
                continue
            lv_set[join(root, name)] = lv + 1
            item = {}
            item['lv'] = lv
            item['rootpath'] = root
            item['path'] = join(root, name)
            item['text'] = name
            item['type'] = 'folder'
            item['source'] = icon_folder
            file_list.append(item)
        for name in files:
            if name.startswith(filter_prefix):
                continue
            if name.endswith(filter_fileext):
                continue
            item = {}
            item['lv'] = lv
            item['rootpath'] = root
            item['path'] = join(root, name)
            item['text'] = name
            item['type'] = ('file','video')[name.endswith(video_fileext)]
            item['source'] = (icon_file, icon_video)[name.endswith(video_fileext)]
            file_list.append(item)
        lv += 1
    #print(file_list)
    return file_list


if __name__ == '__main__':
    LabelBase.register(name='FA5Regular',
                       fn_regular='res\\FontAwesome5\\Font Awesome 5 Free-Regular-400.otf')
    LabelBase.register(name='FA5Solid',
                       fn_regular='res\\FontAwesome5\\Font Awesome 5 Free-Solid-900.otf')
    LabelBase.register(name='tradchinese',
                       fn_regular='res\\NotoSansTC\\NotoSansTC-Regular.otf',
                       fn_bold='res\\NotoSansTC\\NotoSansTC-Bold.otf')
    HomeLearningApp().run()