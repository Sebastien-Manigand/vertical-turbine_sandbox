# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 13:43:17 2020

@author: sebas
"""


import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'serif'


ang = []
wSp = []
tSp = []
bTi = []
tor = []
efs = []
Nang = 0
Nwsp = 0
Ntsp = 0
Nbti = 0
f = open('turbine-output.dat', 'r')
for l in f.readlines():
    if l[0] != '#':
        b = l.strip().split(' ')
        while '' in b:
            b.remove('')
        ang.append(float(b[0]))
        wSp.append(float(b[1]))
        tSp.append(float(b[2]))
        bTi.append(float(b[3]))
        tor.append(float(b[4]))
        efs.append(float(b[5]))
    elif l[0:25] == '#  0 - Turbine angle:    ':
        Nang = int(l[25:].strip())
    elif l[0:25] == '#  1 - Wind speed:       ':
        Nwsp = int(l[25:].strip())
    elif l[0:25] == '#  2 - Turbine speed:    ':
        Ntsp = int(l[25:].strip())
    elif l[0:25] == '#  3 - Blade tilt angle: ':
        Nbti = int(l[25:].strip())
    
print('N angle: {0}'.format(Nang))
print('N wind:  {0}'.format(Nwsp))
print('N turb:  {0}'.format(Ntsp))
print('N tilt:  {0}'.format(Nbti))
        
ang = np.array(ang).reshape((Nwsp, Ntsp, Nbti, Nang))
wSp = np.array(wSp).reshape((Nwsp, Ntsp, Nbti, Nang))
tSp = np.array(tSp).reshape((Nwsp, Ntsp, Nbti, Nang))
bTi = np.array(bTi).reshape((Nwsp, Ntsp, Nbti, Nang))
# wSp = np.array(wSp).reshape((Nang, Nwsp, Ntsp, Nbti))
# tSp = np.array(tSp).reshape((Nang, Nwsp, Ntsp, Nbti))
# bTi = np.array(bTi).reshape((Nang, Nwsp, Ntsp, Nbti))
print(ang.shape)


tor = np.average(np.array(tor).reshape((Nwsp, Ntsp, Nbti, Nang)), axis=3)
efs = np.average(np.array(efs).reshape((Nwsp, Ntsp, Nbti, Nang)), axis=3)
wSp = np.average(wSp, axis=3)
tSp = np.average(tSp, axis=3)
bTi = np.average(bTi, axis=3)


fig, ax = plt.subplots(figsize=(9, 8))
X = tSp[8,:,:].ravel()
Y = bTi[8,:,:].ravel()
Z = tor[8,:,:].ravel()
h, xe, ye, im = ax.hist2d(X, Y, bins=(Ntsp, Nbti), weights=Z, cmap='jet')
ax.set_xlabel('Turbine speed (r.p.m.)', fontsize=12)
ax.set_ylabel('Blade tilt angle (degree)', fontsize=12)
# Create colorbar
cbar = fig.colorbar(im, ax=ax)
cbar.ax.set_ylabel('Turbine torque (kg.m2.s-2)', rotation=90, va="top", fontsize=12)
fig.tight_layout()

fig.savefig("avgTorque_tspeed-tilt.pdf")
fig.savefig("avgTorque_tspeed-tilt.png", dpi=150)


fig, ax = plt.subplots(figsize=(9, 8))
X = tSp[:,:,0].ravel()
Y = wSp[:,:,0].ravel()
Z = tor[:,:,0].ravel()
h, xe, ye, im = ax.hist2d(X, Y, bins=(Ntsp, Nwsp), weights=Z, cmap='jet')
ax.set_xlabel('Turbine speed (r.p.m.)', fontsize=12)
ax.set_ylabel('Wind speed (m.s-1)', fontsize=12)
# Create colorbar
cbar = fig.colorbar(im, ax=ax)
cbar.ax.set_ylabel('Turbine torque (kg.m2.s-2)', rotation=90, va="top", fontsize=12)
fig.tight_layout()

fig.savefig("avgTorque_tspeed-wspeed.pdf")
fig.savefig("avgTorque_tspeed-wspeed.png", dpi=150)











