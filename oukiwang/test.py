import os
allfiles = os.listdir('./')
ofiles=[]
print [x.find(".o") for x in allfiles]