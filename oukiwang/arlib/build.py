import os
allfiles = os.listdir('./')
ofiles=[]
for x in allfiles:
    if x.find(".o") != -1:
        ofiles.append(x)
print ofiles

cmd = "C:/Users/huiwang/AppData/Local/Arduino15/packages/esp8266/tools/xtensa-lx106-elf-gcc/1.20.0-26-gb404fb9-2/bin/xtensa-lx106-elf-ar cru  \"./lib.ar\" "
for file in ofiles:
    command = cmd + "./"+file
    print command
    os.system(command)