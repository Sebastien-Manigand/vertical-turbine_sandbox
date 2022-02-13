# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET


def getProfiles(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    profiles = []
    for i in range(len(root)):
        if not root[i][1].text in profiles:
            profiles.append(root[i][1].text)
    return profiles




def readHeliciel(filename, profile, Re = 5e4):
    
    tree = ET.parse(filename)
    root = tree.getroot()
    profiles = []
    ReList = []
    
    # print("\nList of the profiles:")
    for i in range(len(root)):
        # print("{0:15}  Re= {1:5.1e}".format(root[i][1].text, float(root[i][5].text)))
        if not root[i][1].text in profiles:
            profiles.append(root[i][1].text)
        if not float(root[i][5].text) in ReList:
            ReList.append(float(root[i][5].text))
            
    if not profile in profiles:
        print("Foiler profile {0} not in the file...".format(profile))
        return -1
    else:
        if not Re in ReList:
            print("Re number not listed...")
            return -1
        
    for i in range(len(root)):
        if root[i][1].text == profile and float(root[i][5].text) == Re:
            ang = np.array(root[i][4].text.split(';')[:-1], dtype=int)
            cl = np.array(root[i][6].text.replace(',', '.').split(';')[:-1], dtype=float)
            cd = np.array(root[i][7].text.replace(',', '.').split(';')[:-1], dtype=float)
            cm = np.array(root[i][8].text.replace(',', '.').split(';')[:-1], dtype=float)
            xy = np.array(root[i][3].text.replace(',', '.').split(';')[:-1], dtype=float)
            break
        
    x = np.array([xy[2*i] for i in range(len(xy)//2)], dtype=float)
    y = np.array([xy[2*i+1] for i in range(len(xy)//2)], dtype=float)
    
    
    return ang, cl, cd, cm, x, y
