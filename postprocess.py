#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 21 19:24:44 2021

@author: tufanakba
"""

import openmdao.api as om
from draw_contour import draw_contour
from math import pi
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "times"

# Instantiate your CaseReader
cr = om.CaseReader("cases.sql")

solver_cases = cr.list_cases('root.receiver.nonlinear_solver', out_stream=None)
driver_cases = cr.list_cases('driver', recurse=False);

case = cr.get_case('final_state')
    
r_1 = case.get_val('receiver.r_1')
s_SiC = case.get_val('receiver.s_SiC')
s_RPC = case.get_val('receiver.s_RPC')
z_n = case.get_val('receiver.z_n')
r_n = case.get_val('receiver.r_n')
T = case.get_val('receiver.T').reshape(44,22)
Mass_Flow = case.get_val('receiver.Mass_Flow')
draw_contour(z_n[0,:], r_n[:,0], T-273, r_1+s_SiC, r_1+s_SiC+s_RPC, Mass_Flow, 10)

s_INS = case.get_val('receiver.s_INS')
L = case.get_val('receiver.L')
vol_fin = pi * (r_1+s_SiC+s_RPC+s_INS)**2 * L

r_1 = 0.015
s_SiC = 0.005
s_RPC = 0.015
s_INS  = 0.1
L = 0.065
vol = pi * (r_1+s_SiC+s_RPC+s_INS)**2 * L

print(f'Volume Reduction: {100*(1-vol_fin/vol)}%')
print('-------------------------------------')
last_case = cr.get_case(driver_cases[-1])

objectives = last_case.get_objectives(scaled=False)
design_vars = last_case.get_design_vars(scaled=False)
constraints = last_case.get_constraints(scaled=False)

print('objective')
print(objectives['receiver.eff_S2G'])
print('design_vars')
print('Mass Flow')
print(design_vars['receiver.Mass_Flow'])
print('L')
print(design_vars['receiver.L'])
print('SiC,RPC,INS')
print(design_vars['receiver.s_SiC'])
print(design_vars['receiver.s_RPC'])
print(design_vars['receiver.s_INS'])
print('constraints')
print('Outer surface [K]')
print(np.max(constraints['receiver.T']))
print('T_fluid_out [K]')
print(constraints['receiver.T_fluid_out'])
print('Volume [m**3]')
print(constraints['receiver.Volume'])
print('-------------------------------------')

# print(cr.list_source_vars('root.receiver'))

# List driver cases (do not recurse to system/solver cases, suppress display)
comp_cases = cr.list_cases('root.receiver', recurse=False, out_stream=None)

# Plot the path the design variables took to convergence
# Note that there are two lines in the right plot because "Z"
# contains two variables that are being optimized

for case_id in comp_cases:
    case = cr.get_case(case_id)
    r_1 = case.get_val('receiver.init.r_1')
    s_SiC = case.get_val('receiver.init.s_SiC')
    s_RPC = case.get_val('receiver.init.s_RPC')
    z_n = case.get_val('receiver.solid.z_n')
    r_n = case.get_val('receiver.solid.r_n')
    T = case.get_val('receiver.T').reshape(44,22)
    Mass_Flow = case.get_val('receiver.Mass_Flow')
    draw_contour(z_n[0,:], r_n[:,0], T-273, r_1+s_SiC, r_1+s_SiC+s_RPC, Mass_Flow, 10)



dv_x_values = []
dv_z_values = []
dv_eff_values = []

sic_values = []
rpc_values = []
ins_values = []

volume = []
T_outer = []
T_fluid_out = []

for case_id in driver_cases:
    case = cr.get_case(case_id)
    design_vars = case.get_design_vars(scaled=False)
    objectives = case.get_objectives(scaled=False)
    constraints = case.get_constraints(scaled=False)
    dv_x_values.append(design_vars['receiver.Mass_Flow'])
    dv_z_values.append(design_vars['receiver.L'])
    dv_eff_values.append(objectives['receiver.eff_S2G'])
    
    sic_values.append(design_vars['receiver.s_SiC'])
    rpc_values.append(design_vars['receiver.s_RPC'])
    ins_values.append(design_vars['receiver.s_INS'])
    
    volume.append(constraints['receiver.Volume'])
    T_outer.append(np.max(constraints['receiver.T'])-273)
    T_fluid_out.append(constraints['receiver.T_fluid_out']-273)

fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=1.0, hspace=None)
ax1.plot(np.arange(len(dv_x_values)), np.array(np.absolute(dv_x_values)))
ax1.set(xlabel='Iterations', ylabel='Mass Flow', title='Opt. History')
ax1.grid()
ax2.plot(np.arange(len(dv_z_values)), np.array(dv_z_values))
ax2.set(xlabel='Iterations', ylabel='Receiver Length', title='Opt. History')
ax2.grid()
ax3.plot(np.arange(len(dv_eff_values)), np.array(dv_eff_values))
ax3.set(xlabel='Iterations', ylabel='Efficiency', title='Opt. History')
ax3.grid()
plt.savefig('objective.pdf') 
plt.show()



fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=1.0, hspace=None)
ax1.plot(np.arange(len(sic_values)), np.array(np.absolute(sic_values)))
ax1.set(xlabel='Iterations', ylabel='CAV', title='Cavity Thickness')
ax1.ticklabel_format(useOffset=False, style='plain')
ax1.grid()
ax2.plot(np.arange(len(rpc_values)), np.array(rpc_values))
ax2.set(xlabel='Iterations', ylabel='RPC', title='RPC Thickness')
ax2.grid()
ax3.plot(np.arange(len(ins_values)), np.array(ins_values))
ax3.set(xlabel='Iterations', ylabel='INS', title='INS Thickness')
ax3.grid()
plt.savefig('thickness.pdf') 
plt.show()

fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=1.0, hspace=None)
ax1.plot(np.arange(len(volume)), np.array(volume))
ax1.plot(np.arange(len(volume)),np.ones(len(volume))*0.0038)
ax1.set(xlabel='Iterations', ylabel='Volume', title='Volume Const.')
ax1.ticklabel_format(useOffset=False, style='plain')
ax1.grid()
ax2.plot(np.arange(len(T_outer)), np.array(T_outer))
ax2.plot(np.arange(len(T_outer)),np.ones(len(T_outer))*100)
ax2.plot()
ax2.set(xlabel='Iterations', ylabel='T_outer', title='Insulator Const.')
ax2.grid()
ax3.plot(np.arange(len(T_fluid_out)), np.array(T_fluid_out))
ax3.plot(np.arange(len(T_fluid_out)),np.ones(len(T_fluid_out))*1000)
ax3.set(xlabel='Iterations', ylabel='T_fluid', title='Outlet Fluid Temp.')
ax3.grid()
plt.savefig('constraints.pdf') 
plt.show()


fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6,1, figsize=(5,12.5),dpi=100)
fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=None)
ax1.plot(np.arange(len(sic_values)), np.array(np.absolute(sic_values)))
ax1.set(ylabel='Cavity Thickness')
ax1.ticklabel_format(useOffset=False, style='plain')
# ax1.set_ylim(0.0048,0.0052)
ax1.grid()
ax2.plot(np.arange(len(rpc_values)), np.array(rpc_values))
ax2.set(ylabel='RPC Thickness')
ax2.ticklabel_format(useOffset=False, style='plain')
# ax2.set_ylim(0.0144,0.0156)
ax2.grid()
ax3.plot(np.arange(len(ins_values)), np.array(ins_values))
ax3.set(ylabel='INS Thickness')
ax3.ticklabel_format(useOffset=False, style='plain')
# ax3.set_ylim(0.096,0.104)
ax3.grid()
ax4.plot(np.arange(len(dv_x_values)), np.array(np.absolute(dv_x_values)))
ax4.set(ylabel='Mass Flow')
# ax4.set_ylim(0.000676,0.000624)
ax4.grid()
ax5.plot(np.arange(len(dv_z_values)), np.array(dv_z_values))
ax5.set(ylabel='Receiver Length')
# ax5.set_ylim(0.0624,0.0676)
ax5.grid()
ax6.plot(np.arange(len(dv_eff_values)), np.array(dv_eff_values))
ax6.set(xlabel='Iterations', ylabel='Efficiency')
ax6.grid()
plt.tight_layout(pad=1.5)
# fig.suptitle('Optimization History')
plt.savefig('results.pdf') 
plt.show()


# Plot the convergence of the two coupling variables (last 35 iterations)
# y1_history = []
# y2_history = []

# for case_id in solver_cases[-100:]:#4500 for seeing the pattern
#     case = cr.get_case(case_id)
#     y1_history.append(case['receiver.T_BP'])
#     y2_history.append(case['receiver.T_corner'])

# iterations = np.arange(-len(y1_history), 0, 1)

# fig, (ax1, ax2) = plt.subplots(2, 1)
# fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.65)

# ax1.plot(iterations, np.array(y1_history))
# ax1.set(ylabel='Coup. Output: T_BP', title='Solver History')
# ax1.grid()

# ax2.plot(iterations, np.array(y2_history))
# ax2.set(ylabel='Coup. Output: T_corner', xlabel='Iterations')
# ax2.grid()

# plt.show()

# Get the final values
case = cr.get_case(solver_cases[-1])
print('T_BP')
print(case['receiver.T_BP'])
print('T_corner')
print(case['receiver.T_corner'])

print(f"Number of cases: {len(solver_cases)}")