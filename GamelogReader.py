import Config
import os,io
from Announcements import announcement
import re

class gamelog(object):
    def __init__(self):
        self.file = None
        
    def connect(self):
        if os.path.isfile(Config.settings.get_gamelog_path()):            
            self.file = io.open(Config.settings.get_gamelog_path(),'r')
            self.file.seek(0,2) #Move to the end of the file
            return True
        else:
            self.file = None
            return False
        
    def get_new_announcements(self,list_=None):
        if list_ is None:
            list_ = self.file
        new = []
        if self.file:
            for newline in list_:            
                s = newline.strip()
                if len(s) != 0:                                
                    new.append(announcement(s))
        return new

    def get_old_announcements(self):
        lines = []
        if self.file:
            self.file.seek(0,0)
            exp = re.compile('\*\* Loading Fortress \*\*')
            for line in self.file:
                if exp.match(line):
                    lines = []
                lines.append(line)
        return self.get_new_announcements(list_=lines)            
                      
    def new(self):
        return self.get_new_announcements()
    
    def get_all_announcements(self):
        if self.file:
            self.file.seek(0,0)
        return self.get_new_announcements()        



