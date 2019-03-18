import sys
if sys.version_info.major == 2:
    import ConfigParser
elif sys.version_info.major == 3:
    import configparser as ConfigParser

import pickle
import os
import re
import util


def locate_gamelog(path=os.getcwd()):
    # locates gamelog.txt automatically if opened from LNP utility folder
    # Note: Its pretty sloppy, not sure what is the most reliable method to locate dwarf fortress directory.
    path_ = path
    try:
        head, tail = os.path.split(path_)
        while tail:
            if tail == "LNP":
                # Head is LNP install dir
                for item in os.listdir(head):
                    if re.match('[Dd]warf\s*[Ff]ortress\s*\d+\.\d+\.\d+', item):
                        if os.path.isdir(os.path.join(head, item)):
                            path_ = os.path.join(head, item)
                            if os.path.isfile(os.path.join(path_, 'gamelog.txt')):
                                path_ = os.path.join(path_, 'gamelog.txt')
                            break
                break
            else:
                head, tail = os.path.split(head)
    finally:
        return path_

class config(object):
    def __init__(self):
        self.parser = ConfigParser.ConfigParser()
        self.filepath = "Settings.cfg"
        self.filters_path = "filters.txt"
        self.wordcolor_path = "wordcolor.txt"
        self.gui_data = "Data/gui.dat"
        self.filters_pickle_path = "Data/filters.dat"
        self.icon_path = "@Data/favicon.XBM" if util.platform.linux else "Data/favicon.ico"
        self.init_var()
        self.load()

    def load_gui_data(self):
        if os.path.isfile(self.gui_data):
            with open(self.gui_data, 'rb') as fi:
                return pickle.load(fi)
        return None

    def save_gui_data(self, data):
        with open(self.gui_data, 'wb') as fi:
            pickle.dump(data, fi, protocol=0)

    def init_var(self):
        self.gamelogpath = locate_gamelog()
        self.showgroups = False
        self.load_previous_announcements = False
        self.save_hidden_announcements = False
        self.trim_announcements = [0, 0]
        self.word_color_dict={"white":"#FFFFFF","silver":"#C0C0C0","gray":"#808080","black":"#000000","red":"#FF0000","maroon":"#800000","yellow":"#FFFF00","olive":"#808000","lime":"#00FF00","green":"#008000","aqua":"#00FFFF","teal":"#008080","blue":"#0000FF","navy":"#000080","fuchsia":"#FF00FF","purple":"#800080"}

    def load(self):
        if not os.path.exists(self.filepath):
            self.parser.add_section("Settings")
            self.parser.set("Settings", 'gamelog_path', self.gamelogpath)
            self.parser.set("Settings", 'save_hidden_announcements', str(self.save_hidden_announcements))
            self.parser.set("Settings", 'load_previous_announcements', str(self.load_previous_announcements))
            self.parser.set("Settings", 'trim_announcements_0', str(self.trim_announcements[0]))
            self.parser.set("Settings", 'trim_announcements_1', str(self.trim_announcements[1]))
            self.parser.add_section("Colors")
            for color in self.word_color_dict:
                self.parser.set("Colors",color,self.word_color_dict[color])
            self.save()
        else:
            self.parser.read(self.filepath)
            self.gamelogpath = self.parser.get("Settings", "gamelog_path").replace('"', '')
            self.save_hidden_announcements = self.parser.getboolean("Settings", 'save_hidden_announcements')
            self.load_previous_announcements = self.parser.getboolean("Settings", 'load_previous_announcements')
            self.trim_announcements[0] = self.parser.getint("Settings", 'trim_announcements_0')
            self.trim_announcements[1] = self.parser.getint("Settings", 'trim_announcements_1')
            self.word_color_dict={}
            for (color_name,color_value) in self.parser.items("Colors"):
                self.word_color_dict[color_name]=color_value

    def save(self):
        with open(self.filepath, 'w') as fi:
            self.parser.write(fi)

    def get_gamelog_path(self):
        return self.gamelogpath

    def set_gamelog_path(self, path):
        self.gamelogpath = path.replace('"', '')
        self.parser.set("Settings", "gamelog_path", self.gamelogpath)
        self.save()

    def get_showgroups(self):
        return self.showgroups

    def set_showgroups(self, toggle):
        self.showgroups = toggle
        self.parser.set("Settings", "show_groups", self.showgroups)
        self.save()

settings = config()
