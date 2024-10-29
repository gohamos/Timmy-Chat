import os
import pandas as pd
import numpy as np
import dateutil.parser as dtparse
from datetime import datetime, date

#DONE Reading of Data Sheets
#DONE Reading of Value Lookup Sheets
#DONE Reading of Expressway Direction Lookup values
#DONE Replace Lookup values in Data sheets



class EwayEntry:
    def __init__(self): 
        self.code = 0 
        self.name = ""
        self.dir= dict()

    def fromRow(self,row):  
        if "EWAY_CODE" in row:
            self.code = (int)( row["EWAY_CODE"])
        if "EWAY_NAME" in row:
            self.name = (str)( row["EWAY_NAME"])
        if "DIR_DESC" in row and "DIR_ID" in row:
            self.dir[row["DIR_ID"]] = (str)( row["DIR_DESC"])

    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return "EWay("+(str)(self.code)+","+self.name+","+(str)((self.dir))+")"
        
def getDirList(dir="",subdir=1):
    dirlist = []
    if os.path.isdir(dir):
        # Change the working directory to path specified
        dirlist.append(dir)        
        if subdir>0:
            for subdir in os.listdir(dir):
                if os.path.isdir(dir+"/"+subdir):
                    dirlist.append(dir+"/"+subdir)

        
    return dirlist;


def ReparsePath(path):
    path = path.replace("\n","")
    path = path.replace("\r","")
    if "https://drive.google.com/file/d" in path:
        path = 'https://drive.google.com/uc?export=download&id='+path.split('/')[-2]
    return path

def loadLookup(dir="",filelist=[],subdir=1, filtercols=[], filtertime=1, formattime=0, printdebug=0,reparse=1, removeinvalid=1):
   
    if printdebug>0: print(f"loadLookup():: The current working directory is: {dir}")
    DictMap = dict()
    EwayDict = dict()
    
    if len(dir)==0 and len(filelist)==0:
        # Change the working directory to the current file's directory
        dir = os.path.dirname(os.path.abspath(__file__))
    #01/08/2024 9:59
    if os.path.isdir(dir):
        dirlist = getDirList(dir=dir,subdir=subdir)               
        if printdebug>0: print(f"loadLookup():: The current working directory is: {dir}")
        for searchdir in dirlist:
            if os.path.isdir(searchdir):
                if printdebug>0: print("[]in folder",searchdir)
                for file in os.listdir(searchdir):
                    filelower=file.lower()
                    fullpath = searchdir+"/"+file
                    fullpathlower = fullpath.lower()
                    if ".csv" in file:
                            if "lookup" in fullpathlower:
                                if "ir" in filelower:
                                    filelist.append(fullpath)
                                
                       
    for fullpath in filelist:         
        try:
            fullpath = ReparsePath(fullpath)
            if len(fullpath)==0: continue;
            if printdebug>0: print("\t..reading definition file: ",fullpath)
            
            df_file = pd.read_csv(fullpath)
            lookupname = ""
            lookupkey = ""
            lookupvalue=""
            if len(df_file.keys())<=3:
                #Reading of Value Lookup Sheets
                for key in df_file:
                    #print(key)
                    if "_ID" in key:
                        lookupkey = key;
                        lookupname = lookupkey.replace("_ID","");
                    if "_DESC" in key:
                        lookupvalue = key;
                if printdebug>0: 
                    print("\t\t >> name:",lookupname)
                    print("\t\t >> key:",lookupkey)
                    print("\t\t >> value:",lookupvalue)
                DictMap[lookupname] = dict()
                for idx,row in df_file.iterrows():
                    if lookupkey in row and lookupvalue in row :# Skip header row
                        deffirst = (str)(row[lookupkey])
                        defsecond = (row[lookupvalue])
                        if "removed" not in defsecond:
                            DictMap[lookupname][deffirst] = defsecond
                if printdebug>0: 
                    print("\t<"+lookupname+"> dictmap:",DictMap[lookupname])
            else:
                #Reading of Expressway Direction Lookup values
                if "DIR" in fullpath:
                    for idx,row in df_file.iterrows():
                        tEntry = EwayEntry()
                        tEntry.fromRow(row)
                        #print (tEntry)
                        if tEntry.code>0:
                            if tEntry.code in EwayDict:
                                EwayDict[tEntry.code].dir.update(tEntry.dir)
                            else:
                                EwayDict[tEntry.code] = tEntry       
                else:
                    if printdebug>0: print("\t\t >> skip",len(df_file.keys()))
        except:
            if printdebug>0: print("\t!! cannot read file: ",fullpath)
    return DictMap,EwayDict;
                                        
    

def loadfiles(dir="",filelist=[],subdir=1, filtercols=[], filtertime=0, formattime=0, printdebug=0,reparse=1, removeinvalid=1):
    dtfilter = dtparse.parse("1/1/2000")
    lst_df_all = dict()
    DictMap = dict()
    EwayDict = dict()
    
    
    if len(dir)==0 and len(filelist)==0:
        # Change the working directory to the current file's directory
        dir = os.path.dirname(os.path.abspath(__file__))
            
            
    
    if os.path.isdir(dir):
        if printdebug>0: print(f"loadfiles():: The current working directory is: {dir}")        
        dirlist = getDirList(dir=dir,subdir=subdir)        
        for searchdir in dirlist:      
            if os.path.isdir(searchdir):
                if printdebug>0: print(f"[] searching in : {searchdir}")  
                sublist = os.listdir(searchdir)
                for sub in sublist:
                    if os.path.isfile(searchdir+"/"+sub):
                        filelist.append(searchdir+"/"+sub)
    elif os.path.isfile(dir):
        if printdebug>0: print(f"loadfiles():: current path is file: {dir}")        
        filelist=[file]        
    elif len(filelist)==0:
        if printdebug>0: print("!! Cannot find directory",dir)
        return lst_df_all;
    
    dateparse = lambda dates: [datetime.strptime(d, '%d/%m/%Y %H:%M') for d in dates]
            
    for file in filelist:
        fullpathlower = file.lower()        
        if "http" in fullpathlower or "lookup" not in fullpathlower:
            try:
                file = ReparsePath(file)
                if len(file)==0: continue;
                if "http" in fullpathlower or  ".csv" in fullpathlower:
                    # Reading of Data Sheets
                    if printdebug>0: print("\t..reading data file: ",file)
                    headercols = pd.read_csv(ReparsePath(file), index_col=0, nrows=0).columns.tolist()
                    headercols = [k for k in headercols if 'TIME' in k]
                    df_file = pd.read_csv(ReparsePath(file),parse_dates=headercols,date_format='%d/%m/%Y %H:%M')
                    if printdebug>1:  print(df_file.info(), flush = True)
                    lst_df_all[file]=df_file
                if ".pkl" in fullpathlower:
                    # Reading of Data Sheets
                    if printdebug>0: print("\t..reading data file: ",file)
                    df_file = pd.read_pickle(file)
                    if printdebug>1:  print(df_file.info(), flush = True)
                    lst_df_all[file]=df_file
            except:
                if printdebug>0: print("\t!! cannot read file: ",file)
                        
                        
    if reparse>0:
        DictMap ,EwayDict =loadLookup(dir,subdir,printdebug=printdebug)
                
    if printdebug>1:
        print("size of lst_df_all: ",len(lst_df_all))
        if len(DictMap)>0:
            print("Lookup definition Map :")
            for defi in DictMap:
                print("Defintion Map for",defi)
                print(DictMap[defi])
                
        if len(EwayDict)>0:
            print("Expressway definition Map :")
            for defi in EwayDict:
                print(EwayDict[defi])
        print(flush=True)

   
    # Replace Lookup values in Data sheets
    if len(DictMap)>0 or len(EwayDict)>0 or formattime>0 or filtertime>0 or len(filtercols)>0:
        from copy import deepcopy
        lst_df_renamed = dict() 
        for filepath in lst_df_all:
            if printdebug>0: print("[]reparse file:",filepath, flush=True)
            filecopy = deepcopy(lst_df_all[filepath])
            collist = filecopy.columns.tolist()
            if printdebug>0: print(collist, flush=True)
            
            def subRRemapValues(thisfile,col,RemapDict):
                if printdebug>0: print("\t..Mapping col:",col, flush=True)
                for idx,val in enumerate(thisfile[col]): 
                    tval = (str)(val)
                    if tval in RemapDict:
                        newvalue = RemapDict[tval]
                        if printdebug>1: print("   >>row",idx, "replace",tval,"with",newvalue,"for",col,flush=True)
                        thisfile.loc[idx,col]=newvalue
                    else:
                        if printdebug>1: print("   !!row",idx, " cannot replace",tval,"for",col,RemapDict,flush=True)   
                        if removeinvalid>0:
                           thisfile.loc[idx,col]=""
                            
                        
            def subRRemapEway(thisfile,col,EwayDict):
                if printdebug>0: print("\t..Mapping Eway col:",col, flush=True)
                for idx,val in enumerate(thisfile[col]): 
                    tcode = (str)(val)
                    if tcode in EwayDict:                
                        if printdebug>1: print("   >>row",idx, "replace",row["EWAY_CODE"],"with",EwayDict[tcode].name,"for","EWAY_CODE")
                        thisfile.loc[idx,col] = EwayDict[tcode].name
                    else:
                        if printdebug>0: print("   !! Unknown EWAY_CODE",tcode, flush=True)                        
                        
                        
            def subRFilterTimestamp(thisfile,col):
                if printdebug>0: print("\t..Parsing Time in col:",col, flush=True)
                for idx,val in enumerate(thisfile[col]):
                    if isinstance(val, str):
                        if len(val)>0:
                            #print(type(val))
                            if filtertime>0 and "1970" in val:
                                dt = dtparse.parse(val,dayfirst=True)
                                if dt<dtfilter:
                                   thisfile.loc[idx,col]=np.nan
                                   continue;
                            elif formattime>0:
                                dt = dtparse.parse(val,dayfirst=True)
                                thisfile.loc[idx,col]=dt
                    elif isinstance(val, datetime):
                        if val<dtfilter:
                            thisfile.loc[idx,col] = np.nan
                    else :
                        print("skip",type(val))
                            

                            
                        
            collist = filecopy.columns.tolist()    
            for defi in collist:
                if len(filtercols)>0:
                    sdefi = (str)(defi)
                    if sdefi in filtercols:
                        if printdebug>0: print("\t..Dropping col:",defi, flush=True)
                        #remove column
                        filecopy.drop(defi, inplace=True, axis=1)
                        continue;
                if defi in DictMap:   
                    subRRemapValues(filecopy,defi,DictMap[defi])
                elif "EWAY_CODE"==defi:
                    subRRemapEway(filecopy,defi,EwayDict)  
                elif (filtertime>0  or formattime>0) and "TIME" in defi:
                    subRFilterTimestamp(filecopy,defi,)     
                
            lst_df_renamed[filepath]=filecopy

    else:
        lst_df_renamed=lst_df_all
    return lst_df_renamed;


def getFileDataStore():
    return lst_df_renamed;
    
    
    
def mergingRecords(csvlist,printdebug=0):
    recordlist=dict()
    for filepath in csvlist:
        if printdebug>0: print("[] Merging:",filepath, flush=True)
        for idx,row in csvlist[filepath].iterrows():
            rowdict = row.to_dict()
            id = 0
            if "IR_ID" in rowdict:
                id=(int)(rowdict["IR_ID"])
            if id>0:
                if id not in recordlist:
                    recordlist[id] = rowdict
                else:
                    for col in rowdict:
                        if col not in recordlist[id]:
                            recordlist[id][col] = rowdict[col]
                    #print(recordlist[id])
            else:
                if printdebug>0: print("\t!!Row has no IR_ID!",rowdict, flush=True)
    
                
    return recordlist
    
def printMeta(recordlist, filter=dict()):
    TypeDict = dict()
    RoadDict = dict()
    for recordid in recordlist:
        recordcopy = recordlist[recordid]
        if len(filter)>0:
            skip = 0
            for key in filter:
                if key not in recordcopy:
                     skip = 1
                     break;                    
                elif type(filter[key])==list and recordcopy[key] not in filter[key]:
                     skip = 1
                     break;
                elif recordcopy[key] != filter[key]:
                     skip = 1
                     break;
            if skip>0:
                continue;
        
        if "TYPE" in recordcopy:
            rtype=recordcopy["TYPE"]
            if type(rtype) != str or len(rtype)==0:
                rtype="UNKNOWN"
            if rtype in TypeDict:
                TypeDict[rtype]=TypeDict[rtype]+1
            else:
                TypeDict[rtype]=1
        if "ROAD_NAME" in recordcopy:
            rtype=recordcopy["ROAD_NAME"]
            if type(rtype) != str or len(rtype)==0:
                rtype="UNKNOWN"
            if rtype in RoadDict:
                RoadDict[rtype]=RoadDict[rtype]+1
            else:
                RoadDict[rtype]=1
    print("TypeDict",TypeDict)
    print("RoadDict",RoadDict)
    
                
        
    
        
    
def convertRecordstoDocList(recordlist,printdebug=0,doclist=dict()):
    
    from langchain_core.documents import Document
    for recordid in recordlist:
      if recordid not in doclist:
            recordcopy = recordlist[recordid]
            recordmeta={}
            if "IR_ID" in recordcopy:
                del recordcopy["IR_ID"]
            if "TYPE" in recordcopy:
                recordmeta["TYPE"]=recordcopy["TYPE"]
                del recordcopy["TYPE"]
            if "ROAD_NAME" in recordcopy:
                recordmeta["ROAD_NAME"]=recordcopy["ROAD_NAME"]
            if "LOC_TYPE" in recordcopy:
                recordmeta["LOC_TYPE"]=recordcopy["LOC_TYPE"]
            if "LOC_CODE" in recordcopy:
                recordmeta["LOC_CODE"]=recordcopy["LOC_CODE"]
                
                
                
                
                
            doclist[recordid] = Document(
                    id=recordid,
                    page_content=(str)(recordcopy),
                    metadata=recordmeta
                )

    
                
    return doclist
    
    
    
    
if __name__ == "__main__":
    print("Running Default Main for load_data.py")
    loadfiles(printdebug=1);
