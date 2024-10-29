# Set up and run this Streamlit App
from logics.load_data import loadfiles
import os


filelist = loadfiles(printdebug=2)
print(len(filelist))
print(filelist.keys())

newsubdir = "output"
if not os.path.isdir(newsubdir):
    os.mkdir(newsubdir)
for file in filelist:
    basefile = os.path.basename(file)
    newfile = newsubdir+"/"+basefile
    print("create new file:",newfile)
    filelist[file].to_csv(newfile,index=False)

newsubdir = "outpickle"
if not os.path.isdir(newsubdir):
    os.mkdir(newsubdir)
for file in filelist:
    basefile = os.path.basename(file)
    newfile = newsubdir+"/"+basefile
    newfile = newfile.replace(".csv",".pkl")
    if not os.path.exists(newfile)  :
        print("create new file:",newfile)
        filelist[file].to_pickle(newfile)    


