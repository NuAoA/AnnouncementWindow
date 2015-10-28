import Filters
import Config

class announcement(object):
    def __init__(self,string):
        group,category = Filters.expressions.find_expression(string)
        if type(string) is bytes:
            self.text = string.decode('cp437')
        else:
            self.text = string
        if group == None or category == None:
            print(string)
            raise UserWarning("Nonetype object lookup, string:%s"%(string)) #TODO: remove 
        self.group_name = group.group
        self.category_name = category.category  
        
    def get_text(self,show_group = False,newline = True):
        if show_group:
            return "[%s][%s] %s"%(self.get_group(),self.get_category(),self.get_text())
        else:
            if newline:
                return "%s\n"%self.text
            else:
                return self.text

  
    def insert(self,announcement_window):
        window = announcement_window.id
        if self.get_show(window):
            announcement_window.index+=1          
            index = announcement_window.index
            announcement_window.insert("end",self.get_text(show_group=Config.settings.get_showgroups()))
            announcement_window.tag_add(self.get_group(),float(index),float(index+1))
            announcement_window.tag_config(self.get_group(),foreground=self.get_color())
            return True
        return False
    
    def get_group(self):
        return self.group_name
    
    def get_category(self):
        return self.category_name
    
    def get_show(self,window):
        return Filters.expressions.get_show(self.get_group(), self.get_category(), window) 
    
    def get_color(self):
        #return self.group.color
        return Filters.expressions.get_color(self.get_group())
  
    def print_text(self):
        print('%s'%(self.get_text(show_group=True).strip()))
        print('  Color:%s, Show:%s'%(self.get_color(),self.get_show(-1)))