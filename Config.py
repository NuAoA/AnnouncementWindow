import ConfigParser
import pickle
import os

class config(object):
    def __init__(self):
        self.parser = ConfigParser.ConfigParser()        
        self.filepath =            "Settings.cfg"
        self.filters_path =        "filters.cfg"       
        self.gui_data =            "gui.dat"
        self.filters_pickle_path = "filters.dat"
        self.section ="Settings"
        self.init_var()
        self.load() 
        
    def load_gui_data(self):
        if os.path.isfile(self.gui_data):
            with open(self.gui_data,"r") as fi:
                return pickle.load(fi)
        return None
    
    def save_gui_data(self,data):
        with open(self.gui_data,"w") as fi:
            pickle.dump(data,fi)
            
    def init_var(self):
        self.gamelogpath = os.getcwd()
        self.showgroups = False
        self.load_previous_announcements = False
        self.save_hidden_announcements = False
        self.trim_announcements = [0,0]
        
    def load(self):
        if not os.path.exists(self.filepath):
            self.parser.add_section(self.section)
            self.parser.set(self.section, 'gamelog_path', self.gamelogpath)
            self.parser.set(self.section, 'save_hidden_announcements', self.save_hidden_announcements)
            self.parser.set(self.section, 'load_previous_announcements', self.load_previous_announcements)
            self.parser.set(self.section, 'trim_announcements_0', self.trim_announcements[0])
            self.parser.set(self.section, 'trim_announcements_1', self.trim_announcements[1])
            self.save()
        else:    
            self.parser.read(self.filepath)
            self.gamelogpath = self.parser.get(self.section,"gamelog_path").replace('"','')
            self.save_hidden_announcements = self.parser.getboolean(self.section,'save_hidden_announcements')
            self.load_previous_announcements = self.parser.getboolean(self.section,'load_previous_announcements')
            self.trim_announcements[0] = self.parser.getint(self.section,'trim_announcements_0')
            self.trim_announcements[1] = self.parser.getint(self.section,'trim_announcements_1')

    def save(self):
        with open(self.filepath, 'w') as fi:
            self.parser.write(fi)
        
    def get_gamelog_path(self):
        return self.gamelogpath
        
    def set_gamelog_path(self,path):
        self.gamelogpath = path.replace('"','')
        self.parser.set(self.section,"gamelog_path",self.gamelogpath)        
        self.save()
    
    def get_showgroups(self):
        return self.showgroups
        
    def set_showgroups(self,toggle):
        self.showgroups = toggle
        self.parser.set(self.section,"show_groups",self.showgroups)
        self.save()

settings = config()
