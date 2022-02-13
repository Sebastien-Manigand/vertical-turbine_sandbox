# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 10:51:12 2020

@author: sebas
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import numpy as np
#from xmlHandling import *
from Foiler import *
import pathlib
import time

import matplotlib
matplotlib.rcParams['font.family'] = 'serif'



class AppliCanevas(tk.Tk):
    
    def __init__(self):
        self.running = False
        self.DEBUGGING = True
        self.TEST_PROFILELIST = ["profile1", "profile2", "profile3", "profile4", "profile5"]
        self.TEST_PROFILE = np.array([[0.5, 0.0],
                             [0.4, 0.1],
                             [-0.5, 0.0],
                             [0.4, -0.1]])
        self.CANVCOLOR_BLADE = ['#FFCCCC', '#CCFFCC', '#CCCCFF']
        self.OUTPUT_NAME = 'turbine-output'
        self.output_dir = str(pathlib.Path().absolute())
        
        tk.Tk.__init__(self)
        self.width = 840
        self.height = 640
        
        self.turbineAngle = 0.0 # in degree
        self.turbineRadius = 1.0 # in meter
        self.bladeSize = 0.5 # in meter
        self.bladeTilt = 0.0 # in degree
        self.turbSpeed = 0.0 # in rpm
        self.windSpeed = 1.0 # in m.s-1
        
        self.gridAngle_num = 72
        self.gridAngle_beg = 0.0 # degree
        self.gridAngle_end = 360.0 # degree
        self.gridWind_num = 10
        self.gridWind_beg = 1.0 # m.s-1
        self.gridWind_end = 10.0 # m.s-1
        self.gridTurbine_num = 10
        self.gridTurbine_beg = 10.0 # r.p.m.
        self.gridTurbine_end = 100.0 # r.p.m.
        self.gridTilt_num = 11
        self.gridTilt_beg = -25.0 # degree
        self.gridTilt_end = 25.0 # degree
        
        self.gridAngle = []
        self.gridModel = []
        self.gridModelLen = 1
        self.gridAng_i = 0
        self.gridMod_i = 0
        
        # geometrical parameters (angle and speed in the air flux) of each blade
        self.veffx1 = 0.0
        self.veffx2 = 0.0
        self.veffx3 = 0.0
        self.veffy1 = 0.0
        self.veffy2 = 0.0
        self.veffy3 = 0.0
        self.theta1 = 0.0
        self.theta2 = 0.0
        self.theta3 = 0.0
        
        # results variables
        self.fL1, self.fD1, self.M1, self.S1 = 0, 0, 0, 0
        self.fL2, self.fD2, self.M2, self.S2 = 0, 0, 0, 0
        self.fL3, self.fD3, self.M3, self.S3 = 0, 0, 0, 0
        
        
        self.plotX = []
        self.plotY = []
        self.outputCurMod = [[], [], [], [], [], []]
        self.output_allSteps = False
        self.RUNNING_INTERVAL = 5
        
        
        self.foilerHandler = Foiler("naca_heliciel3.xml")
        self.PROFILELIST = self.foilerHandler.getProfileList()
        self.PROFILE = np.array([[], []])
        self.bProfile = 'naca2415' #self.PROFILELIST[13]
        self.setProfile(self.bProfile)
        
        self.create_widgets()
        
        self.geoBlade()
        self.drawMonitor()
        
        


    def create_widgets(self):
        # création canevas
        self.canv = tk.Canvas(self, bg="#EEEEFF", borderwidth=1, height=self.height, width=self.width)
        self.canv.config(borderwidth=1)
        self.canv.pack(side=tk.LEFT)
        
        self.settingPanel = tk.Frame(self)
        self.settingPanel_title = tk.Label(self.settingPanel, text="Simulation options")
        self.settingPanel_title.pack(side=tk.TOP)
        
        
        self.geometryPanel = tk.LabelFrame(self.settingPanel, text="Geometry", padx=2, pady=2)
        
        self.gP_profileFrame = tk.Frame(self.geometryPanel)
        self.gP_pF_title = tk.Label(self.gP_profileFrame, text="Profile")
        self.gP_pF_title.pack(side=tk.LEFT)
        self.gP_pF_profileList = ttk.Combobox(self.gP_profileFrame, values=self.PROFILELIST)
        self.gP_pF_profileList.current(self.PROFILELIST.index(self.bProfile))
        self.gP_pF_profileList.bind("<<ComboboxSelected>>", self.chooseProfile)
        self.gP_pF_profileList.pack(side=tk.RIGHT)
        self.gP_profileFrame.pack(side=tk.TOP, fill=tk.X)
        
        self.gP_tRadiusFrame = tk.Frame(self.geometryPanel)
        self.gP_trF_title = tk.Label(self.gP_tRadiusFrame, text="Turbine radius (m)")
        self.gP_trF_title.pack(side=tk.LEFT)
        self.var_tRadius = tk.DoubleVar()
        self.var_tRadius.set(self.turbineRadius)
        self.gP_trF_box = tk.Spinbox(self.gP_tRadiusFrame, textvariable=self.var_tRadius, from_=0.1, to=10.0, increment=0.1, command=self.set_tRadius)
        self.gP_trF_box.bind("<Return>", self.set_tRadius)
        self.gP_trF_box.pack(side=tk.RIGHT)
        self.gP_tRadiusFrame.pack(side=tk.TOP, fill=tk.X)
        
        self.gP_bSizeFrame = tk.Frame(self.geometryPanel)
        self.gP_bsF_title = tk.Label(self.gP_bSizeFrame, text="Blade size (m)")
        self.gP_bsF_title.pack(side=tk.LEFT)
        self.var_bSize = tk.DoubleVar()
        self.var_bSize.set(self.bladeSize)
        self.gP_bsF_box = tk.Spinbox(self.gP_bSizeFrame, textvariable=self.var_bSize, from_=0.05, to=3.0, increment=0.05, command=self.set_bSize)
        self.gP_bsF_box.bind("<Return>", self.set_bSize)
        self.gP_bsF_box.pack(side=tk.RIGHT)
        self.gP_bSizeFrame.pack(side=tk.TOP, fill=tk.X)
        
        self.gP_bTiltFrame = tk.Frame(self.geometryPanel)
        self.gP_btF_title = tk.Label(self.gP_bTiltFrame, text="Blade tilt (deg)")
        self.gP_btF_title.pack(side=tk.LEFT)
        self.var_bTilt = tk.DoubleVar()
        self.var_bTilt.set(self.bladeTilt)
        self.gP_btF_box = tk.Spinbox(self.gP_bTiltFrame, textvariable=self.var_bTilt, from_=-60.0, to=60.0, increment=1.0, command=self.set_bTilt)
        self.gP_btF_box.bind("<Return>", self.set_bTilt)
        self.gP_btF_box.pack(side=tk.RIGHT)
        self.gP_bTiltFrame.pack(side=tk.TOP, fill=tk.X)
        
        self.gP_wSpeedFrame = tk.Frame(self.geometryPanel)
        self.gP_wsF_title = tk.Label(self.gP_wSpeedFrame, text="Wind speed (m.s-1)")
        self.gP_wsF_title.pack(side=tk.LEFT)
        self.var_wSpeed = tk.DoubleVar()
        self.var_wSpeed.set(self.windSpeed)
        self.gP_wsF_box = tk.Spinbox(self.gP_wSpeedFrame, textvariable=self.var_wSpeed, from_=0.0, to=50.0, increment=0.1, command=self.set_wSpeed)
        self.gP_wsF_box.bind("<Return>", self.set_wSpeed)
        self.gP_wsF_box.pack(side=tk.RIGHT)
        self.gP_wSpeedFrame.pack(side=tk.TOP, fill=tk.X)
        
        self.gP_tSpeedFrame = tk.Frame(self.geometryPanel)
        self.gP_tsF_title = tk.Label(self.gP_tSpeedFrame, text="Turbine speed (rpm)")
        self.gP_tsF_title.pack(side=tk.LEFT)
        self.var_tSpeed = tk.DoubleVar()
        self.var_tSpeed.set(self.turbSpeed)
        self.gP_tsF_box = tk.Spinbox(self.gP_tSpeedFrame, textvariable=self.var_tSpeed, from_=-300.0, to=300.0, increment=5.0, command=self.set_tSpeed)
        self.gP_tsF_box.bind("<Return>", self.set_tSpeed)
        self.gP_tsF_box.pack(side=tk.RIGHT)
        self.gP_tSpeedFrame.pack(side=tk.TOP, fill=tk.X)
        
        self.geometryPanel.pack(side=tk.TOP)
        
        
        self.allSteps_enabled = tk.BooleanVar()
        self.windGrid_enabled = tk.BooleanVar()
        self.turbGrid_enabled = tk.BooleanVar()
        self.tiltGrid_enabled = tk.BooleanVar()
        self.allSteps_enabled.set(self.output_allSteps)
        self.windGrid_enabled.set(False)
        self.turbGrid_enabled.set(False)
        self.tiltGrid_enabled.set(False)
        
        
        self.gridsPanel = tk.LabelFrame(self.settingPanel, text="Grids", padx=2, pady=2)
        
        self.gsP_agTFrame = tk.Frame(self.gridsPanel)
        self.var_gridAngle_beg = tk.StringVar(value=str(self.gridAngle_beg))
        self.var_gridAngle_end = tk.StringVar(value=str(self.gridAngle_end))
        self.var_gridAngle_num = tk.StringVar(value=str(self.gridAngle_num))
        self.gsP_agLabel = tk.Label(self.gsP_agTFrame, text="Angle grid")
        self.gsP_agLabel.pack(side=tk.LEFT)
        self.gsP_agButton = tk.Checkbutton(self.gsP_agTFrame, text='show all steps?', var = self.allSteps_enabled, command=self.toggle_allSteps) 
        self.gsP_agButton.deselect()
        self.gsP_agButton.pack(side=tk.RIGHT)
        self.gsP_agTFrame.pack(side=tk.TOP, fill=tk.X)
        self.gsP_agTFrame = tk.Frame(self.gridsPanel)
        self.gsP_agEntry_min = tk.Entry(self.gsP_agTFrame, width=20, textvariable=self.var_gridAngle_beg)
        self.gsP_agEntry_min.pack(side=tk.RIGHT)
        self.gsP_agLabel_min = tk.Label(self.gsP_agTFrame, text="    min (deg):")
        self.gsP_agLabel_min.pack(side=tk.RIGHT)
        self.gsP_agTFrame.pack(side=tk.TOP, fill=tk.X)
        self.gsP_agTFrame = tk.Frame(self.gridsPanel)
        self.gsP_agEntry_max = tk.Entry(self.gsP_agTFrame, width=20, textvariable=self.var_gridAngle_end)
        self.gsP_agEntry_max.pack(side=tk.RIGHT)
        self.gsP_agLabel_max = tk.Label(self.gsP_agTFrame, text="    max (deg):")
        self.gsP_agLabel_max.pack(side=tk.RIGHT)
        self.gsP_agTFrame.pack(side=tk.TOP, fill=tk.X)
        self.gsP_agTFrame = tk.Frame(self.gridsPanel)
        self.gsP_agEntry_num = tk.Entry(self.gsP_agTFrame, width=20, textvariable=self.var_gridAngle_num)
        self.gsP_agEntry_num.pack(side=tk.RIGHT)
        self.gsP_agLabel_num = tk.Label(self.gsP_agTFrame, text="    num:")
        self.gsP_agLabel_num.pack(side=tk.RIGHT)
        self.gsP_agTFrame.pack(side=tk.TOP, fill=tk.X)
        self.gsP_agEntry_min.bind('<Return>', self.set_gridAngle_beg)
        self.gsP_agEntry_max.bind('<Return>', self.set_gridAngle_end)
        self.gsP_agEntry_num.bind('<Return>', self.set_gridAngle_num)
        
        
        self.gsP_wgTFrame = tk.Frame(self.gridsPanel)
        self.var_gridWind_beg = tk.StringVar(value=str(self.gridWind_beg))
        self.var_gridWind_end = tk.StringVar(value=str(self.gridWind_end))
        self.var_gridWind_num = tk.StringVar(value=str(self.gridWind_num))
        self.gsP_wgButton = tk.Checkbutton(self.gsP_wgTFrame, text='Wind grid', var = self.windGrid_enabled, command=self.toggle_windGrid) 
        self.gsP_wgButton.deselect()
        self.gsP_wgButton.pack(side=tk.LEFT)
        self.gsP_wgTFrame.pack(side=tk.TOP, fill=tk.X)
        self.gsP_wgTFrame = tk.Frame(self.gridsPanel)
        self.gsP_wgEntry_min = tk.Entry(self.gsP_wgTFrame, width=20, textvariable=self.var_gridWind_beg)
        self.gsP_wgEntry_min.config(state='disabled')
        self.gsP_wgEntry_min.pack(side=tk.RIGHT)
        self.gsP_wgLabel_min = tk.Label(self.gsP_wgTFrame, text="    min (m.s-1):", state='disabled')
        self.gsP_wgLabel_min.pack(side=tk.RIGHT)
        self.gsP_wgTFrame.pack(side=tk.TOP, fill=tk.X)
        self.gsP_wgTFrame = tk.Frame(self.gridsPanel)
        self.gsP_wgEntry_max = tk.Entry(self.gsP_wgTFrame, width=20, textvariable=self.var_gridWind_end)
        self.gsP_wgEntry_max.config(state='disabled')
        self.gsP_wgEntry_max.pack(side=tk.RIGHT)
        self.gsP_wgLabel_max = tk.Label(self.gsP_wgTFrame, text="    max (m.s-1):", state='disabled')
        self.gsP_wgLabel_max.pack(side=tk.RIGHT)
        self.gsP_wgTFrame.pack(side=tk.TOP, fill=tk.X)
        self.gsP_wgTFrame = tk.Frame(self.gridsPanel)
        self.gsP_wgEntry_num = tk.Entry(self.gsP_wgTFrame, width=20, textvariable=self.var_gridWind_num)
        self.gsP_wgEntry_num.config(state='disabled')
        self.gsP_wgEntry_num.pack(side=tk.RIGHT)
        self.gsP_wgLabel_num = tk.Label(self.gsP_wgTFrame, text="    num:", state='disabled')
        self.gsP_wgLabel_num.pack(side=tk.RIGHT)
        self.gsP_wgTFrame.pack(side=tk.TOP, fill=tk.X)
        self.gsP_wgEntry_min.bind('<Return>', self.set_gridWind_beg)
        self.gsP_wgEntry_max.bind('<Return>', self.set_gridWind_end)
        self.gsP_wgEntry_num.bind('<Return>', self.set_gridWind_num)
        
        
        self.gsP_tgTFrame = tk.Frame(self.gridsPanel)
        self.var_gridTurb_beg = tk.StringVar(value=str(self.gridTurbine_beg))
        self.var_gridTurb_end = tk.StringVar(value=str(self.gridTurbine_end))
        self.var_gridTurb_num = tk.StringVar(value=str(self.gridTurbine_num))
        self.gsP_tgButton = tk.Checkbutton(self.gsP_tgTFrame, text='Turbine grid', var = self.turbGrid_enabled, command=self.toggle_turbGrid) 
        self.gsP_tgButton.deselect()
        self.gsP_tgButton.pack(side=tk.LEFT)
        self.gsP_tgTFrame.pack(side=tk.TOP, fill=tk.X)
        self.gsP_tgTFrame = tk.Frame(self.gridsPanel)
        self.gsP_tgEntry_min = tk.Entry(self.gsP_tgTFrame, width=20, textvariable=self.var_gridTurb_beg)
        self.gsP_tgEntry_min.config(state='disabled')
        self.gsP_tgEntry_min.pack(side=tk.RIGHT)
        self.gsP_tgLabel_min = tk.Label(self.gsP_tgTFrame, text="    min (rpm):", state='disabled')
        self.gsP_tgLabel_min.pack(side=tk.RIGHT)
        self.gsP_tgTFrame.pack(side=tk.TOP, fill=tk.X)
        self.gsP_tgTFrame = tk.Frame(self.gridsPanel)
        self.gsP_tgEntry_max = tk.Entry(self.gsP_tgTFrame, width=20, textvariable=self.var_gridTurb_end)
        self.gsP_tgEntry_max.config(state='disabled')
        self.gsP_tgEntry_max.pack(side=tk.RIGHT)
        self.gsP_tgLabel_max = tk.Label(self.gsP_tgTFrame, text="    max (rpm):", state='disabled')
        self.gsP_tgLabel_max.pack(side=tk.RIGHT)
        self.gsP_tgTFrame.pack(side=tk.TOP, fill=tk.X)
        self.gsP_tgTFrame = tk.Frame(self.gridsPanel)
        self.gsP_tgEntry_num = tk.Entry(self.gsP_tgTFrame, width=20, textvariable=self.var_gridTurb_num)
        self.gsP_tgEntry_num.config(state='disabled')
        self.gsP_tgEntry_num.pack(side=tk.RIGHT)
        self.gsP_tgLabel_num = tk.Label(self.gsP_tgTFrame, text="    num:", state='disabled')
        self.gsP_tgLabel_num.pack(side=tk.RIGHT)
        self.gsP_tgTFrame.pack(side=tk.TOP, fill=tk.X)
        self.gsP_tgEntry_min.bind('<Return>', self.set_gridTurb_beg)
        self.gsP_tgEntry_max.bind('<Return>', self.set_gridTurb_end)
        self.gsP_tgEntry_num.bind('<Return>', self.set_gridTurb_num)
        
        
        self.gsP_tigTFrame = tk.Frame(self.gridsPanel)
        self.var_gridTilt_beg = tk.StringVar(value=str(self.gridTilt_beg))
        self.var_gridTilt_end = tk.StringVar(value=str(self.gridTilt_end))
        self.var_gridTilt_num = tk.StringVar(value=str(self.gridTilt_num))
        self.gsP_tigButton = tk.Checkbutton(self.gsP_tigTFrame, text='Blade tilt grid', var = self.tiltGrid_enabled, command=self.toggle_tiltGrid) 
        self.gsP_tigButton.deselect()
        self.gsP_tigButton.pack(side=tk.LEFT)
        self.gsP_tigTFrame.pack(side=tk.TOP, fill=tk.X)
        self.gsP_tigTFrame = tk.Frame(self.gridsPanel)
        self.gsP_tigEntry_min = tk.Entry(self.gsP_tigTFrame, width=20, textvariable=self.var_gridTilt_beg)
        self.gsP_tigEntry_min.config(state='disabled')
        self.gsP_tigEntry_min.pack(side=tk.RIGHT)
        self.gsP_tigLabel_min = tk.Label(self.gsP_tigTFrame, text="    min (deg):", state='disabled')
        self.gsP_tigLabel_min.pack(side=tk.RIGHT)
        self.gsP_tigTFrame.pack(side=tk.TOP, fill=tk.X)
        self.gsP_tigTFrame = tk.Frame(self.gridsPanel)
        self.gsP_tigEntry_max = tk.Entry(self.gsP_tigTFrame, width=20, textvariable=self.var_gridTilt_end)
        self.gsP_tigEntry_max.config(state='disabled')
        self.gsP_tigEntry_max.pack(side=tk.RIGHT)
        self.gsP_tigLabel_max = tk.Label(self.gsP_tigTFrame, text="    max (deg):", state='disabled')
        self.gsP_tigLabel_max.pack(side=tk.RIGHT)
        self.gsP_tigTFrame.pack(side=tk.TOP, fill=tk.X)
        self.gsP_tigTFrame = tk.Frame(self.gridsPanel)
        self.gsP_tigEntry_num = tk.Entry(self.gsP_tigTFrame, width=20, textvariable=self.var_gridTilt_num)
        self.gsP_tigEntry_num.config(state='disabled')
        self.gsP_tigEntry_num.pack(side=tk.RIGHT)
        self.gsP_tigLabel_num = tk.Label(self.gsP_tigTFrame, text="    num:", state='disabled')
        self.gsP_tigLabel_num.pack(side=tk.RIGHT)
        self.gsP_tigTFrame.pack(side=tk.TOP, fill=tk.X)
        self.gsP_tigEntry_min.bind('<Return>', self.set_gridTilt_beg)
        self.gsP_tigEntry_max.bind('<Return>', self.set_gridTilt_end)
        self.gsP_tigEntry_num.bind('<Return>', self.set_gridTilt_num)
        
        self.gridsPanel.pack(side=tk.TOP)
        
        
        self.var_output_path = tk.StringVar(value=self.output_dir)
        self.output_enabled = tk.BooleanVar()
        self.output_enabled.set(True)
        
        
        self.resultFilePanel = tk.LabelFrame(self.settingPanel, text="Output", padx=2, pady=2)
        
        self.rfP_buttonFrame = tk.Frame(self.resultFilePanel)
        self.rfP_outputButton = tk.Checkbutton(self.rfP_buttonFrame, text='Write output file ?', var = self.output_enabled, command=self.toggle_output) 
        self.rfP_outputButton.select()
        self.rfP_outputButton.pack(side=tk.LEFT)
        self.rfP_buttonFrame.pack(side=tk.TOP, fill=tk.X)
        self.rfP_entryFrame = tk.Frame(self.resultFilePanel)
        self.rfP_outputEntry = tk.Entry(self.rfP_entryFrame, width=30, textvariable=self.var_output_path)
        self.rfP_outputEntry.bind('<Return>', self.set_output_dir)
        self.rfP_outputEntry.config(state='normal')
        self.rfP_outputEntry.pack(side=tk.RIGHT)
        self.rfP_outputLabel = tk.Label(self.rfP_entryFrame, text="dir:", state='normal')
        self.rfP_outputLabel.pack(side=tk.RIGHT)
        self.rfP_entryFrame.pack(side=tk.TOP, fill=tk.X)
        
        self.resultFilePanel.pack(side=tk.TOP)
        
        
        
        self.bouton_run = tk.Button(self.settingPanel, text="START SIMULATION", command=self.startModel, height=3, bg='#CCFFCC')
        self.bouton_run.pack(side=tk.BOTTOM, fill=tk.X)
        
        
        self.settingPanel.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.debugPlotBlade()
        
    
    def set_gridModel_len(self):
        self.gridModelLen = 1
        if self.windGrid_enabled.get():
            self.gridModelLen *= self.gridWind_num
        if self.turbGrid_enabled.get():
            self.gridModelLen *= self.gridTurbine_num
        if self.tiltGrid_enabled.get():
            self.gridModelLen *= self.gridTilt_num
            
    def toggle_allSteps(self):
        if self.allSteps_enabled.get():
            print("enabling all steps show")
            self.output_allSteps = True
            self.RUNNING_INTERVAL = 40
        else:
            print("disabling all steps show")
            self.output_allSteps = False
            self.RUNNING_INTERVAL = 5
    
    def toggle_windGrid(self):
        if self.windGrid_enabled.get():
            print("enabling wind grid")
            self.gsP_wgEntry_min.config(state='normal')
            self.gsP_wgLabel_min.config(state='normal')
            self.gsP_wgEntry_max.config(state='normal')
            self.gsP_wgLabel_max.config(state='normal')
            self.gsP_wgEntry_num.config(state='normal')
            self.gsP_wgLabel_num.config(state='normal')
            self.gP_wsF_title.config(state='disabled')
            self.gP_wsF_box.config(state='disabled')
            self.windSpeed = self.gridWind_beg
        else:
            print("disabling wind grid")
            self.gsP_wgEntry_min.config(state='disabled')
            self.gsP_wgLabel_min.config(state='disabled')
            self.gsP_wgEntry_max.config(state='disabled')
            self.gsP_wgLabel_max.config(state='disabled')
            self.gsP_wgEntry_num.config(state='disabled')
            self.gsP_wgLabel_num.config(state='disabled')
            self.gP_wsF_title.config(state='normal')
            self.gP_wsF_box.config(state='normal')
            self.windSpeed = float(self.var_wSpeed.get())
        self.set_gridModel_len()
        self.geoBlade()
        self.drawMonitor()
            
    def toggle_turbGrid(self):
        if self.turbGrid_enabled.get():
            print("enabling turbine grid")
            self.gsP_tgEntry_min.config(state='normal')
            self.gsP_tgLabel_min.config(state='normal')
            self.gsP_tgEntry_max.config(state='normal')
            self.gsP_tgLabel_max.config(state='normal')
            self.gsP_tgEntry_num.config(state='normal')
            self.gsP_tgLabel_num.config(state='normal')
            self.gP_tsF_title.config(state='disabled')
            self.gP_tsF_box.config(state='disabled')
            self.turbSpeed = self.gridTurbine_beg
        else:
            print("disabling turbine grid")
            self.gsP_tgEntry_min.config(state='disabled')
            self.gsP_tgLabel_min.config(state='disabled')
            self.gsP_tgEntry_max.config(state='disabled')
            self.gsP_tgLabel_max.config(state='disabled')
            self.gsP_tgEntry_num.config(state='disabled')
            self.gsP_tgLabel_num.config(state='disabled')
            self.gP_tsF_title.config(state='normal')
            self.gP_tsF_box.config(state='normal')
            self.turbSpeed = float(self.var_tSpeed.get())
        self.set_gridModel_len()
        self.geoBlade()
        self.drawMonitor()
            
    def toggle_tiltGrid(self):
        if self.tiltGrid_enabled.get():
            print("enabling blade tilt grid")
            self.gsP_tigEntry_min.config(state='normal')
            self.gsP_tigLabel_min.config(state='normal')
            self.gsP_tigEntry_max.config(state='normal')
            self.gsP_tigLabel_max.config(state='normal')
            self.gsP_tigEntry_num.config(state='normal')
            self.gsP_tigLabel_num.config(state='normal')
            self.gP_btF_title.config(state='disabled')
            self.gP_btF_box.config(state='disabled')
            self.bladeTilt = self.gridTilt_beg
        else:
            print("disabling blade tilt grid")
            self.gsP_tigEntry_min.config(state='disabled')
            self.gsP_tigLabel_min.config(state='disabled')
            self.gsP_tigEntry_max.config(state='disabled')
            self.gsP_tigLabel_max.config(state='disabled')
            self.gsP_tigEntry_num.config(state='disabled')
            self.gsP_tigLabel_num.config(state='disabled')
            self.gP_btF_title.config(state='normal')
            self.gP_btF_box.config(state='normal')
            self.bladeTilt = float(self.var_bTilt.get())
        self.set_gridModel_len()
        self.geoBlade()
        self.drawMonitor()
        
        
    def toggle_output(self):
        if self.output_enabled.get():
            print("enabling output file")
            self.rfP_outputEntry.config(state='normal')
            self.rfP_outputLabel.config(state='normal')
        else:
            print("disabling output file")
            self.rfP_outputEntry.config(state='disabled')
            self.rfP_outputLabel.config(state='disabled')
            
            
        
    def chooseProfile(self, event):
        select = self.gP_pF_profileList.get()
        # print(select)
        self.setProfile(select)
        self.geoBlade()
        self.drawMonitor()
        
    def setProfile(self, select):
        prof_x, prof_y = self.foilerHandler.loadProfile(select)
        self.PROFILE = np.array([prof_x, prof_y])
        self.PROFILE[0] = -self.PROFILE[0]+0.5
        self.PROFILE = self.PROFILE.T
        self.bProfile = select
       
            
            
    def set_tRadius(self, *args):
        self.turbineRadius = float(self.var_tRadius.get())
        self.geoBlade()
        self.drawMonitor()
            
    def set_bSize(self, *args):
        self.bladeSize = float(self.var_bSize.get())
        self.geoBlade()
        self.drawMonitor()
            
    def set_bTilt(self, *args):
        self.bladeTilt = float(self.var_bTilt.get())
        self.geoBlade()
        self.drawMonitor()
            
    def set_wSpeed(self, *args):
        self.windSpeed = float(self.var_wSpeed.get())
        self.geoBlade()
        self.drawMonitor()
            
    def set_tSpeed(self, *args):
        self.turbSpeed = float(self.var_tSpeed.get())
        self.geoBlade()
        self.drawMonitor()
        
    def set_gridAngle_beg(self, event):
        self.gridAngle_beg = float(self.var_gridAngle_beg.get())
        self.geoBlade()
        self.drawMonitor()
            
    def set_gridAngle_end(self, event):
        self.gridAngle_end = float(self.var_gridAngle_end.get())
        self.geoBlade()
        self.drawMonitor()
    
    def set_gridAngle_num(self, event):
        self.gridAngle_num = int(self.var_gridAngle_num.get())
        self.geoBlade()
        self.drawMonitor()
    
    def set_gridWind_beg(self, event):
        self.gridWind_beg = float(self.var_gridWind_beg.get())
        self.geoBlade()
        self.drawMonitor()
            
    def set_gridWind_end(self, event):
        self.gridWind_end = float(self.var_gridWind_end.get())
        self.geoBlade()
        self.drawMonitor()
    
    def set_gridWind_num(self, event):
        self.gridWind_num = int(self.var_gridWind_num.get())
        self.set_gridModel_len()
        self.geoBlade()
        self.drawMonitor()
    
    def set_gridTurb_beg(self, event):
        self.gridTurbine_beg = float(self.var_gridTurb_beg.get())
        self.geoBlade()
        self.drawMonitor()
            
    def set_gridTurb_end(self, event):
        self.gridTurbine_end = float(self.var_gridTurb_end.get())
        self.geoBlade()
        self.drawMonitor()
    
    def set_gridTurb_num(self, event):
        self.gridTurbine_num = int(self.var_gridTurb_num.get())
        self.set_gridModel_len()
        self.geoBlade()
        self.drawMonitor()
    
    def set_gridTilt_beg(self, event):
        self.gridTilt_beg = float(self.var_gridTilt_beg.get())
        self.geoBlade()
        self.drawMonitor()
            
    def set_gridTilt_end(self, event):
        self.gridTilt_end = float(self.var_gridTilt_end.get())
        self.geoBlade()
        self.drawMonitor()
    
    def set_gridTilt_num(self, event):
        self.gridTilt_num = int(self.var_gridTilt_num.get())
        self.set_gridModel_len()
        self.geoBlade()
        self.drawMonitor()
    
    def set_output_dir(self, event):
        self.output_dir = self.var_output_path.get()
        print(self.output_dir)
        # self.geoBlade()
        # self.drawMonitor()
    
            
    def startModel(self):
        self.running = True
        self.bouton_run.configure(text="STOP SIMULATION", command=self.stopModel, bg='#FFCCCC')
        self.gsP_tgButton.config(state='disabled')
        self.gsP_tgEntry_min.config(state='disabled')
        self.gsP_tgLabel_min.config(state='disabled')
        self.gsP_tgEntry_max.config(state='disabled')
        self.gsP_tgLabel_max.config(state='disabled')
        self.gsP_tgEntry_num.config(state='disabled')
        self.gsP_tgLabel_num.config(state='disabled')
        self.gsP_tigButton.config(state='disabled')
        self.gsP_tigEntry_min.config(state='disabled')
        self.gsP_tigLabel_min.config(state='disabled')
        self.gsP_tigEntry_max.config(state='disabled')
        self.gsP_tigLabel_max.config(state='disabled')
        self.gsP_tigEntry_num.config(state='disabled')
        self.gsP_tigLabel_num.config(state='disabled')
        self.gsP_wgButton.config(state='disabled')
        self.gsP_wgEntry_min.config(state='disabled')
        self.gsP_wgLabel_min.config(state='disabled')
        self.gsP_wgEntry_max.config(state='disabled')
        self.gsP_wgLabel_max.config(state='disabled')
        self.gsP_wgEntry_num.config(state='disabled')
        self.gsP_wgLabel_num.config(state='disabled')
        self.gsP_agLabel.config(state='disabled')
        self.gsP_agEntry_min.config(state='disabled')
        self.gsP_agLabel_min.config(state='disabled')
        self.gsP_agEntry_max.config(state='disabled')
        self.gsP_agLabel_max.config(state='disabled')
        self.gsP_agEntry_num.config(state='disabled')
        self.gsP_agLabel_num.config(state='disabled')
        self.gP_pF_title.config(state='disabled')
        self.gP_pF_profileList.config(state='disabled')
        self.gP_trF_title.config(state='disabled')
        self.gP_trF_box.config(state='disabled')
        self.gP_bsF_title.config(state='disabled')
        self.gP_bsF_box.config(state='disabled')
        self.gP_btF_title.config(state='disabled')
        self.gP_btF_box.config(state='disabled')
        self.gP_wsF_title.config(state='disabled')
        self.gP_wsF_box.config(state='disabled')
        self.gP_tsF_title.config(state='disabled')
        self.gP_tsF_box.config(state='disabled')
        self.rfP_outputButton.config(state='disabled')
        self.rfP_outputEntry.config(state='disabled')
        self.rfP_outputLabel.config(state='disabled')
        
        self.plotX = []
        self.plotY = []
        self.outputCurMod = [[], [], [], [], [], []]
        
        Na, Nb, Nc, Nd = self.setGrid()
        self.windSpeed = self.gridModel[0][0]
        self.turbSpeed = self.gridModel[0][1]
        self.bladeTilt = self.gridModel[0][2]
                    
        
        if self.output_enabled.get():
            output = open(self.output_dir + '\\' + self.OUTPUT_NAME + '.dat', 'w')
            output.write('# Vertical Turbine Simulation Output\n')
            output.write('#---------------------------------------\n')
            output.write('# Parameters:\n')
            output.write('#    - Turbine radius:       {0:.2f} m\n'.format(self.turbineRadius))
            output.write('#    - Turbine height:       1.0 m\n')
            output.write('#    - Blade profile:        {0}\n'.format(self.bProfile))
            output.write('#    - Date & hour of simu.: {0}\n'.format(time.asctime(time.localtime())))
            output.write('# Datacube shape:\n')
            output.write('#  0 - Turbine angle:    {0}\n'.format(Na))
            output.write('#  1 - Wind speed:       {0}\n'.format(Nb))
            output.write('#  2 - Turbine speed:    {0}\n'.format(Nc))
            output.write('#  3 - Blade tilt angle: {0}\n'.format(Nd))
            output.write('# Columns:\n')
            output.write('#  0 - Turbine angle (degree)\n')
            output.write('#  1 - Wind speed (m.s-1)\n')
            output.write('#  2 - Turbine speed (r.p.m.)\n')
            output.write('#  3 - Blade tilt angle (degree)\n')
            output.write('#  4 - Turbine torque (kg.m2.s-2)\n')
            output.write('#  5 - Effective surface (m2)\n')
            output.write('#---------------------------------------\n')
            output.close()
            
        self.runModel()
        
        
    def runModel(self):
        self.geoBlade()
        
        # ------------
        # send information to physics class
        # compute the torque on each blade and on the turbine
        # fL: lift force
        # fD: drag force
        # M: momentum torque
        # S: effective surface
        self.fL1, self.fD1, self.M1, self.S1, cz, cx = self.foilerHandler.computeLiftDrag(self.theta1, self.veffx1, self.veffy1, self.turbineAngle, self.turbineRadius)
        self.fL2, self.fD2, self.M2, self.S2, _, _ = self.foilerHandler.computeLiftDrag(self.theta2, self.veffx2, self.veffy2, self.turbineAngle+120, self.turbineRadius)
        self.fL3, self.fD3, self.M3, self.S3, _, _ = self.foilerHandler.computeLiftDrag(self.theta3, self.veffx3, self.veffy3, self.turbineAngle+240, self.turbineRadius)
        # ------------
        
        if self.output_allSteps:
            self.drawMonitor()
        if self.running:
            self.plotX.append(self.turbineAngle)
            self.plotY.append(self.M1 + self.M2 + self.M3)
            self.outputCurMod[0].append(self.turbineAngle)
            self.outputCurMod[1].append(self.windSpeed)
            self.outputCurMod[2].append(self.turbSpeed)
            self.outputCurMod[3].append(self.bladeTilt)
            self.outputCurMod[4].append(self.M1 + self.M2 + self.M3)
            self.outputCurMod[5].append(self.S1 + self.S2 + self.S3)
            if self.output_enabled.get() and self.output_allSteps:
                output = open(self.output_dir + '\\' + self.OUTPUT_NAME + '.dat', 'a')
                output.write('{0:6.1f} {1:6.2f} {2:6.2f} {3:6.2f} {4:8.4f} {5:8.4f}\n'.format(self.turbineAngle, self.windSpeed, self.turbSpeed, self.bladeTilt, self.M1 + self.M2 + self.M3, self.S1 + self.S2 + self.S3))
                output.close()
        
            self.gridAng_i += 1
            if self.gridAng_i >= len(self.gridAngle):
                self.gridMod_i += 1
                self.gridAng_i = 0
                if not self.output_allSteps:
                    self.turbineAngle = self.gridAngle[self.gridAng_i]
                    self.windSpeed = self.gridModel[self.gridMod_i%len(self.gridModel)][0]
                    self.turbSpeed = self.gridModel[self.gridMod_i%len(self.gridModel)][1]
                    self.bladeTilt = self.gridModel[self.gridMod_i%len(self.gridModel)][2]
                    self.drawMonitor()
                    output = open(self.output_dir + '\\' + self.OUTPUT_NAME + '.dat', 'a')
                    for i in range(len(self.outputCurMod[0])):
                        output.write('{0:6.1f} {1:6.2f} {2:6.2f} {3:6.2f} {4:8.4f} {5:8.4f}\n'.format(self.outputCurMod[0][i], self.outputCurMod[1][i], self.outputCurMod[2][i], self.outputCurMod[3][i], self.outputCurMod[4][i], self.outputCurMod[5][i]))
                    output.close()
                    if self.gridMod_i < len(self.gridModel):
                        self.plotX = []
                        self.plotY = []
                    self.outputCurMod = [[], [], [], [], [], []]
        
            
            if self.gridMod_i >= len(self.gridModel):
                self.stopModel()
            
            
            self.turbineAngle = self.gridAngle[self.gridAng_i]
            self.windSpeed = self.gridModel[self.gridMod_i][0]
            self.turbSpeed = self.gridModel[self.gridMod_i][1]
            self.bladeTilt = self.gridModel[self.gridMod_i][2]
            
            
            self.after(self.RUNNING_INTERVAL, self.runModel)
        
        
    def stopModel(self):
        self.running = False
        if not self.output_allSteps:
            output = open(self.output_dir + '\\' + self.OUTPUT_NAME + '.dat', 'a')
            for i in range(len(self.outputCurMod[0])):
                output.write('{0:6.1f} {1:6.2f} {2:6.2f} {3:6.2f} {4:9.4f} {5:7.4f}\n'.format(self.outputCurMod[0][i], self.outputCurMod[1][i], self.outputCurMod[2][i], self.outputCurMod[3][i], self.outputCurMod[4][i], self.outputCurMod[5][i]))
            output.close()
            self.outputCurMod = [[], [], [], [], [], []]
        self.bouton_run.configure(text="START SIMULATION", command=self.startModel, bg='#CCFFCC')
        self.gridAng_i = 0
        self.gridMod_i = 0
        self.gP_pF_title.config(state='normal')
        self.gP_pF_profileList.config(state='normal')
        self.gP_trF_title.config(state='normal')
        self.gP_trF_box.config(state='normal')
        self.gP_bsF_title.config(state='normal')
        self.gP_bsF_box.config(state='normal')
        self.gsP_agLabel.config(state='normal')
        self.gsP_agEntry_min.config(state='normal')
        self.gsP_agLabel_min.config(state='normal')
        self.gsP_agEntry_max.config(state='normal')
        self.gsP_agLabel_max.config(state='normal')
        self.gsP_agEntry_num.config(state='normal')
        self.gsP_agLabel_num.config(state='normal')
        self.gsP_wgButton.config(state='normal')
        self.gsP_tgButton.config(state='normal')
        self.gsP_tigButton.config(state='normal')
        self.rfP_outputButton.config(state='normal')

        self.toggle_windGrid()
        self.toggle_turbGrid()
        self.toggle_tiltGrid()
        self.toggle_output()
        
        
            
            
            
    def setGrid(self):
        self.gridAngle = np.arange(self.gridAngle_beg, self.gridAngle_end, step=(self.gridAngle_end-self.gridAngle_beg)/(self.gridAngle_num))
        # print(self.gridAngle)
        if self.windGrid_enabled.get():
            wG = np.linspace(self.gridWind_beg, self.gridWind_end, num=self.gridWind_num)
        else:
            wG = [self.windSpeed]
        if self.turbGrid_enabled.get():
            tG = np.linspace(self.gridTurbine_beg, self.gridTurbine_end, num=self.gridTurbine_num)
        else:
            tG = [self.turbSpeed]
        if self.tiltGrid_enabled.get():
            iG = np.linspace(self.gridTilt_beg, self.gridTilt_end, num=self.gridTilt_num)
        else:
            iG = [self.bladeTilt]
        self.gridModel = []
        for w in wG:
            for t in tG:
                for i in iG:
                    self.gridModel.append([w, t, i])
        self.gridModel = np.array(self.gridModel)
        return len(self.gridAngle), len(wG), len(tG), len(iG)
        
            
        
    def drawMonitor(self):
        self.canv.delete("all")
        self.canv.create_line(0, 0.6*self.height, self.width, 0.6*self.height)
        self.canv.create_line(self.width - 0.2*self.height, 0, self.width - 0.2*self.height, 0.6*self.height)
        self.canv.create_line(self.width - 0.2*self.height, 0.2*self.height, self.width, 0.2*self.height)
        self.canv.create_line(self.width - 0.2*self.height, 0.4*self.height, self.width, 0.4*self.height)
        
        tCenter = [self.width - 0.5*self.height, 0.3*self.height]
        self.canv.create_oval(self.width - 0.7*self.height, 0.1*self.height, self.width - 0.3*self.height, 0.5*self.height, dash=(2, 3) )
        self.canv.create_line(tCenter[0], tCenter[1], tCenter[0] + 0.2*self.height*np.cos(self.turbineAngle / 180.0*np.pi), tCenter[1] - 0.2*self.height*np.sin(self.turbineAngle / 180.0*np.pi), dash=(2, 3) )
        self.canv.create_line(tCenter[0], tCenter[1], tCenter[0] + 0.2*self.height*np.cos((self.turbineAngle+120) / 180.0*np.pi), tCenter[1] - 0.2*self.height*np.sin((self.turbineAngle+120) / 180.0*np.pi), dash=(2, 3) )
        self.canv.create_line(tCenter[0], tCenter[1], tCenter[0] + 0.2*self.height*np.cos((self.turbineAngle+240) / 180.0*np.pi), tCenter[1] - 0.2*self.height*np.sin((self.turbineAngle+240) / 180.0*np.pi), dash=(2, 3) )
        
        bCoord = self.PROFILE*0.2*self.height * self.bladeSize / self.turbineRadius
        blade = bCoord.T
        
        blade1 = blade.copy()
        blade1[0] = blade[0]*np.cos(np.pi/2 + (self.turbineAngle + self.bladeTilt) / 180.0*np.pi) + blade[1]*np.sin(np.pi/2 + (self.turbineAngle + self.bladeTilt) / 180.0*np.pi) + tCenter[0] + 0.2*self.height*np.cos(self.turbineAngle / 180.0*np.pi)
        blade1[1] = blade[1]*np.cos(np.pi/2 + (self.turbineAngle + self.bladeTilt) / 180.0*np.pi) - blade[0]*np.sin(np.pi/2 + (self.turbineAngle + self.bladeTilt) / 180.0*np.pi) + tCenter[1] - 0.2*self.height*np.sin(self.turbineAngle / 180.0*np.pi)
        blade1 = blade1.T.tolist()
        self.canv.create_polygon(blade1, fill=self.CANVCOLOR_BLADE[0], outline="black", width=1)
        blade1 = blade.copy()
        blade1[0] = blade[0]*np.cos(np.pi/2 + (self.turbineAngle + self.bladeTilt+120) / 180.0*np.pi) + blade[1]*np.sin(np.pi/2 + (self.turbineAngle + self.bladeTilt+120) / 180.0*np.pi) + tCenter[0] + 0.2*self.height*np.cos((self.turbineAngle+120) / 180.0*np.pi)
        blade1[1] = blade[1]*np.cos(np.pi/2 + (self.turbineAngle + self.bladeTilt+120) / 180.0*np.pi) - blade[0]*np.sin(np.pi/2 + (self.turbineAngle + self.bladeTilt+120) / 180.0*np.pi) + tCenter[1] - 0.2*self.height*np.sin((self.turbineAngle+120) / 180.0*np.pi)
        blade1 = blade1.T.tolist()
        self.canv.create_polygon(blade1, fill=self.CANVCOLOR_BLADE[1], outline="black", width=1)
        blade1 = blade.copy()
        blade1[0] = blade[0]*np.cos(np.pi/2 + (self.turbineAngle + self.bladeTilt+240) / 180.0*np.pi) + blade[1]*np.sin(np.pi/2 + (self.turbineAngle + self.bladeTilt+240) / 180.0*np.pi) + tCenter[0] + 0.2*self.height*np.cos((self.turbineAngle+240) / 180.0*np.pi)
        blade1[1] = blade[1]*np.cos(np.pi/2 + (self.turbineAngle + self.bladeTilt+240) / 180.0*np.pi) - blade[0]*np.sin(np.pi/2 + (self.turbineAngle + self.bladeTilt+240) / 180.0*np.pi) + tCenter[1] - 0.2*self.height*np.sin((self.turbineAngle+240) / 180.0*np.pi)
        blade1 = blade1.T.tolist()
        self.canv.create_polygon(blade1, fill=self.CANVCOLOR_BLADE[2], outline="black", width=1)
        
        
        bCoord = self.PROFILE*0.15*self.height
        blade = bCoord.T
        blade[1] = -blade[1]
        blade[0] = -blade[0]
        
        tCenter = [self.width - 0.1*self.height, 0.1*self.height]
        blade1 = blade.copy()
        blade1[0] = blade[0]*np.cos((-self.theta1) / 180.0*np.pi) + blade[1]*np.sin((-self.theta1) / 180.0*np.pi) + tCenter[0] 
        blade1[1] = blade[1]*np.cos((-self.theta1) / 180.0*np.pi) - blade[0]*np.sin((-self.theta1) / 180.0*np.pi) + tCenter[1] 
        blade1 = blade1.T.tolist()
        self.canv.create_line(self.width-0.18*self.height, 0.04*self.height, self.width-0.02*self.height, 0.04*self.height, arrow='last', fill='#BBBBBB' )
        self.canv.create_line(self.width-0.18*self.height, 0.08*self.height, self.width-0.02*self.height, 0.08*self.height, arrow='last', fill='#BBBBBB' )
        self.canv.create_line(self.width-0.18*self.height, 0.12*self.height, self.width-0.02*self.height, 0.12*self.height, arrow='last', fill='#BBBBBB' )
        self.canv.create_line(self.width-0.18*self.height, 0.16*self.height, self.width-0.02*self.height, 0.16*self.height, arrow='last', fill='#BBBBBB' )
        self.canv.create_polygon(blade1, fill=self.CANVCOLOR_BLADE[0], outline="black", width=1)
        self.canv.create_line(self.width-0.2*self.height, 0.1*self.height, self.width, 0.1*self.height, dash=(2, 3) )
        self.canv.create_text(self.width-0.195*self.height, 0.195*self.height, anchor='sw', text='{0:.1f} deg'.format(self.theta1))
        self.canv.create_text(self.width-0.005*self.height, 0.195*self.height, anchor='se', text='{0:.1f} m.s-1'.format(np.sqrt(self.veffx1**2 + self.veffy1**2)))
        
        tCenter = [self.width - 0.1*self.height, 0.3*self.height]
        blade1 = blade.copy()
        blade1[0] = blade[0]*np.cos((-self.theta2) / 180.0*np.pi) + blade[1]*np.sin((-self.theta2) / 180.0*np.pi) + tCenter[0] 
        blade1[1] = blade[1]*np.cos((-self.theta2) / 180.0*np.pi) - blade[0]*np.sin((-self.theta2) / 180.0*np.pi) + tCenter[1] 
        blade1 = blade1.T.tolist()
        self.canv.create_line(self.width-0.18*self.height, 0.24*self.height, self.width-0.02*self.height, 0.24*self.height, arrow='last', fill='#BBBBBB' )
        self.canv.create_line(self.width-0.18*self.height, 0.28*self.height, self.width-0.02*self.height, 0.28*self.height, arrow='last', fill='#BBBBBB' )
        self.canv.create_line(self.width-0.18*self.height, 0.32*self.height, self.width-0.02*self.height, 0.32*self.height, arrow='last', fill='#BBBBBB' )
        self.canv.create_line(self.width-0.18*self.height, 0.36*self.height, self.width-0.02*self.height, 0.36*self.height, arrow='last', fill='#BBBBBB' )
        self.canv.create_polygon(blade1, fill=self.CANVCOLOR_BLADE[1], outline="black", width=1)
        self.canv.create_line(self.width-0.2*self.height, 0.3*self.height, self.width, 0.3*self.height, dash=(2, 3) )
        self.canv.create_text(self.width-0.195*self.height, 0.395*self.height, anchor='sw', text='{0:.1f} deg'.format(self.theta2))
        self.canv.create_text(self.width-0.005*self.height, 0.395*self.height, anchor='se', text='{0:.1f} m.s-1'.format(np.sqrt(self.veffx2**2 + self.veffy2**2)))
        
        tCenter = [self.width - 0.1*self.height, 0.5*self.height]
        blade1 = blade.copy()
        blade1[0] = blade[0]*np.cos((-self.theta3) / 180.0*np.pi) + blade[1]*np.sin((-self.theta3) / 180.0*np.pi) + tCenter[0] 
        blade1[1] = blade[1]*np.cos((-self.theta3) / 180.0*np.pi) - blade[0]*np.sin((-self.theta3) / 180.0*np.pi) + tCenter[1] 
        blade1 = blade1.T.tolist()
        self.canv.create_line(self.width-0.18*self.height, 0.44*self.height, self.width-0.02*self.height, 0.44*self.height, arrow='last', fill='#BBBBBB' )
        self.canv.create_line(self.width-0.18*self.height, 0.48*self.height, self.width-0.02*self.height, 0.48*self.height, arrow='last', fill='#BBBBBB' )
        self.canv.create_line(self.width-0.18*self.height, 0.52*self.height, self.width-0.02*self.height, 0.52*self.height, arrow='last', fill='#BBBBBB' )
        self.canv.create_line(self.width-0.18*self.height, 0.56*self.height, self.width-0.02*self.height, 0.56*self.height, arrow='last', fill='#BBBBBB' )
        self.canv.create_polygon(blade1, fill=self.CANVCOLOR_BLADE[2], outline="black", width=1)
        self.canv.create_line(self.width-0.2*self.height, 0.5*self.height, self.width, 0.5*self.height, dash=(2, 3) )
        self.canv.create_text(self.width-0.195*self.height, 0.595*self.height, anchor='sw', text='{0:.1f} deg'.format(self.theta3))
        self.canv.create_text(self.width-0.005*self.height, 0.595*self.height, anchor='se', text='{0:.1f} m.s-1'.format(np.sqrt(self.veffx3**2 + self.veffy3**2)))
        
        
        self.canv.create_line(self.width-0.8*self.height, 0.3*self.height, self.width-0.75*self.height, 0.3*self.height, width=3, arrow='last')
        
        textX, textY = 20, 0.25*self.height
        if self.running:
            text = "Current state\n"
        else:
            text = "Initial state\n"
        # text += "    turbine radius:\n"
        # text += "    blade size:\n"
        text += "    Model:\n"
        text += "    turbine angle:\n"
        text += "    blade tilt:\n"
        text += "    wind speed:\n"
        text += "    turbine speed:"
        self.canv.create_text(textX, textY, anchor='nw', text=text, font=('Arial',12))
        textX, textY = 20+130, 0.25*self.height
        text = "\n"
        # text += "{0:.2f} m\n".format(self.turbineRadius)
        # text += "{0:.2f} m\n".format(self.bladeSize)
        text += "{0}/{1}\n".format(self.gridMod_i + 1, self.gridModelLen)
        text += "{0:.2f} deg\n".format(self.turbineAngle)
        text += "{0:.1f} deg\n".format(self.bladeTilt)
        text += "{0:.2f} m.s-1\n".format(self.windSpeed)
        text += "{0:.2f} rpm\n".format(self.turbSpeed)
        self.canv.create_text(textX, textY, anchor='nw', text=text, font=('Arial',12))
        
        
        textX, textY = 20, 0.05*self.height
        text = 'Grids definition\n'
        text += '    Turbine angle:\n'
        text += '    Wind speed:\n'
        text += '    Turbine speed:\n'
        text += '    Blade tilt angle:'
        self.canv.create_text(textX, textY, anchor='nw', text=text, font=('Arial',12))
        textX, textY = 20+130, 0.05*self.height
        text = '\n'
        text += '[{0:8.1f}, {1:8.1f}, {2:4d}] deg\n'.format(self.gridAngle_beg, self.gridAngle_end, self.gridAngle_num)
        if self.windGrid_enabled.get():
            text += '[{0:8.2f}, {1:8.2f}, {2:4d}] m.s-1\n'.format(self.gridWind_beg, self.gridWind_end, self.gridWind_num)
        else:
            text += '{0:.2f} m.s-1\n'.format(self.windSpeed)
        if self.turbGrid_enabled.get():
            text += '[{0:8.1f}, {1:8.1f}, {2:4d}] rpm\n'.format(self.gridTurbine_beg, self.gridTurbine_end, self.gridTurbine_num)
        else:
            text += '{0:.2f} rpm\n'.format(self.turbSpeed)
        if self.tiltGrid_enabled.get():
            text += '[{0:8.1f}, {1:8.1f}, {2:4d}] deg\n'.format(self.gridTilt_beg, self.gridTilt_end, self.gridTilt_num)
        else:
            text += '{0:.2f} deg\n'.format(self.bladeTilt)
        self.canv.create_text(textX, textY, anchor='nw', text=text, font=('Arial',12))
        
        textX, textY = 10, 0.6*self.height + 10
        RESLINEH = 20
        RESTXTOFFSET = 2
        RESCOLHEADERW = 140
        RESCOLW = 50
        self.canv.create_line(textX, textY, textX, textY + 5*RESLINEH)
        self.canv.create_line(textX + RESCOLHEADERW, textY, textX + RESCOLHEADERW, textY + 5*RESLINEH)
        self.canv.create_line(textX + RESCOLHEADERW + 1*RESCOLW, textY, textX + RESCOLHEADERW + 1*RESCOLW, textY + 5*RESLINEH)
        self.canv.create_line(textX + RESCOLHEADERW + 2*RESCOLW, textY, textX + RESCOLHEADERW + 2*RESCOLW, textY + 5*RESLINEH)
        self.canv.create_line(textX + RESCOLHEADERW + 3*RESCOLW, textY, textX + RESCOLHEADERW + 3*RESCOLW, textY + 5*RESLINEH)
        self.canv.create_line(textX + RESCOLHEADERW + 4*RESCOLW, textY, textX + RESCOLHEADERW + 4*RESCOLW, textY + 5*RESLINEH)
        self.canv.create_line(textX, textY, textX + RESCOLHEADERW + 4*RESCOLW, textY)
        self.canv.create_line(textX, textY + 1*RESLINEH, textX + RESCOLHEADERW + 4*RESCOLW, textY + 1*RESLINEH)
        self.canv.create_line(textX, textY + 2*RESLINEH, textX + RESCOLHEADERW + 4*RESCOLW, textY + 2*RESLINEH)
        self.canv.create_line(textX, textY + 3*RESLINEH, textX + RESCOLHEADERW + 4*RESCOLW, textY + 3*RESLINEH)
        self.canv.create_line(textX, textY + 4*RESLINEH, textX + RESCOLHEADERW + 4*RESCOLW, textY + 4*RESLINEH)
        self.canv.create_line(textX, textY + 5*RESLINEH, textX + RESCOLHEADERW + 4*RESCOLW, textY + 5*RESLINEH)
        
        self.canv.create_text(textX + RESTXTOFFSET, textY+RESTXTOFFSET, text='RESULTS', anchor='nw')
        self.canv.create_text(textX + RESTXTOFFSET, textY+RESTXTOFFSET + 1*RESLINEH, text='Effective surface (m2)', anchor='nw')
        self.canv.create_text(textX + RESTXTOFFSET, textY+RESTXTOFFSET + 2*RESLINEH, text='Lift force (kg.m.s-2)', anchor='nw')
        self.canv.create_text(textX + RESTXTOFFSET, textY+RESTXTOFFSET + 3*RESLINEH, text='Drag force (kg.m.s-2)', anchor='nw')
        self.canv.create_text(textX + RESTXTOFFSET, textY+RESTXTOFFSET + 4*RESLINEH, text='Torque contr. (kg.m2.s-2)', anchor='nw')
        self.canv.create_text(textX + RESTXTOFFSET + RESCOLHEADERW, textY+RESTXTOFFSET, text='Blade 1', anchor='nw')
        self.canv.create_text(textX + RESTXTOFFSET + RESCOLHEADERW + 1*RESCOLW, textY+RESTXTOFFSET, text='Blade 2', anchor='nw')
        self.canv.create_text(textX + RESTXTOFFSET + RESCOLHEADERW + 2*RESCOLW, textY+RESTXTOFFSET, text='Blade 3', anchor='nw')
        self.canv.create_text(textX + RESTXTOFFSET + RESCOLHEADERW + 3*RESCOLW, textY+RESTXTOFFSET, text='Total', anchor='nw')
        
        self.canv.create_text(textX + RESTXTOFFSET + RESCOLHEADERW, textY+RESTXTOFFSET + 1*RESLINEH, text='{0:.2f}'.format(self.S1), anchor='nw')
        self.canv.create_text(textX + RESTXTOFFSET + RESCOLHEADERW + 1*RESCOLW, textY+RESTXTOFFSET + 1*RESLINEH, text='{0:.2f}'.format(self.S2), anchor='nw')
        self.canv.create_text(textX + RESTXTOFFSET + RESCOLHEADERW + 2*RESCOLW, textY+RESTXTOFFSET + 1*RESLINEH, text='{0:.2f}'.format(self.S3), anchor='nw')
        self.canv.create_text(textX + RESTXTOFFSET + RESCOLHEADERW + 3*RESCOLW, textY+RESTXTOFFSET + 1*RESLINEH, text='{0:.2f}'.format(self.S1 + self.S2 + self.S3), anchor='nw')
        self.canv.create_text(textX + RESTXTOFFSET + RESCOLHEADERW, textY+RESTXTOFFSET + 2*RESLINEH, text='{0:.2f}'.format(self.fL1), anchor='nw')
        self.canv.create_text(textX + RESTXTOFFSET + RESCOLHEADERW + 1*RESCOLW, textY+RESTXTOFFSET + 2*RESLINEH, text='{0:.2f}'.format(self.fL2), anchor='nw')
        self.canv.create_text(textX + RESTXTOFFSET + RESCOLHEADERW + 2*RESCOLW, textY+RESTXTOFFSET + 2*RESLINEH, text='{0:.2f}'.format(self.fL3), anchor='nw')
        self.canv.create_text(textX + RESTXTOFFSET + RESCOLHEADERW, textY+RESTXTOFFSET + 3*RESLINEH, text='{0:.2f}'.format(self.fD1), anchor='nw')
        self.canv.create_text(textX + RESTXTOFFSET + RESCOLHEADERW + 1*RESCOLW, textY+RESTXTOFFSET + 3*RESLINEH, text='{0:.2f}'.format(self.fD2), anchor='nw')
        self.canv.create_text(textX + RESTXTOFFSET + RESCOLHEADERW + 2*RESCOLW, textY+RESTXTOFFSET + 3*RESLINEH, text='{0:.2f}'.format(self.fD3), anchor='nw')
        self.canv.create_text(textX + RESTXTOFFSET + RESCOLHEADERW, textY+RESTXTOFFSET + 4*RESLINEH, text='{0:.2f}'.format(self.M1), anchor='nw')
        self.canv.create_text(textX + RESTXTOFFSET + RESCOLHEADERW + 1*RESCOLW, textY+RESTXTOFFSET + 4*RESLINEH, text='{0:.2f}'.format(self.M2), anchor='nw')
        self.canv.create_text(textX + RESTXTOFFSET + RESCOLHEADERW + 2*RESCOLW, textY+RESTXTOFFSET + 4*RESLINEH, text='{0:.2f}'.format(self.M3), anchor='nw')
        self.canv.create_text(textX + RESTXTOFFSET + RESCOLHEADERW + 3*RESCOLW, textY+RESTXTOFFSET + 4*RESLINEH, text='{0:.2f}'.format(self.M1 + self.M2 + self.M3), anchor='nw')
        
        # if self.DEBUGGING and self.running:
        #     self.plotX.append(self.turbineAngle)
        #     self.plotY.append(self.theta1)
        
        
        self.create_plot(textX + RESCOLHEADERW + 4*RESCOLW + 10, 0.6*self.height+2, self.width-4 - (textX + RESCOLHEADERW + 4*RESCOLW), 0.4*self.height-4, 
                         self.plotX, self.plotY, 
                         axXlim_=[-2, 362],
                         axXlabel='Turbine angle (deg)', axYlabel='Turbine torque (kg.m2.s-2)')
            
            
    
    def create_plot(self, figX, figY, figW, figH, plotX, plotY,
                    padn=15, pads=47, padw=47, pade=15,
                    axXlim_=None, axYlim_=None,
                    axXlabel=None, axYlabel=None
                    ):
        axX = figX + padw
        axY = figY + padn
        axW = figW - padw - pade
        axH = figH - padn - pads
        labelX = 'Label X'
        labelY = 'Label Y'
        markerSize = 2
        markerlc = 'black'
        markerbg = 'blue'
        tickerInterval = [5.0e3, 2.5e3, 1.0e3,
                          5.0e2, 2.5e2, 1.0e2,
                          5.0e1, 2.5e1, 1.0e1,
                          5.0e0, 2.5e0, 1.0e0,
                          5.0e-1, 2.5e-1, 1.0e-1,
                          5.0e-2, 2.5e-2, 1.0e-2
                          ]
        tickerId = 0
        
        if axXlim_ is None:
            if len(plotX) == 0:
                axXlim = [0, 1]
            elif len(plotX) == 1:
                axXlim = [plotX[0] - 0.1, plotX[0] + 0.1]
            else:
                lim = max(plotX) - min(plotX)
                axXlim = [min(plotX) - 0.25*lim, max(plotX) + 0.25*lim]
        else:
            axXlim = axXlim_
        if axYlim_ is None:
            if len(plotY) == 0:
                axYlim = [0, 1]
            elif len(plotY) == 1 or (len(plotY)>1 and max(plotY) - min(plotY) < 0.2):
                axYlim = [plotY[0] - 0.1, plotY[0] + 0.1]
            else:
                lim = max(plotY) - min(plotY)
                axYlim = [min(plotY) - 0.25*lim, max(plotY) + 0.25*lim]
        else:
            axYlim = axYlim_
            
        if not axXlabel is None:
            labelX = axXlabel
        if not axYlabel is None:
            labelY = axYlabel
        
        # set the ticker for X label
        tickX = []
        tickXint = 0
        for i in range(len(tickerInterval)):
            tickXint = tickerInterval[i]
            firstTick = (axXlim[0] - axXlim[0]%tickerInterval[i]) + tickerInterval[i]
            if firstTick + 2*tickerInterval[i] < axXlim[1]:
                tickX = np.arange(firstTick, axXlim[1], step=tickerInterval[i])
                break
        # set the ticker for X label
        tickY = []
        tickYint = 0
        for i in range(len(tickerInterval)):
            tickYint = tickerInterval[i]
            firstTick = (axYlim[0] - axYlim[0]%tickerInterval[i]) + tickerInterval[i]
            if firstTick + 2*tickerInterval[i] < axYlim[1]:
                tickY = np.arange(firstTick, axYlim[1], step=tickerInterval[i])
                break
        
        self.canv.create_rectangle(axX, axY, axX + axW, axY + axH, fill='white')
        self.canv.create_text(axX + axW/2, axY + axH + 25, text=labelX, anchor='n')
        self.canv.create_text(axX - 25, axY + axH/2, text=labelY, anchor='s', angle=90)
        if len(tickX) > 0:
            for t in tickX:
                X = axX + (t-axXlim[0])/(axXlim[1]-axXlim[0])*axW
                self.canv.create_line(X, axY+axH, X, axY+axH+3)
                if tickXint >= 10:
                    tx = '{0:d}'.format(int(t))
                elif tickXint >= 1:
                    tx = '{0:.1f}'.format(t)
                elif tickXint >= 1e-1:
                    tx = '{0:.2f}'.format(t)
                elif tickXint >= 1e-2:
                    tx = '{0:.3f}'.format(t)
                else:
                    tx = '{0:.1e}'.format(t)
                self.canv.create_text(X, axY+axH+5, text=tx, anchor='n')
        if len(tickY) > 0:
            for t in tickY:
                Y = axY + axH - (t-axYlim[0])/(axYlim[1]-axYlim[0])*axH
                self.canv.create_line(axX, Y, axX-3, Y)
                if tickYint >= 10:
                    tx = '{0:d}'.format(int(t))
                elif tickYint >= 1:
                    tx = '{0:.1f}'.format(t)
                elif tickYint >= 1e-1:
                    tx = '{0:.2f}'.format(t)
                elif tickYint >= 1e-2:
                    tx = '{0:.3f}'.format(t)
                else:
                    tx = '{0:.1e}'.format(t)
                self.canv.create_text(axX-5, Y, text=tx, anchor='s', angle=90)
        
        if len(plotX) > 0:
            for i in range(len(plotX)):
                markX = axX + (plotX[i]-axXlim[0])/(axXlim[1]-axXlim[0])*axW
                markY = axY + axH - (plotY[i]-axYlim[0])/(axYlim[1]-axYlim[0])*axH
                self.canv.create_oval(markX - markerSize, markY - markerSize, markX + markerSize, markY + markerSize, outline=markerlc, fill=markerbg)
        
        
        
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
    
    
    def geoBlade(self):
        vT = 2*np.pi/60.0 * self.turbSpeed * self.turbineRadius
        vTx = vT * np.cos((self.turbineAngle) / 180.0 * np.pi + np.pi/2)
        vTy = vT * np.sin((self.turbineAngle) / 180.0 * np.pi + np.pi/2)
        self.veffx1 = vTx - self.windSpeed
        self.veffy1 = vTy
        theta_T = self.arctan(vTx, vTy)
        theta_eff = self.arctan(self.veffx1, self.veffy1)
        self.theta1 = -90.0+self.turbineAngle  - theta_eff*180/np.pi - 180.0 + self.bladeTilt
        self.theta1 = (-self.theta1+180)%360 - 180
        # self.veff1 = np.sqrt(veffx**2 + veffy**2)
        
        vT = 2*np.pi/60.0 * self.turbSpeed * self.turbineRadius
        vTx = vT * np.cos((self.turbineAngle+120) / 180.0 * np.pi + np.pi/2)
        vTy = vT * np.sin((self.turbineAngle+120) / 180.0 * np.pi + np.pi/2)
        self.veffx2 = vTx - self.windSpeed
        self.veffy2 = vTy
        theta_T = self.arctan(vTx, vTy)
        theta_eff = self.arctan(self.veffx2, self.veffy2)
        self.theta2 = -90.0+self.turbineAngle+120  - theta_eff*180/np.pi - 180.0 + self.bladeTilt
        self.theta2 = (-self.theta2+180)%360 - 180
        # self.veff2 = np.sqrt(veffx**2 + veffy**2)
        
        vT = 2*np.pi/60.0 * self.turbSpeed * self.turbineRadius
        vTx = vT * np.cos((self.turbineAngle+240) / 180.0 * np.pi + np.pi/2)
        vTy = vT * np.sin((self.turbineAngle+240) / 180.0 * np.pi + np.pi/2)
        self.veffx3 = vTx - self.windSpeed
        self.veffy3 = vTy
        theta_T = self.arctan(vTx, vTy)
        theta_eff = self.arctan(self.veffx3, self.veffy3)
        self.theta3 = -90.0+self.turbineAngle+240  - theta_eff*180/np.pi - 180.0 + self.bladeTilt
        self.theta3 = (-self.theta3+180)%360 - 180
        # self.veff3 = np.sqrt(veffx**2 + veffy**2)
        


    def debugPlotBlade(self):
        '''
        This function tests the calculation of the torque on one blade,
        using the default foiler profile and the default values for the 
        blade angle, the wind speed, and the turbine speed.
        The function plot directly the variation of the attack angle,
        the air flow speed felt by the blade and the different contributions 
        of the force to the momentum with respect to the turbine angle,
        from 0 to 360 degrees.
        '''
        angle = np.linspace(0, 360, num=360)
        attack = np.zeros_like(angle)
        veff = np.zeros_like(angle)
        fL = np.zeros_like(angle)
        fD = np.zeros_like(angle)
        M = np.zeros_like(angle)
        S = np.zeros_like(angle)
        cz = np.zeros_like(angle)
        cx = np.zeros_like(angle)
        
        fig, ax = plt.subplots(figsize=(5, 8), nrows=2, sharex=True)
        # print(self.foilerHandler.angle)
        ax[0].scatter(self.foilerHandler.angle, self.foilerHandler.cl, s=16, color='black', linewidth=0.5)
        ax[1].scatter(self.foilerHandler.angle, self.foilerHandler.cd, s=16, color='black', linewidth=0.5)
        for i in range(2):
            ylim = ax[i].get_ylim()
            ax[i].plot([90, 90], list(ylim), linewidth=0.5, linestyle='dashed', color='black')
            ax[i].plot([180, 180], list(ylim), linewidth=0.5, linestyle='dashed', color='black')
            ax[i].plot([270, 270], list(ylim), linewidth=0.5, linestyle='dashed', color='black')
            ax[i].set_ylim(ylim)
        ax[1].set_xlim(0, 360)
        ax[1].set_xlabel('Angle (degree)', fontsize=12)
        ax[0].set_ylabel('Cl coefficient', fontsize=12)
        ax[1].set_ylabel('cd coefficient', fontsize=12)
        fig.tight_layout()
            
        for i in range(len(angle)):
            self.turbineAngle = angle[i]
            self.geoBlade()
            attack[i] = self.theta1
            veff[i] = np.sqrt(self.veffx1**2 + self.veffy1**2)
            fL[i], fD[i], M[i], S[i], cz[i], cx[i] = self.foilerHandler.computeLiftDrag(self.theta1, self.veffx1, self.veffy1, self.turbineAngle, self.turbineRadius)
        
            
        fig, ax = plt.subplots(figsize=(11, 9), nrows=3, ncols=3, sharex=True)
        ax[0][0].scatter(angle, attack, marker='o', s=16, color='blue', linewidth=0.5)
        ax[1][0].scatter(angle, veff, marker='o', s=16, color='blue', linewidth=0.5)
        ax[2][0].scatter(angle, S, marker='o', s=16, color='blue', linewidth=0.5)
        ax[0][1].scatter(angle, cz, marker='o', s=16, color='blue', linewidth=0.5)
        ax[0][2].scatter(angle, cx, marker='o', s=16, color='blue', linewidth=0.5)
        ax[1][1].scatter(angle, fL, marker='o', s=16, color='red', linewidth=0.5)
        ax[1][2].scatter(angle, fD, marker='o', s=16, color='red', linewidth=0.5)
        ax[2][1].scatter(angle, M, marker='o', s=16, color='red', linewidth=0.5)
        
        ax[2][1].set_xlabel('Turbine angle (degree)', fontsize=12)
        ax[0][0].set_ylabel('Attack angle (degree)', fontsize=12)
        ax[1][0].set_ylabel('Effective speed (m.s-1)', fontsize=12)
        ax[2][0].set_ylabel('Effective surface (m2)', fontsize=12)
        ax[0][1].set_ylabel('Cz coefficient', fontsize=12)
        ax[0][2].set_ylabel('Cx coefficient', fontsize=12)
        ax[1][1].set_ylabel('Lift force (kg.m.s-2)', fontsize=12)
        ax[1][2].set_ylabel('Drag force (kg.m.s-2)', fontsize=12)
        ax[2][1].set_ylabel('Momentum (kg.m2.s-2)', fontsize=12)
        
        for i in range(3):
            for j in range(3):
                ylim = ax[i][j].get_ylim()
                ax[i][j].plot([90, 90], list(ylim), linewidth=0.5, linestyle='dashed', color='black')
                ax[i][j].plot([180, 180], list(ylim), linewidth=0.5, linestyle='dashed', color='black')
                ax[i][j].plot([270, 270], list(ylim), linewidth=0.5, linestyle='dashed', color='black')
                ax[i][j].set_ylim(ylim)
        # ylim = ax[1][0].get_ylim()
        # ax[1][0].plot([90, 90], list(ylim), linewidth=0.5, linestyle='dashed', color='black')
        # ax[1][0].plot([180, 180], list(ylim), linewidth=0.5, linestyle='dashed', color='black')
        # ax[1][0].plot([270, 270], list(ylim), linewidth=0.5, linestyle='dashed', color='black')
        # ax[1][0].set_ylim(ylim)
        ax[0][0].set_xlim((0, 360))
        fig.tight_layout()
            
        self.turbineAngle = 0
        
        
if __name__ == "__main__":
    app = AppliCanevas()
    app.title("Gridded SPH simulation")
    app.mainloop()
