#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  2 16:47:38 2022

@author: tufanakba
"""

import openmdao.api as om
from viewer2 import viewer, viewer2, map_plots, sankey
# from receiver import ReceiverSubProblem
from GenLP import MPComplex2
from MDAOMetaModel_Opt import surrOpt
import time
from mail import mail

from map_plotter2 import comp_map_all, turb_map_all

if __name__ == "__main__":
    
    # Design cond.s
    
    Q_Solar = 1000.
    T_4 = 1000.
    pwr_target = 170.
    alt = 1e-6
    fc_MN = 1e-6

    comp_eff = 0.83
    turb_eff = 0.86
    
    # Design Param.s start
    
    # s_RPC = 0.01
    # s_INS = 0.1
    # L = 0.035
    
    #optimal old
    # L = 0.07399128296774038
    # s_INS = 0.0935956711788761
    # s_RPC = 0.012720754242360544
    
    # L = 0.0728442745978244 m
    # INS = 0.09750373307761401 m 
    # RPC = 0.009870229483574647 m
    # mass_flow = 0.0008403087454728476 kg/s
    
    #optimal
    L = 0.0728442745978244
    s_INS = 0.09750373307761401
    s_RPC = 0.009870229483574647
    
    
    prob = om.Problem()
    mp_complex = prob.model = MPComplex2()

    prob.setup(check=False)
    
    prob.set_val('DESIGN'+'.rec.rec.s_RPC', s_RPC, units='m')
    prob.set_val('DESIGN'+'.rec.rec.s_INS', s_INS, units='m')
    prob.set_val('DESIGN'+'.rec.rec.L', L, units='m')
    #Define the design point
    prob.set_val('DESIGN.fc.alt', alt, units='ft')
    prob.set_val('DESIGN.fc.MN', fc_MN)
    
    prob.set_val('DESIGN.balance.pwr_target', pwr_target, units='W')
    prob.set_val('DESIGN.balance.T4_target', T_4, units='degC') 
    prob.set_val('DESIGN.LPcomp.PR', 2.0)
    prob.set_val('DESIGN.HPcomp.PR', 2.6)
    prob.set_val('DESIGN.HPcomp.eff', comp_eff)
    prob.set_val('DESIGN.HPturb.eff', turb_eff)
    prob.set_val('DESIGN.LPcomp.eff', comp_eff)
    prob.set_val('DESIGN.LPturb.eff', turb_eff)
    prob.set_val('DESIGN.rec.Q_Solar_In', Q_Solar, units='W')
    
    # initial guesses
    prob['DESIGN.balance.W'] = 0.002
    prob['DESIGN.balance.LPturb_PR'] = 1.5
    prob['DESIGN.balance.HPturb_PR'] = 6.7
    prob['DESIGN.fc.balance.Pt'] = 14.696
    prob['DESIGN.fc.balance.Tt'] = 518.67
    
    prob.set_solver_print(level=-1)
    prob.set_solver_print(level=2, depth=2)
    
    # st = time.time()
    # prob.run_model()
    # print("time", time.time() - st)
    
    for i,pt in enumerate(mp_complex.od_pts):

        prob[pt+'.fc.balance.Pt'] = 14.696
        prob[pt+'.fc.balance.Tt'] = 518.67
        
        # initial guesses
        
        # if pt == 'Max_105':
            
        #     prob[pt+'.balance.LP_Nmech'] = 15000
        #     prob[pt+'.balance.HP_Nmech'] = 25000
            
        #     prob[pt+'.balance.W'] = 0.0025
                         
        #     prob[pt+'.HPturb.PR'] = 10.9
        #     prob[pt+'.LPturb.PR'] = 3.5
        #     prob[pt+'.LPcomp.PR'] = 4.2 
        #     prob[pt+'.HPcomp.PR'] = 5.
        #     prob[pt+'.LPcomp.map.RlineMap'] = 2.0
        #     prob[pt+'.HPcomp.map.RlineMap'] = 2.0
            
        # if pt == 'Min_75':
            
        #     prob[pt+'.balance.LP_Nmech'] = 15000
        #     prob[pt+'.balance.HP_Nmech'] = 25000
            
        #     prob[pt+'.balance.W'] = 0.0014
                         
        #     prob[pt+'.HPturb.PR'] = 10.8
        #     prob[pt+'.LPturb.PR'] = 2.
        #     prob[pt+'.LPcomp.PR'] = 3.3 
        #     prob[pt+'.HPcomp.PR'] = 3.1 
        #     prob[pt+'.LPcomp.map.RlineMap'] = 2.0
        #     prob[pt+'.HPcomp.map.RlineMap'] = 2.0
        
        # if pt == 'SelfSupplied':
            
        #     prob[pt+'.balance.LP_Nmech'] = 16000
        #     prob[pt+'.balance.HP_Nmech'] = 26000
            
        #     prob[pt+'.balance.W'] = 0.0018
                         
        #     prob[pt+'.HPturb.PR'] = 11.
        #     prob[pt+'.LPturb.PR'] = 2.
        #     prob[pt+'.LPcomp.PR'] = 5.7
        #     prob[pt+'.HPcomp.PR'] = 2.7 
        #     prob[pt+'.LPcomp.map.RlineMap'] = 1.2
        #     prob[pt+'.HPcomp.map.RlineMap'] = 2.
            
        # if pt == 'Motoring':
            
        #     prob[pt+'.balance.LP_Nmech'] = 16294
        #     prob[pt+'.balance.HP_Nmech'] = 25194
            
        #     prob[pt+'.balance.W'] = 0.00145
                         
        #     prob[pt+'.HPturb.PR'] = 10.578
        #     prob[pt+'.LPturb.PR'] = 1.982
        #     prob[pt+'.LPcomp.PR'] = 6.256
        #     prob[pt+'.HPcomp.PR'] = 1.849
        #     prob[pt+'.LPcomp.map.RlineMap'] = 1.
        #     prob[pt+'.HPcomp.map.RlineMap'] = 2.357
            
        prob[pt+'.balance.LP_Nmech'] = 15000
        prob[pt+'.balance.HP_Nmech'] = 25000
        
        prob[pt+'.balance.W'] = 0.00154
                    
        prob[pt+'.HPturb.PR'] = 6.7
        prob[pt+'.LPturb.PR'] = 1.5
        prob[pt+'.LPcomp.PR'] = 2.
        prob[pt+'.HPcomp.PR'] = 2.6
        prob[pt+'.LPcomp.map.RlineMap'] = 2.0
        prob[pt+'.HPcomp.map.RlineMap'] = 2.0
    
        prob.set_val(pt+'.rec.rec.s_RPC', s_RPC, units='m')
        prob.set_val(pt+'.rec.rec.s_INS', s_INS, units='m')
        prob.set_val(pt+'.rec.rec.L', L, units='m')
    
    # prob.set_solver_print(level=-1)
    # prob.set_solver_print(level=2, depth=1)
        
    st = time.time()
    prob.run_model()
    print("time", time.time() - st)
    st = time.time()
    
    # w_ini = mp_complex.get_val('DESIGN.inlet.Fl_O:stat:W', units='kg/s')
    # T_fluid_in = mp_complex.get_val('DESIGN.rec.rec.T_fluid_in', units='K')
    
    # diff = 1
    # limit = 0.001
    
    # # sankey(prob,'DESIGN')
    
    # L_log=[]
    # s_INS_log=[]
    # s_RPC_log=[]
    # m_dot_log=[]
    # diff_log=[]
    
    # m_dot=float(w_ini)
    
    # L_log.append(L)
    # s_INS_log.append(s_INS)
    # s_RPC_log.append(s_RPC)
    # m_dot_log.append(m_dot)
    
    # prob.cleanup()
    
    # while diff>limit:
        
    #     p = om.Problem()
            
    #     p.model.add_subsystem('receiver', 
    #                           surrOpt(L=L, s_INS=s_INS, s_RPC=s_RPC)
    #                           ,promotes=['*'])
                                                              
    #     p.setup()
    #     # p.set_val('receiver.Q_Solar_In', Q_Solar, units='W')
    #     p.set_val('m_dot', m_dot,units='kg/s')
    #     p.set_val('Tfi',T_fluid_in, units='K')
        
    #     p.final_setup()
    #     p.run_model()
        
    #     L = float(p.get_val('receiver.L', units='m'))
    #     s_INS=float(p.get_val('receiver.ins', units='m'))
    #     s_RPC=float(p.get_val('receiver.rpc', units='m'))
        
    #     L_log.append(L)
    #     s_INS_log.append(s_INS)
    #     s_RPC_log.append(s_RPC)
        
    #     print("time", time.time() - st)
    #     st = time.time()
    #     p.cleanup()
        
    #     prob = om.Problem()
    #     mp_complex = prob.model = MPComplex2()
    #     prob.setup(check=False)
        
    #     prob.set_val('DESIGN.rec.rec.s_RPC', s_RPC, units='m')
    #     prob.set_val('DESIGN.rec.rec.s_INS', s_INS, units='m')
    #     prob.set_val('DESIGN.rec.rec.L', L, units='m')
        
    #     #Define the design point
    #     prob.set_val('DESIGN.fc.alt', alt, units='ft')
    #     prob.set_val('DESIGN.fc.MN', fc_MN)
        
    #     #Define the design point
    #     prob.set_val('DESIGN.fc.alt', alt, units='ft')
    #     prob.set_val('DESIGN.fc.MN', fc_MN)
        
    #     prob.set_val('DESIGN.balance.pwr_target', pwr_target, units='W')
    #     prob.set_val('DESIGN.balance.T4_target', T_4, units='degC') 
    #     prob.set_val('DESIGN.LPcomp.PR', 2.0)
    #     prob.set_val('DESIGN.HPcomp.PR', 2.6)
    #     prob.set_val('DESIGN.HPcomp.eff', comp_eff)
    #     prob.set_val('DESIGN.HPturb.eff', turb_eff)
    #     prob.set_val('DESIGN.LPcomp.eff', comp_eff)
    #     prob.set_val('DESIGN.LPturb.eff', turb_eff)
    #     prob.set_val('DESIGN.rec.Q_Solar_In', Q_Solar, units='W')
    
        
    #     # initial guesses
    #     prob['DESIGN.balance.W'] = 0.0015
    #     prob['DESIGN.balance.LPturb_PR'] = 1.6
    #     prob['DESIGN.balance.HPturb_PR'] = 10.
    #     prob['DESIGN.fc.balance.Pt'] = 14.696
    #     prob['DESIGN.fc.balance.Tt'] = 518.67
        
    #     for i,pt in enumerate(mp_complex.od_pts):

    #         # initial guesses
    #         prob[pt+'.fc.balance.Pt'] = 14.6955113159
    #         prob[pt+'.fc.balance.Tt'] = 518.670
    #         prob[pt+'.balance.LP_Nmech'] = 15000
    #         prob[pt+'.balance.HP_Nmech'] = 25000
            
    #         prob[pt+'.balance.W'] = 0.00154
                        
    #         prob[pt+'.HPturb.PR'] = 10.
    #         prob[pt+'.LPturb.PR'] = 1.5
    #         prob[pt+'.LPcomp.PR'] = 2.
    #         prob[pt+'.HPcomp.PR'] = 2.6
    #         prob[pt+'.LPcomp.map.RlineMap'] = 2.0
    #         prob[pt+'.HPcomp.map.RlineMap'] = 2.0
        
    #         prob.set_val(pt+'.rec.rec.s_RPC', s_RPC, units='m')
    #         prob.set_val(pt+'.rec.rec.s_INS', s_INS, units='m')
    #         prob.set_val(pt+'.rec.rec.L', L, units='m')
            

    #     prob.set_solver_print(level=-1)
    #     prob.set_solver_print(level=2, depth=1)
    #     prob.run_model()
        
    #     m_dot=float(mp_complex.get_val('DESIGN.inlet.Fl_O:stat:W', units='kg/s'))
    #     m_dot_log.append(m_dot)
        
    #     print("time", time.time() - st)
    #     st = time.time()
        
    #     # sankey(prob,'DESIGN')
    #     viewer(prob, 'DESIGN')
    #     viewer2(prob, 'DESIGN')
    #     w = m_dot
        
    #     diff=abs(1-w/w_ini)
    #     w_ini=w
        
    #     diff_log.append(diff)
    #     print(f"L = {float(prob.get_val('DESIGN.rec.rec.L', units='m'))} m")
    #     print(f"INS = {float(prob.get_val('DESIGN.rec.rec.s_INS', units='m'))} m ")
    #     print(f"RPC = {float(prob.get_val('DESIGN.rec.rec.s_RPC', units='m'))} m")
    #     print(f"mass_flow = {w} kg/s")
        
    #     if diff>limit:
    #         prob.cleanup()
        
    
    for pt in ['DESIGN']+mp_complex.od_pts:
        viewer(prob, pt)
        viewer2(prob, pt)
        map_plots(prob, pt)
        
    comp_map_all(prob)
    turb_map_all(prob)
    
    mail('')
    
    print()
    print("time", time.time() - st)
    
    print('shaft power [W]:  ')
    print(mp_complex.get_val('DESIGN.LPshaft.pwr_net', units='W'))
    print('receiver outlet temperature  [oC]:')
    print(mp_complex.get_val('DESIGN.rec.Fl_O:tot:T', units='degC'))
    print('mass flow rate [kg/s]:')
    print(mp_complex.get_val('DESIGN.inlet.Fl_O:stat:W', units='kg/s'))