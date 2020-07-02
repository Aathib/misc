# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 11:46:58 2020
"""

from __future__ import print_function
from itertools import chain, islice, repeat
import pandas as pd
import os

def metadata(path):
    cwd = os.getcwd()
    NaN = pd.np.NaN
    data_file = path
    
    class MetaData():
        PERCENTILES = (1,5,10,20,25,40,50,60,75,80,90,95,99)
        def __init__(self,pos):
            self.Position = pos
            self.Name = None
            self.Type = None
            self.Count = 0
            self.CountDistinct = 0
            self.DistTotalCounts = 0
            self.TypeofDimension = None
            self.Unique = False
            self.Nullable = False
            self.Primary = False
            self.Top10Counts = []
            self.Top10Values = []
        @staticmethod
        def csv_cols():
            return 'Position,Name,Type,Count,CountDistinct,DistTotalCounts, TypeofDimension,Is-Unique,Is-Nullable, Is-Primary,' + \
        '{},{}'.format(','.join('Top{}'.format(n) for n in range(1,11)),
                       ','.join('Count-Top{}'.format(n) for n in range(1,11)))
        
        def csv_row(self):
            return ','.join(str(s) for s in [
                self.Position,self.Name,self.Type,self.Count,self.CountDistinct,self.DistTotalCounts,self.TypeofDimension,\
                    self.Unique,self.Nullable,self.Primary,\
                        ','.join(str(n) for n in islice(chain(self.Top10Values, repeat(NaN,10)),10)),
                        ','.join(str(n) for n in islice(chain(self.Top10Counts, repeat(NaN,10)),10))
                        ])
    col = MetaData.csv_cols().split(',')
    print(len(col))
    df2 = pd.DataFrame([],columns = col)
    df = pd.read_csv(filepath_or_buffer = data_file, header = 0, nrows = 5)
    i = 0
    s = []
    for c in range(df.shape[1]):
        md = MetaData(pos = c)
        sr = pd.read_csv(filepath_or_buffer = data_file, usecols = [c], header = 0, squeeze= True, skip_blank_lines=False)
        # if sr.dtype.name =='object':
        #     sr = sr.map(lambda v: len(v) if isinstance(v,str) else 0)
        # elif sr.dtype.name == 'bool':
        #     sr = sr.map(lambda v: 1 if (isinstance(v,bool) and v) else 0)
        uv = sr.value_counts()
        md.name = sr.dtype.name
        md.Count = len(sr)
        md.CountDistinct = len(uv)
        md.DistTotalCounts = len(uv)/len(sr)
        if md.CountDistinct < 50 and md.DistTotalCounts < 0.20:
            md.TypeofDimension = 'Categorical'
        elif md.CountDistinct > 50 and md.DistTotalCounts < 0.20:
            md.TypeofDimension = 'Reference'
        else:
            md.TypeofDimension = 'Open'
        md.Unique = sr.is_unique
        md.Nullable = sr.hasnans
        md.Primary = not md.Nullable and (md.Count == md.CountDistinct)
        md.Top10Counts = sr.value_counts().head(n=10).values.tolist()
        x = []
        for j in sr.value_counts().head(n=10).keys().tolist():
            try:
                m =j.replace(',','')
                x.append(m)
            except:
                x.append(j)
        md.Top10Values = x
        print(md.csv_row())
        s = md.csv_row().split(',')
        print(s)
        print(md.Top10Values)
        print(len(s))
        df2.loc[i] = s
        i = i+1
        s = []        
    df2.to_csv(cwd + "_Metadata.csv")

metadata(r"file.csv")
