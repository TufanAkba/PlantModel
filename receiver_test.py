#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 25 00:50:51 2022

@author: tufanakba
this code for running the receiver for given conditions
inputs = rpc, ins, L, Tfo, Tfi, m_dot
rest of the parameters should not be change for surrogate model algorithm

"""

import openmdao.api as om
import numpy as np
from receiver import Receiver

from components.draw_contour import draw_contour

def test(rpc,ins,L,Tfi,m_dot,mesh):
    
    p = om.Problem()
    
    
    p.model.add_subsystem('receiver', Receiver(disc_z=mesh,
                                               disc_SiC=int(mesh/2),
                                               disc_RPC=mesh,
                                               disc_INS=int(mesh/2)))
    
    p.setup()
    
    #set inputs
    
    # surrogate optimization results
    # rpc = .00785298
    # ins = .09976585
    # L = .07252483
    Tfi = 300.
    m_dot = .00066
    
    p.set_val('receiver.s_RPC',rpc, units='m')
    p.set_val('receiver.s_INS',ins, units='m')
    p.set_val('receiver.L',L, units='m')
    
    p.set_val('receiver.T_fluid_in',Tfi, units='K')
    
    p.set_val('receiver.Mass_Flow', m_dot, units='kg/s')
    
    p.run_model()
    
    z_n = p.get_val('receiver.z_n')
    r_n = p.get_val('receiver.r_n')
    T = p.get_val('receiver.T').reshape(44,22)
    
    r_1 = 0.015
    s_SiC = 0.005
    
    draw_contour(z_n[0,:], r_n[:,0], T-273, r_1+s_SiC, r_1+s_SiC+rpc, m_dot, 10)
    
    Tf_out= p.get_val('receiver.T_fluid_out')
    if Tf_out<1273:
        print(f'failed : {Tf_out-273}')
    print(f'Mass_Flow: {m_dot}')
    print(f'Tf_out: {Tf_out}K')
    print('efficiency:',p.get_val('receiver.eff_S2G'))
    
    return Tf_out-273.15


if __name__ == "__main__":
    
    
    
    #set inputs
    # first try
    Tfi = 300.
    m_dot = .00066
    
    #mesh conv.
    rpc = .01
    ins = .08
    L = .065
    
    # response surface
    rpc = .00860
    ins = .0995
    L = .0729
    
    # # gradient based results
    # rpc = .0109
    # ins = .0786
    # L = .0630
    
    # krigin
    rpc = .0135
    ins = .0853
    L = .0807
    
    Tf_out = test(rpc,ins,L,Tfi,m_dot,mesh = 20)
    
    # mesh = [8, 10, 16, 20 , 32, 40, 50]
    # Tf_out = []
    # for i in  mesh:
    #     Tf_out.append(test(rpc,ins,L,Tfi,m_dot,mesh = i))
    
    # print(Tf_out)
