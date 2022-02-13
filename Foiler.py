# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 08:39:35 2020

@author: sebas
"""

import os, sys
import numpy as np
# from xmlHandling import *
import xml.etree.ElementTree as ET


class Foiler():
    
    def __init__(self, dbFilename):
        self.dbFilename = dbFilename
        if not os.path.exists(self.dbFilename):
            print("Database file not found, \nplease check the location of the file, which has to be in the root directory of the program")
            sys.exit(-1)
        self.profileLoaded = False
        self.profiles = []
        self.root = ET.parse(self.dbFilename).getroot()
        self.rho = 1.292 # kg.m-3
        self.angle = None
        self.cl = None
        self.cd = None
        self.cm = None
        self.x = None
        self.y = None
        
        self.getProfileList()
        
        
    def getProfileList(self):
        self.fl_profiles = []
        self.fl_Re = {}
        self.fl_Re_rootId = {} # id of the datarow in self.root corresponding to the foiler and the Reynolds number wanted
        
        # tree = ET.parse(self.dbFilename)
        # root = tree.getroot()
        for i in range(len(self.root)):
            if not self.root[i][1].text in self.fl_profiles:
                self.fl_profiles.append(self.root[i][1].text)
                self.fl_Re[self.root[i][1].text] = []
                self.fl_Re_rootId[self.root[i][1].text] = []
            if not int(self.root[i][5].text) in self.fl_Re[self.root[i][1].text]:
                self.fl_Re[self.root[i][1].text].append(int(self.root[i][5].text))
                self.fl_Re_rootId[self.root[i][1].text].append(i)
        return self.fl_profiles
                
    
    def loadProfile(self, pName):
        if not pName in self.fl_profiles:
            print("Profile wanted not in the loaded list...")
            sys.exit(-1)
        self.profileLoaded = True
        i = self.fl_Re_rootId[pName][0]
        a = self.root[i][4].text.split(';')[:-1]
        self.angle = np.array(np.array(a + ['360'], dtype=int), dtype=float)
        a = self.root[i][6].text.replace(',', '.').split(';')[:-1]
        self.cl = np.array(a + [a[0]], dtype=float)
        a = self.root[i][7].text.replace(',', '.').split(';')[:-1]
        self.cd = np.array(a + [a[0]], dtype=float)
        a = self.root[i][8].text.replace(',', '.').split(';')[:-1]
        self.cm = np.array(a + [a[0]], dtype=float)
        xy = np.array(self.root[i][3].text.replace(',', '.').split(';')[:-1], dtype=float)
        
        self.x = np.array([xy[2*i] for i in range(len(xy)//2)], dtype=float)
        self.y = np.array([xy[2*i+1] for i in range(len(xy)//2)], dtype=float)
    
        # return ang, cl, cd, cm, x, y
        return self.x, self.y
    
    
    def computeLiftDrag(self, ang, veffx, veffy, turbineAngle, turbineRadius):
        x = self.x * np.cos(-ang/180*np.pi) - self.y * np.sin(-ang/180*np.pi)
        y = self.y * np.cos(-ang/180*np.pi) + self.x * np.sin(-ang/180*np.pi)
        S = (max(y) - min(y)) * 1.0
        veff = np.sqrt(veffx**2 + veffy**2)
        
        # evx = -veffx/veff
        # evy = -veffy/veff
        evx = np.cos((-ang+turbineAngle-90)/180*np.pi)
        evy = np.sin((-ang+turbineAngle-90)/180*np.pi)
        ewx = np.cos((-ang+turbineAngle)/180*np.pi)
        ewy = np.sin((-ang+turbineAngle)/180*np.pi)
        etx = np.cos(turbineAngle/180*np.pi)
        ety = np.sin(turbineAngle/180*np.pi)
        
        # print('foiler eval at angle {0:.1f}'.format(ang%360))
        # print(self.angle)
        # print(self.cl)
        Cz = np.interp((ang%360), self.angle, self.cl)
        Cx = np.interp((ang%360), self.angle, self.cd)
        # print('       Cz = {0:2f}       Cx = {1:.2f}'.format(Cz, Cx))
        
        
        fL = self.rho * veff**2 / 2 * S * Cz
        fD = self.rho * veff**2 / 2 * S * Cx
        
        ML = turbineRadius * fL * (etx*ewy - ety*ewx)
        MD = turbineRadius * fD * (etx*evy - ety*evx)
        
        return fL, fD, ML + MD, S, Cz, Cx
        
    
    def arctan(self, X, Y):
        '''
        return the angle of the vector (X, Y) in the direct orthogonal system.
        angle = arctan(Y/X)
        '''
        a = 0.0
        if X != 0:
            if X >= 0:
                a = np.arctan(Y/X)
            else:
                a = np.arctan(Y/X) + np.pi
        else:
            if Y >= 0:
                a = np.pi/2
            else:
                a = -np.pi/2
        return a