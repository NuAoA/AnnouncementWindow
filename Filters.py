from collections import OrderedDict
import re, os
import pickle
import Config
import sys
import json

class subgroup(object):
    def __init__(self, category, re_expression, w, show):
        self.category = category
        self.re_expressions = [re.compile(re_expression, re.IGNORECASE)]
        self.show = OrderedDict([])
        self.show[w] = show

    def get_show(self, w):
        s = self.show.get(w)
        if s is not None:
            return s
        elif w == -1:
            return self.show
        else:
            return False

    def set_show(self, w, show):
        s = self.show.get(w)
        if s is not None:
            self.show[w] = show
        else:
            raise UserWarning("[%s] Tried to set window data for window %d that does not exist: %s" % (self.category, w, self.show))  # TODO: remove

    def add_window(self, w):
        self.show[w] = self.show[0]

    def add_expression(self, re_expression):
        self.re_expressions.append(re.compile(re_expression, re.IGNORECASE))

    def check_expression(self, string):
        for expression in self.re_expressions:
            if expression.match(string):
                return True
        return False

    def get_rematch(self, string):
        for expression in self.re_expressions:
            e = expression.match(string)
            if e:
                return e
        return None

    def _dict(self):
        ret_dict = {'category':self.category, 'show':self.show}
        return ret_dict

class groups(object):
    def __init__(self, group):
        self.group = group
        self.color = "#FFF"
        self.categories = OrderedDict([])

    def lookup_category(self, category):
        return self.categories.get(category)

    def add_category(self, category, re_expression, w=0, show=True):
        # WARNING: do not call to create new show's
        cat = self.lookup_category(category)
        if cat is not None:
            cat.add_expression(re_expression)
        else:
            self.categories[category] = subgroup(category, re_expression, w, show)

    def set_color(self, color):
        self.color = color

    def set_show(self, category, w, show):
        cat = self.lookup_category(category)
        if cat is not None:
            cat.set_show(w, show)
        else:
            raise UserWarning("Nonetype object lookup, group:%s category:%s" % (self.group, category))  # TODO: remove

    def get_show(self, w, category):
        cat = self.lookup_category(category)
        if cat is not None:
            return cat.get_show(w)
        else:
            return False

    def find_expression(self, string):
        for category in self.categories.items():
            if category[1].check_expression(string):
                return category[1]
        return None

    def _dict(self):
        ret_dict = {'group':self.group, 'color':self.color, 'categories':OrderedDict([])}
        for cat_ in self.categories.items():
            ret_dict['categories'][cat_[0]] = cat_[1]._dict()
        return ret_dict

class announcement_filter(object):
    def __init__(self):
        self.groups = OrderedDict([])
        self.pickle_path = Config.settings.filters_pickle_path
        self.filters_path = Config.settings.filters_path
        self.filter_format = '\[(?P<group>\w+)\]\[(?P<category>\w+|\s*)\]\s*\"(?P<expression>.+)\"'
        self.window_count = 0
        self.reload()

    def reload(self):
        self.load_filter_expressions()
        self.load_filter_data()

    def lookup_group(self, group):
        return self.groups.get(group)

    def load_filter_expressions(self):
        self.groups.clear()
        if os.path.isfile(self.filters_path):
            with open(self.filters_path, 'r') as fi:
                for line in fi:
                    if not re.match('\#.+', line) and not re.match('\s*$', line) and len(line.strip()) != 0:
                        mat = re.match(self.filter_format, line)
                        if mat:
                            group = mat.group("group")
                            category = mat.group("category")
                            expression = mat.group("expression")
                            if category == "" or category == None:
                                category = "Other/All"
                            if not self.lookup_group(group):
                                self.groups[group] = groups(group)
                            self.lookup_group(group).add_category(category, expression)
        group = "UNKNOWN"
        category = "unmatchedString"
        expression = "(.+)"
        self.groups[group] = groups(group)
        self.groups[group].set_color("#FF0")
        self.lookup_group(group).add_category(category, expression)
        if self.window_count > 0:
            for window in range(0, self.window_count):
                for group in self.groups.items():
                    for cat in group[1].categories.items():
                        cat[1].add_window(window)

    def load_filter_data(self):
        if os.path.isfile(self.pickle_path):
            with open(self.pickle_path, 'r') as fi:
                groups_temp = json.load(fi, parse_int=True)
                for window in range(0, self.window_count):
                    for group in groups_temp.items():
                        g = self.lookup_group(group[0])
                        if g:
                            for cat in group[1]['categories'].items():
                                c = g.lookup_category(cat[0])
                                if c:
                                    if str(window) in cat[1]["show"]:
                                        g.set_show(cat[0], window, cat[1]["show"][str(window)])
                                    g.set_color(group[1]['color'])


    def save_filter_data(self):
        with open(self.pickle_path, 'w') as fi:
            json.dump(self._dict(), fi, indent=4)

    def find_expression(self, string):
        for group in self.groups.items():
            cat = group[1].find_expression(string)
            if cat:
                return group[1], cat
        return None, None

    def add_window(self, window):
        self.window_count += 1
        for group in self.groups.items():
            for cat in group[1].categories.items():
                cat[1].add_window(window)

    def print_filters(self):
        for group in self.groups.items():
            print('[%s]' % group[1].group)
            for cat in group[1].categories.items():
                print(' [%s]' % cat[1].category)
                print('  show: %s' % cat[1].show)
                print('   patterns:')
                for exp in cat[1].re_expressions:
                    print('    %s' % exp.pattern)
    def set_color(self, group, color):
        g = self.lookup_group(group)
        if g:
            g.set_color(color)
        else:
            raise UserWarning("Nonetype object lookup, group:%s color:%s" % (group, color))  # TODO: remove

    def get_color(self, group):
        g = self.lookup_group(group)
        if g:
            return g.color
        else:
            return "#FFF"

    def set_show(self, group, category, show, w):
        g = self.lookup_group(group)
        if g:
            g.set_show(category, w, show)
        else:
            raise UserWarning("Nonetype object lookup, group:%s category:%s" % (group, category))  # TODO: remove

    def get_show(self, group, category, w):
        g = self.lookup_group(group)
        if g:
            return g.get_show(w, category)
        else:
            return False

    def save_filter_expressions(self):
        line_list = []
        # Copy info at start of file:
        with open(self.filters_path, 'r') as fi:
            for line in fi:
                if not re.match('\#.+', line) and not re.match('\s*$', line) and len(line.strip()) != 0 and re.match(self.filter_format, line):
                    break
                line_list.append(line)
        # Write out expression data:
        with open(self.filters_path, 'w') as fi:
            for line in line_list:
                fi.write(line)
            for group_ in self.groups.items():
                group_name = group_[0]
                group = group_[1]
                for category_ in group.categories.items():
                    category_name = category_[0]
                    category = category_[1]
                    for exp in category.re_expressions:
                        if group_name != "UNKNOWN":
                            if category_name == "Other/All":
                                category_name = ""
                            fi.write('[%s][%s] "%s"\n' % (group_name, category_name, exp.pattern))
                    fi.write('\n')

    def _dict(self):
        # My own seralization method for the group dict
        ret_dict = OrderedDict([])
        for group_ in self.groups.items():
            ret_dict[group_[0]] = group_[1]._dict()
        return ret_dict
expressions = announcement_filter()
