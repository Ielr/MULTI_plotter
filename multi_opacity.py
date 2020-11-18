#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Program upload under: GNU General Public License v3.0  - 13 Nov. 2020
# inital author: G. Rigon (LULI)

####!/usr/bin/python3 -i
import numpy as np
import opacplot2 as op
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons, TextBox, Button
from matplotlib.ticker import LogFormatter

dir_name= '/home/rigong/.local/multi/Tables/Krypton/'
base_name= 'Krypton'
Znum= 36
Anum= 83.8

Kr= op.OpgMulti.open_file(dir_name, base_name)
Kr.toEosDict(Znum=Znum, Anum=Anum)

En= Kr['groups']
T0= np.exp((np.log(Kr['temp'].max()) + np.log(Kr['temp'].min()))/2)
rho0= np.exp((np.log(Kr['dens'].max()) + np.log(Kr['dens'].min()))/2)

test= op.OplGrid(Kr['dens'], Kr['temp'], Kr['groups'], lambda jd, jt: Kr['opp_mg'][jd, jt, :])

f= plt.figure()
ax= f.add_subplot(111)
plt.subplots_adjust(bottom=0.22, right=0.99, left=0.23)

l,= ax.plot((En[:-1]+En[1:])/2, test.interp(rho0, T0)) # dens T

ax.set_xlabel('Energy (eV)')
ax.set_ylabel('Opacity (cm$^2$/g)')
ax.loglog()

# Define Slider
axcolor = 'lightgoldenrodyellow'
axrho= plt.axes([0.23, 0.04, 0.6, 0.03], facecolor=axcolor)
rhoSl= Slider(axrho, r'$\rho$ (g/cc)', np.log10(Kr['dens'].min()), np.log10(Kr['dens'].max()), valinit= np.log10(rho0))
axT= plt.axes([0.23, 0.09, 0.6, 0.03], facecolor=axcolor)
TSl= Slider(axT, 'T (eV)', np.log10(Kr['temp'].min()), np.log10(Kr['temp'].max()), valinit= np.log10(T0))

textrho= ax.text(0.895, 0.045, ': %3.2e'%(rho0), fontsize= 10, transform= f.transFigure) # write the true value -> to work with a log slider scale
textT= ax.text(0.895, 0.095, ': %3.2e'%(T0), fontsize= 10, transform= f.transFigure)

# Update Slider and associate value
def update(val):
    rho= 10**(rhoSl.val)
    T= 10**(TSl.val)
    l.set_ydata(test.interp(rho, T))
    textrho.set_text(': %3.2e'%(rho)) # change the text value
    textT.set_text(': %3.2e'%(T))
    ax.relim() # update ax.dataLim
    ax.autoscale_view() # update ax.viewLim avec ax.dataLim
    f.canvas.draw_idle()

rhoSl.on_changed(update)
TSl.on_changed(update)

rax = plt.axes([0.01, 0.5, 0.12, 0.14], facecolor=axcolor)
radio = RadioButtons(rax, ('opp mg', 'opr mg', 'eps mg', 'emp mg'), active=0)

def new_opac(label):
    global test
    label1= {'opp mg':'opp_mg', 'opr mg':'opr_mg', 'eps mg':'eps_mg', 'emp mg':'emp_mg'}[label]
    test= op.OplGrid(Kr['dens'], Kr['temp'], Kr['groups'], lambda jd, jt: Kr[label1][jd, jt, :])
    ax.set_ylabel('Opacity ' + label +' (cm$^2$/g)')
    update(1)
radio.on_clicked(new_opac)

## Loading data
dirbox= plt.axes([0.1, 0.94, 0.8, 0.045])
dir_text= TextBox(dirbox, 'Directory:', initial= dir_name)
filebox= plt.axes([0.1, 0.89, 0.35, 0.045])
file_text= TextBox(filebox, 'File:', initial= base_name)
Zbox= plt.axes([0.55, 0.89, 0.07, 0.045])
Z_text= TextBox(Zbox, 'Znum:', initial= str(Znum))
Abox= plt.axes([0.75, 0.89, 0.07, 0.045])
A_text= TextBox(Abox, 'Anum:', initial= str(Anum))

Done= plt.axes([0.9, 0.89, 0.07, 0.045])
button= Button(Done, 'Load', color= axcolor, hovercolor='0.975')

def Load(event):
    global Kr
    global En
    Kr= op.OpgMulti.open_file(dir_text.text, file_text.text)
    Kr.toEosDict(Znum=int(Z_text.text), Anum=float(A_text.text))
    En= Kr['groups']
    T0= ((np.log(Kr['temp'].max()) + np.log(Kr['temp'].min()))/2)/np.log(10)
    rho0=((np.log(Kr['dens'].max()) + np.log(Kr['dens'].min()))/2)/np.log(10)
#    test= op.OplGrid(Kr['dens'], Kr['temp'], Kr['groups'], lambda jd, jt: Kr['opp_mg'][jd, jt, :])
    l.set_data((En[:-1]+En[1:])/2, En[:-1])
    TSl.valmin= np.log10(Kr['temp'].min())
    TSl.valmax= np.log10(Kr['temp'].max())
    TSl.valinit= T0
    TSl.set_val(T0)
    rhoSl.valmin= np.log10(Kr['dens'].min())
    rhoSl.valmax= np.log10(Kr['dens'].max())
    rhoSl.valinit= rho0
    rhoSl.set_val(rho0)
    new_opac(radio.value_selected)

button.on_clicked(Load)
f.show()
input('')
