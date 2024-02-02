#Mitchell Lab, 2024
#Written by Max Libmann - libmannm@oregonstate.edu
#Coordinated by Kaiyo Shi - shik@ohsu.edu

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class PreProcess():
    def __init__(self, filePath, sheetNo, cols):
        self.returnList = ["df", "data", "DataLoss"]
        xL = pd.ExcelFile(filePath)
        sheetName = xL.sheet_names[sheetNo]
        self.sheetTitle = xL.sheet_names[sheetNo]
        self.df = pd.read_excel(filePath, usecols= cols, sheet_name = sheetName)
        c = ["ET_PupilLeft","ET_PupilRight"]
        inter = self.df[c]
        self.data = inter.to_numpy()
        self.preNaNCount = np.count_nonzero(np.isnan(self.data))
        self.numPoints = np.shape(self.data[:])[0]
        inter = self.df["Timestamp"]
        self.timeArray = inter.to_numpy()
        
        
        self.lrMerge() #Fills in each column with data from the other and then merges the two pupils into a 1d array
        self.outliers() #Adds any outliers to the very important self.NaNIndex
        self.crop() #Turns every value pointed to by self.NaNIndex into np.nan for future interpolation
        self.blinkOnOff() #Defines what qualifies as a blink and notes where they are in a variety of ways
        self.monotonic() #monotonically filters the beginning and ends of the blinks in a form of noise based filtering
        self.crop()
        self.df.insert(loc = 5, column='Pupil', value=self.data)
        #self.df["Pupil"] = self.data
        self.df["Pupil"] = self.df["Pupil"].interpolate(method = "pchip") #pchip was qualitatively the best and most consistent
        self.df = self.df.drop(["ET_PupilLeft","ET_PupilRight"], axis=1)
        self.gazeAOI()
        
        
        
    def outliers(self):
        #Creates an upper and lower fence and designates anything outside them as being an outlier via the NaNIndex
        #Uses IQR because why not?
        quantile = np.nanquantile(self.data, [0,0.25,0.5,0.75,1])
        IQR = quantile[3]-quantile[1]
        self.uFence = quantile[3]+2.5*IQR
        self.lFence = quantile[1]-2.5*IQR
        self.NaNIndex = []
        for j in range(self.numPoints):
            if self.data[j] < self.lFence:
                self.NaNIndex.append(j)
            elif self.data[j] > self.uFence:
                self.NaNIndex.append(j)

    def blinkOnOff(self):
        self.OnBlink = []
        self.OffBlink = []
        self.blinkIndex = []
        self.k = self.NaNIndex[0]-1 #Just a starting value
        self.counter = 0
        
        for j in self.NaNIndex:
            #go through each NaN value, if it is consecutive, then increase the current value. If not, append the old value to self.blinkIndex and set the counter to 0
            if (j-self.k)==1:
                self.counter += 1
            else:
                self.blinkIndex.append(self.counter+1)
                self.counter = 0
            self.k = j
        self.blinkIndex[0] = self.blinkIndex[0]-1 #accounts for autostarting the first value (self.k)   
        
        self.i = 0
        self.blinkIndexCu = []
        for j in self.blinkIndex:
            #creates values of the cumulative starting points of each consecutive period of NaN Values, which is used for locating
            self.i += j
            self.blinkIndexCu.append(self.i)
        self.blinkIndexCu.insert(0,0) #allows to be 0 indexed
        
        for j,k in enumerate(self.blinkIndex):
            # if NaN values last for between ~45 and ~500 ms, their start and end point indeces are recorded
            if k > 9 and k<100:
                self.OnBlink.append(self.NaNIndex[k]-1)
                self.OffBlink.append(self.NaNIndex[self.blinkIndexCu[j+1]-1]+1)

    def monoCompare(self,first,second):
        if first > self.data[second]:
            return False
        else:
            return True

    def monotonic(self):
        #dending on on or offset, it goes back until it finds a value that isnt NaN and is larger or smaller than the initial on or offset
        #onsets
        for j in range(len(self.OnBlink)):    
            ind = self.OnBlink[j]
            indP = self.data[ind]
            while self.monoCompare(indP,ind-1):
                self.data[ind] = np.nan
                ind = ind - 1
                indP = self.data[ind]
            self.OnBlink[j] = ind
        
        #offsets
        for j in range(len(self.OffBlink)):
            ind = self.OffBlink[j]
            indP = self.data[ind]
            while self.monoCompare(indP, ind+1):
                self.data[ind] = np.nan
                ind += 1
                indP = self.data[ind]
            self.OffBlink[j] = ind
            
    def crop(self):
        #crops to np.nan 
        for j in self.NaNIndex:
            self.data[j] = np.nan
    
    def NaNTest(self, inVal):
        #catches NaNs, which are missed by normal comparisons
        if np.isnan(inVal) or inVal < 0:
            return True
        else:
            return False
    
    def lrMerge(self):
        #when there is an asymmetric NaN, it finds the delta between the valid side and the last valid data point and applies it to itself
        for i in range(len(self.data)):
            if self.data[i,0] > 0 and self.NaNTest(self.data[i,1]) == True:
                j = 1
                while self.NaNTest(self.data[i-j,1])==True or self.NaNTest(self.data[i-j,0])==True:
                    j += 1
                change = self.data[i,0] - self.data[i-j,0] 
                self.data[i,1] = self.data[i-j,1] + change
            elif self.data[i,1] > 0 and self.NaNTest(self.data[i,0]) == True:
                j = 1
                while self.NaNTest(self.data[i-j,1])==True or self.NaNTest(self.data[i-j,0])==True:
                    j += 1
                change = self.data[i,1] - self.data[i-j,1] 
                self.data[i,0] = self.data[i-j,0] + change
        
        self.data = np.mean(self.data, axis = 1) #turns self.data from a 2d array for 2 pupils into a 1d array for one average
    
    def AOIL(self, x, y):
        t = True
        if x > 820 or x < 200:
            t = False
        if y > 750 or y < 330:
            t = False
        return(t)
    
    def AOIR(self, x, y):
        t = True
        if x > 1720 or x < 1100:
            t = False
        if y > 750 or y < 330:
            t = False
        return(t)
    
    def gazeAOI(self):
        c = ["Interpolated Gaze X","Interpolated Gaze Y"]
        intermediate = self.df[c].to_numpy()
        expLR = np.zeros(len(intermediate))
        for i,j in enumerate(intermediate):
            if np.isnan(j[0]) or np.isnan(j[1]):
                expLR[i] = -1
            else:
                if self.AOIL(j[0],j[1]):
                    expLR[i] = 1 #Left
                elif self.AOIR(j[0],j[1]):
                    expLR[i] = 2 #Right
                else:
                    expLR[i] = 0 #Neither
        self.df = self.df.drop(c, axis=1)
        #self.df["GazeLoc"] = expLR
        self.df.insert(loc = 6, column='GazeLoc', value= expLR)
        
    def returner(self, i):
        if i == 0:
            return(self.df)
        elif i == 1:
            return(self.data)
    
    def sheetName(self):
        return(self.sheetTitle)


class Analysis():
    def __init__(self, bpath, excelInput = False, data = None):
        if excelInput == False:
            self.data = data
        elif excelInput == True:
            print("NOT YET")#Might not do it lol
        
        
        self.baselrMerge(bpath,0)
        self.ffbaselineTrialIndex()
        self.trialIndex() #Finds the start points of every trial
        
        self.dilate() #finds the average of the first 200 data points (~1 sec) and makes the other data points relative to it
        self.click() #Creates a list of every click
        self.classify() #Categorizes each click as submit, left, or right, via a 0,1,2 system
        
        #Turns seperate lists into a 2D array for all the interaction data
        self.finalClassified = np.column_stack((np.asarray(self.classifiedTrial),np.asarray(self.clickIndex),np.asarray(self.classified)))

        print("0 is submit, 1 is left, 2 is right")
        
    def NaNTest(self, inVal):
        #catches NaNs, which are missed by normal comparisons
        if np.isnan(inVal) or inVal < 0:
            return True
        else:
            return False
    
    def baseMean(self, trialNum):
        if trialNum == 0:
            begin = self.trialIndex[trialNum]
            begin = self.data["iMotionsRow"][begin]
            series = np.arange(begin-200,begin,1)
            c = 0
            d = 0
            for i in series:
                if self.baselineArray[i,3]*0 == 0:
                    c += 1
                    d += self.baselineArray[i,3]
            ave = d/c
            return(ave)
        else:
            begin = self.baselineTrialIndex[trialNum]
            end = self.baselineTrialIndex[trialNum+1]
            series = self.baselineArray[begin:end,-1]
            ave = np.nanmean(series)
            return(ave)
            
    def ffbaselineTrialIndex(self):
        inter = -1
        self.baselineTrialIndex = []
        for i,j in enumerate(self.baselinedf["Trial"]):
            if inter != j:
                inter = j
                self.baselineTrialIndex.append(i)
        #print(self.baselineTrialIndex)
        #print(len(self.baselineTrialIndex))
        
    def trialIndex(self):
        #looks for changes in the provided "Trial" Column and notes the index
        inter = -1
        self.trialIndex = []
        for i,j in enumerate(self.data["Trial"]):
            if inter != j:
                inter = j
                self.trialIndex.append(i)
                
    def dilate(self, time = 200):
        #sets all data points [200:] to be relative to mean of [:200], [:200] is set to said mean
        inter = self.data["Pupil"]
        self.pupil = inter.to_numpy()
        self.dilated = np.zeros_like(self.pupil)
        self.locMean = 0
    
        self.locMeanList = []
        #print(len(self.trialIndex))
        for i,j in enumerate(self.trialIndex):
            #self.locMean = np.mean(self.pupil[j:j+200])
            #self.dilated[j:j+200] = self.locMean
            #print(i)
            self.locMean = self.baseMean(i)
            self.locMeanList.append(self.locMean)
            try:
                end = self.trialIndex[i+1]
            except:
                end = len(self.pupil)
            for k in range(j, end):
                self.dilated[k] = self.pupil[k] - self.locMean
        
        #print(self.locMeanList)        
        #self.data["Dilated"] = self.dilated #adds this to a new column in the original dataframe
        self.data.insert(loc = 5, column='Dilated', value=self.dilated)
        
    def click(self):
        #finds indeces of everytime the mouse is clicked
        self.inter = self.data["Data"]
        self.clickData = self.inter.to_numpy()
        self.clickData2 = np.zeros_like(self.clickData)
        self.clickIndex = []
        for i,j in enumerate(self.clickData):
            self.ih = j
            if type(self.ih) == str:
                if "LBUTTONDOWN" in self.ih:
                    self.clickData2[i] = j
                    self.clickIndex.append(i)
    
    def classify(self):
        self.classified = []
        self.classifiedTrial = []
        #0 is index, 1 is raw, 2 is x, 3 is y, 4 is category
        for i,j in enumerate(self.clickIndex):
            self.cd = self.clickData2[j]
            self.x = int(self.cd[7:self.cd.index(";Y:")])
            self.y = int(self.cd[self.cd.index(";Y:")+3:self.cd.index(";Mouse")])
            #0 is submit, 1 is left, 2 is right!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if self.y > 787 and self.y < 1041 and self.x > 659 and self.x<1338:
                self.classified.append(0)
            elif self.x > 199 and self.y > 327 and self.x < 821 and self.y < 751:
                self.classified.append(1)
            elif self.x > 1099 and self.y > 329 and self.x < 1723 and self.y <751:
                self.classified.append(2)
            else:
                self.classified.append(3)
            self.classifiedTrial.append(self.data["Trial"][j]-1)
    
    def baselrMerge(self, basePath, sheetNo):
        xL = pd.ExcelFile(basePath)
        sheetName = xL.sheet_names[sheetNo]
        self.baselinedf = pd.read_excel(basePath, usecols= [0,1,22,23,57], sheet_name = sheetName)
        
        c = ["ET_PupilLeft","ET_PupilRight"]
        inter = self.baselinedf[c]
        self.baseArray = inter.to_numpy()
        
        for i in range(len(self.baseArray)):
            if self.baseArray[i,0] > 0 and self.NaNTest(self.baseArray[i,1]) == True:
                j = 1
                while self.NaNTest(self.baseArray[i-j,1])==True or self.NaNTest(self.baseArray[i-j,0])==True:
                    j += 1
                change = self.baseArray[i,0] - self.baseArray[i-j,0] 
                self.baseArray[i,1] = self.baseArray[i-j,1] + change
            elif self.baseArray[i,1] > 0 and self.NaNTest(self.baseArray[i,0]) == True:
                j = 1
                while self.NaNTest(self.baseArray[i-j,1])==True or self.NaNTest(self.baseArray[i-j,0])==True:
                    j += 1
                change = self.baseArray[i,1] - self.baseArray[i-j,1] 
                self.baseArray[i,0] = self.baseArray[i-j,0] + change
        
        self.baseArray = np.mean(self.baseArray, axis = 1) #turns self.data from a 2d array for 2 pupils into a 1d array for one average
        
        for i,j in enumerate(self.baseArray):
            if j == -1 or j*0 != 0:
                self.baseArray[i] = np.nan
        
        self.baselinedf = self.baselinedf.drop(["ET_PupilLeft","ET_PupilRight"], axis=1)
        
        self.baselinedf["Pupil"] = self.baseArray
        self.baselineArray = self.baselinedf.to_numpy()
        
        global baselinedf
        baselinedf = self.baselinedf
        
    
    def retInputs(self):
        return self.finalClassified
    
    def retTable(self):
        return self.data
    
    def retIndex(self):
        return self.trialIndex
    
    def baseret(self):
        return(self.baselinedf)
    
    def retMeanList(self):
        return(self.locMeanList)


def exporter(data, trialIndex, blinkLocs, fName, sName, export = False):
    exportFrame = data
    tIndex = np.zeros(len(data)) #data has to be filled in w/ 0s to be the same length
    tIndex[:len(trialIndex)] = trialIndex
    exportFrame.insert(loc = 9, column='TrialIndex', value=tIndex)
    Blinks = np.zeros((len(data),3))
    Blinks[:len(blinkLocs),:] = blinkLocs
    exportFrame.insert(loc = 10, column='BlinkTrial', value=Blinks[:,0])
    exportFrame.insert(loc = 11, column='ClickIndex', value=Blinks[:,1])
    exportFrame.insert(loc = 12, column='InputType', value=Blinks[:,2])
    if export == True:
        outName = fName + ".xlsx"
        try:
            with pd.ExcelWriter(outName, mode = "a", engine="openpyxl") as writer:  
                exportFrame.to_excel(writer, sheet_name= sName, index = False)
        except:
            with pd.ExcelWriter(outName) as writer:  
                exportFrame.to_excel(writer, sheet_name= sName, index = False)
    return(exportFrame)