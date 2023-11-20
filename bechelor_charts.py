import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import sys

#Refineing plots from bechelor thesis

#Power Curves Comparison 
U_wind = np.arange(0,23,1)
P_basic =  [0,0,0,0,7247,19342,34078,53010,76032,102338,129012,154213,175606,195911,209167,212674,211286,208135,204146,199744,194849,190126,184838]
P_activ =  [0,0,0,0,7247,19342,34630,57600,85900,116425,146025,175170,200800,200300,200300,199700,199680,198900,197500,195900,200500,197500,192800,]

P_basic_kW_list = []
P_activ_kW_list = []

for p in P_basic:
    element_b = 1e-03 * p 
    P_basic_kW_list.append(element_b)

for p in P_activ:
    element_a = 1e-03 * p 
    P_activ_kW_list.append(element_a)


# plt.plot(U_wind,P_basic_kW_list, marker='.')
# plt.plot(U_wind,P_activ_kW_list, marker='*')
# plt.title('Power curves comparison', fontsize="15")
# plt.legend(['Basic turbine', 'Active_geom_turbine'], loc='lower right',fontsize="12")
# plt.xlim(0,max(U_wind) + 0.5)
# plt.ylim(0,max(P_basic_kW_list)+ 5)
# plt.xlabel('Freestream Wind Velocity, m/s')
# plt.ylabel('Power, kW')
# plt.grid()
# plt.show()

#Weibull
def Weibul(k,Ua,c,U):
    return k * pow((Ua / c), k) * pow(U, k-1) * np.exp(-pow(Ua/c*U,k))

U_ave = 7
k = 2
c = 7.9

# plt.plot(U_wind, Weibul(k,U_ave,c,U_wind))
# plt.show(   )

#BAr chart

# turbines = ['Basic','Activ']
# energy = [5.80E+05,6.23E+05]

# plt.bar(turbines,energy,width=0.1)
# plt.show()



