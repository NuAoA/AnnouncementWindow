from collections import OrderedDict
import re, os
import Config

class subgroup(object):
    def __init__(self, colorName, word_list):
        self.colorName = colorName
        self.word_list = word_list

    def add_words(self, word_list):
        for word in word_list:
            self.word_list.append(word)

    def check_word(self,word):
        return word in self.word_list

    def set_wordlist(self, word_list):
        self.word_list = word_list.split(',')

class groups(object):
    def __init__(self, group):
        self.group = group
        self.colorName = OrderedDict([])

    def lookup_colorName(self, colorName):
        return self.colorName.get(colorName)

    def add_colorName(self, colorName, word_list):
        cN = self.lookup_colorName(colorName)
        if cN is not None:
            cN.add_words(word_list)
        else:
            self.colorName[colorName] = subgroup(colorName, word_list)

    def find_word(self, word):
        for colorName in self.colorName.items():
            if colorName[1].check_word(word):
                return colorName[0]

    def set_wordlist(self, colorName, word_list):
        cN = self.lookup_colorName(colorName)
        if cN is not None:
            cN.set_wordlist(word_list)

class color_grouping(object):
    def __init__(self):
        self.groups = OrderedDict([])
        self.datafile_path = Config.settings.wordcolor_path
        self.data_format = '\[(?P<group>\w+)\]\[(?P<colorName>\w+|\s*)\]\s*\"(?P<word_list>.+)\"'
        self.reload()

    def reload(self):
        self.load_color_data()

    def lookup_group(self, group):
        return self.groups.get(group)

    def load_color_data(self):
        """Parse all entry of the wordcolor.txt file
        """
        self.groups.clear()
        if os.path.isfile(self.datafile_path):
            with open(self.datafile_path, 'r') as fi:
                for line in fi:
                    if not re.match('\#.+', line) and not re.match('\s*$', line) and len(line.strip()) != 0:
                        mat = re.match(self.data_format, line)
                        if mat:
                            group = mat.group("group")
                            colorName = mat.group("colorName")
                            word_list_str = mat.group("word_list")
                            if not self.lookup_group(group):
                                self.groups[group] = groups(group)
                            self.lookup_group(group).add_colorName(colorName, word_list_str.split(','))

    def get_all_colorname(self):
        colors=[]
        for group in self.groups:
            for colorName in self.groups[group].colorName:
                if colorName not in colors:
                    colors.append(colorName)
        return colors
                            
    def get_colorname(self,word,group):
        """Get the colorname of a word in a group
        check in the default group if nothing found in
        the given group
        """
        if group in self.groups:
            cN=self.groups[group].find_word(word)
            if cN:
                return cN
        else:
            cND=self.groups['General'].find_word(word)
            if cND:
                return cND

    def get_all_group_words(self,group):
        """ Return all the words of a group and 
        the ones in the default group
        """

        l=[]
        for colorName in self.groups['General'].colorName:
            for word in self.groups['General'].colorName[colorName].word_list:
                l.append(word)

        if group in self.groups:
            for colorName in self.groups[group].colorName:
                for word in self.groups[group].colorName[colorName].word_list:
                    l.append(word)
        return l
            
wd = color_grouping()
