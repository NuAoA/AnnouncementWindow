# Announcement Window+

Announcement Window+ is a python application that interfaces with Dwarf Fortress to print announcements and combat reports to a separate window.

You can edit the type of announcements that are shown in the two separate displays. For example, the first window could be set up to show announcements (```a```) and the other could show a live feed of your combat reports (```r```). No more pausing the game! 

You can also configure the font/size/color of the announcements (by right clicking on either display), and with a basic understanding of [regular expressions](https://docs.python.org/2/library/re.html) you can even create your own custom filters!

This program was written for python 2.7.10, but now has python 3 support! It should work with any version of python > 2.3 

## Configuration

### **Install**

If you are running windows, download the latest release (https://github.com/BrachystochroneSD/AnnouncementWindow/releases) and unzip the folder anywhere on your computer. Click *AnnouncementWindow.exe* to launch.

If you are not on windows, or just want to run the code directly, you will need to have python installed on your computer. Download the repository. The program is launched by running the script *run.py*.

### **Setup**

The first time you start Announcement Window+, you need to connect the program to Dwarf Fortress. Just click ```Set Directory``` and locate *gamelog.txt* in the main folder of your dwarf fortress install. If you can't find it you probably have not started a fortress yet, once you do that the file will be created. Alternatively, you can manually edit the variable ```gamelog_path``` in *settings.cfg* before launching the program (see below).

### **Custom Filters**

If you want to take a look at how the announcements are filtered, right click the window and click ```Toggle Tags``` to see how each announcement is tagged. These filters and tags are loaded from the file found at ```Open Filters.txt```, and can be configured by opening the ```Filters Configuration``` window. 

Each filter uses regular expressions to group announcements into categories for easy filtering (see: https://docs.python.org/2/library/re.html). Anything that you find in your *gamelog.txt* file will be checked against these expressions. 

Each tag follows the format:

	[group][category] "regular_expression"
    
Where ```[group]``` is a tag to set a separate color for each matched announcement. Whatever color you set will carry over to every window. ```[category]``` is a separate tag for each window, and is used to set if the announcement should be shown in the window or not.

The expressions are checked in the order that their tags appear in the file. This means that the first instance of [group] that is seen will cause every [category] and expression that has that group tag to be checked before moving on to other tags in the file. Filters with the same tag are checked sequentially. You can check ```Filters Configuration``` to see the order that the program loads the filters.

#### Here's a typical example:

Say you don't like how the announcements for Thief's showing up share the same color with as Snatchers. Just edit *Filters.txt* and change the group for that regular expression from ```[intruders]``` to something new.
specifically, you could change the line

	[intruders][intruders] "Thief!  Protect the hoard from skulking filth!"

to 

	[intruders_Theif][intruders] "Thief!  Protect the hoard from skulking filth!"

Now you can now edit the color for the new group ```[intruders_Thief]```.

### **Custom Word Coloring**

You can customize the list of words to be highlighted with a defined color with similare format
in the wordcolor.txt
Each tag follows the format:

[group][colortag] "list,of,words"

Where ```[group]``` is the same tag as the filters.txt format. The ```[colortag]``` is
defined in the *Settings.cfg* [Colors] section (see Settings/Colors section below). The words need to be listed between double quotes
and separated with coma.

For example, to set all "cancels" and "mandate" words to be highlighted in red, you can add
a line in the wordcolor.txt:
```
[General][red] "cancels,mandate"
```

You can specify the same word with different colors for different group like so:
```
[battle][green] "Urist McColored"
[masterpiece][olive] "Urist McColored"
```

### **Settings**

There are a few options in *settings.cfg* that change how the program functions. For the most part they allow you to change how demanding this program is on your CPU along with how much memory it uses, which is only really a concern if you are running a [danger room](http://dwarffortresswiki.org/index.php/DF2014:Danger_room) ("*The Dwarf blocks The spinning *apricot wood training spear* with the -copper shield-!*" spam) or otherwise are generating hundreds of announcements per second. Note, periodically clearing the windows (maybe once per hour) will keep even the worst offenders under ~150mb of ram. Also, if you are running multiple cores (its 2015 for god sakes) CPU usage is not much of a concern since Dwarf Fortress only uses a single core. 

* ```gamelog_path```: 

Lets you manually set the path to your *gamelog.txt* file.

* ```load_previous_announcements```:

When the program is opened, this option will load all announcements in *gamelog.txt* since the last time a fortress was loaded. If you open the program with this option before loading your fortress, it will load the announcements from your last game session. 

* ```save_hidden_announcements```: 

If you set this to ```True``` it tell the program to save all announcements, even if they are not shown in the window. This would use more memory (especially if you are hiding tons of announcement spam) and a bit more CPU power, but allows you to see all past announcements that have not been printed to the window. For example, if this option is enabled, after your fortress has been turned into a lake of dwarf blood by some megabeast, you could enable all combat announcements (if they were previously disabled) to see a play by play of how they all fought and died. Otherwise, those previously hidden announcements will not show up once you you enable their visibility.

* ```trim_announcements_[window number]``` 

This option saves system memory at the cost of increased CPU power. If it is set to any integer value above zero, it will limit how many of each announcement type (category) are saved in memory. For example, a value of 2000 would store only up to 2000 of each type of announcement (ie 2000 ```[battle_minor][hitevents_miss]``` along with 2000 ```[battle_minor][block_dodge]```, which are typical combat training spam). Once there are 2000 of that type of announcement, the oldest announcement will be thrown out to free up some space. If it is set to zero, all announcements will be kept until you clear the window(s).

Another use of this option is to set the value to 1 for one of the windows, making it only display a single announcement from each category. The window would then only display the most recent event, ie. *"A (.+) caravan from (.+) has arrived"* would be replaced by *"Merchants have arrived and are unloading their goods"* once they reach your trade depot or "It has started Raining" would be replaced by "The weather has cleared" when the rain stops.

* ```Colors```

Simply add your custom "ColorTag" under the section [Colors] with a custom name and the hex value of your choice.
Each "colortag" can take two arguments: a *foreground* color and a *background* color (#RGB or #RRGGBB).
The format is:
```tagname = #foreground #background```
If there's no background color defined, the ```default_background``` color is used.
The ```default_background``` only take one argument and set the default background used for non-specified background colortag.
You can modify the hex value of the default colors and assign new words in the wordcolor.txt file.
