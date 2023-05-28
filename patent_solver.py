#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 31 14:34:26 2022

@author: tufanakba
patent solver
"""

import openmdao.api as om
from viewer_patent import viewer_generation, viewer_motoring
from patent import MPgeneration, MPmotoring
from MDAOMetaModel_Opt import surrOpt
from map_plotter3 import comp_map, turb_map

from mail import mail
import time

if __name__ == "__main__":
    # Design cond.s
    
    optn=False #Thickness optimization
    
    
    Q_Solar = 1000.
    T_4 = 1000.
    pwr_target = 170.
    alt = 0.000001
    fc_MN = 1e-6

    comp_eff = 0.83
    turb_eff = 0.86
    
    # Design Param.s start
    
    # s_RPC = 0.01
    # s_INS = 0.1
    # L = 0.035
    
    
    # optimized results (old)
    # L = 0.07285836023878457
    # s_INS = 0.09788381936713199
    # s_RPC = 0.009487799245649634
    
    # optimized results (new)
    L = 0.07284367071677698
    s_INS = 0.0975481552652269
    s_RPC = 0.009827702728493431
    # mass_flow = 0.000836789005063164 kg/s
    
    prob = om.Problem()
    # TODO: set od - change to true when generation below is simulated!..
    gen_no_od = True
    patent_cycle = prob.model = MPgeneration(No_od=gen_no_od)
    
    prob.setup(check=False)
    
    prob.set_val('DESIGN'+'.rec.rec.s_RPC', s_RPC, units='m')
    prob.set_val('DESIGN'+'.rec.rec.s_INS', s_INS, units='m')
    prob.set_val('DESIGN'+'.rec.rec.L', L, units='m')
    #Define the design point
    prob.set_val('DESIGN.fc.alt', alt, units='ft')
    prob.set_val('DESIGN.fc.MN', fc_MN)
    
    prob.set_val('DESIGN.balance.pwr_target', pwr_target, units='W')
    prob.set_val('DESIGN.balance.T4_target', T_4, units='degC') 
    prob.set_val('DESIGN.comp.PR', 5.2)
    prob.set_val('DESIGN.comp.eff', comp_eff)
    prob.set_val('DESIGN.turb.eff', turb_eff)
    prob.set_val('DESIGN.gen.eff', turb_eff)
    prob.set_val('DESIGN.rec.Q_Solar_In', Q_Solar, units='W')
    
    # initial guesses
    prob['DESIGN.balance.W'] = 0.0018 #0.00122811 #147/100000
    prob['DESIGN.balance.turb_PR'] = 2.
    prob['DESIGN.balance.gen_PR'] = 2.3
    # prob['DESIGN.balance.comp_PR'] = 4.489
    prob['DESIGN.fc.balance.Pt'] = 14.696
    prob['DESIGN.fc.balance.Tt'] = 518.670 #518.665288153
    
    if not gen_no_od:
        for i,pt in enumerate(patent_cycle.od_pts):
            
            # initial guesses
            prob[pt+'.balance.W'] = 0.0018
            prob[pt+'.balance.Gen_Nmech'] = 15000
            prob[pt+'.balance.Nmech'] = 25000
            prob[pt+'.fc.balance.Pt'] = 14.696
            prob[pt+'.fc.balance.Tt'] = 518.670                         
            prob[pt+'.turb.PR'] = 2.
            prob[pt+'.gen.PR'] = 2.3
            prob[pt+'.comp.PR'] = 5.2
            prob[pt+'.comp.map.RlineMap'] = 2.0
        
            prob.set_val(pt+'.rec.rec.s_RPC', s_RPC, units='m')
            prob.set_val(pt+'.rec.rec.s_INS', s_INS, units='m')
            prob.set_val(pt+'.rec.rec.L', L, units='m')
        
    prob.set_solver_print(level=-1)
    prob.set_solver_print(level=2, depth=1)
    
    st = time.time()
    prob.run_model()
    print("time", time.time() - st)
    st = time.time()
    
    w_ini = patent_cycle.get_val('DESIGN.inlet.Fl_O:stat:W', units='kg/s')
    T_fluid_in = patent_cycle.get_val('DESIGN.rec.rec.T_fluid_in', units='K')
    
    
    diff = 1
    limit = 0.001
    
    # sankey(prob,'DESIGN')
    # viewer_generation(prob, 'DESIGN')
    
    L_log=[]
    s_INS_log=[]
    s_RPC_log=[]
    m_dot_log=[]
    diff_log=[]
    
    m_dot=float(w_ini)
    
    L_log.append(L)
    s_INS_log.append(s_INS)
    s_RPC_log.append(s_RPC)
    m_dot_log.append(m_dot)
    
    prob.cleanup()
    
    
    if optn:
        while diff>limit:
            
            p = om.Problem()
                
            p.model.add_subsystem('receiver', 
                                  surrOpt(L=L, s_INS=s_INS, s_RPC=s_RPC)
                                  ,promotes=['*'])
                                                                  
            p.setup()
            # p.set_val('receiver.Q_Solar_In', Q_Solar, units='W')
            p.set_val('m_dot', m_dot,units='kg/s')
            p.set_val('Tfi',T_fluid_in, units='K')
            
            p.final_setup()
            p.run_model()
            
            L = float(p.get_val('receiver.L', units='m'))
            s_INS=float(p.get_val('receiver.ins', units='m'))
            s_RPC=float(p.get_val('receiver.rpc', units='m'))
            
            L_log.append(L)
            s_INS_log.append(s_INS)
            s_RPC_log.append(s_RPC)
            
            print("time", time.time() - st)
            st = time.time()
            p.cleanup()
            
            prob = om.Problem()
            patent_cycle = prob.model = MPgeneration(No_od=True)
            prob.setup(check=False)
            
            prob.set_val('DESIGN'+'.rec.rec.s_RPC', s_RPC, units='m')
            prob.set_val('DESIGN'+'.rec.rec.s_INS', s_INS, units='m')
            prob.set_val('DESIGN'+'.rec.rec.L', L, units='m')
            #Define the design point
            prob.set_val('DESIGN.fc.alt', alt, units='ft')
            prob.set_val('DESIGN.fc.MN', fc_MN)
            
            prob.set_val('DESIGN.balance.pwr_target', pwr_target, units='W')
            prob.set_val('DESIGN.balance.T4_target', T_4, units='degC') 
            prob.set_val('DESIGN.comp.PR', 5.2)
            prob.set_val('DESIGN.comp.eff', comp_eff)
            prob.set_val('DESIGN.turb.eff', turb_eff)
            prob.set_val('DESIGN.gen.eff', turb_eff)
            prob.set_val('DESIGN.rec.Q_Solar_In', Q_Solar, units='W')
            
            # initial guesses
            prob['DESIGN.balance.W'] = 0.0018 #0.00122811 #147/100000
            prob['DESIGN.balance.turb_PR'] = 2.
            prob['DESIGN.balance.gen_PR'] = 2.3
            # prob['DESIGN.balance.comp_PR'] = 4.489
            prob['DESIGN.fc.balance.Pt'] = 14.696
            prob['DESIGN.fc.balance.Tt'] = 518.670 #518.665288153
            
            # for i,pt in enumerate(patent_cycle.od_pts):
    
            #     # initial guesses
            #     prob[pt+'.balance.W'] = 0.00178
            #     prob[pt+'.balance.Gen_Nmech'] = 15000
            #     prob[pt+'.balance.Nmech'] = 25000
            #     prob[pt+'.fc.balance.Pt'] = 14.6955113159
            #     prob[pt+'.fc.balance.Tt'] = 518.670                         
            #     prob[pt+'.turb.PR'] = 1.8
            #     prob[pt+'.gen.PR'] = 2.3
            #     prob[pt+'.comp.PR'] = 4.
            #     prob[pt+'.comp.map.RlineMap'] = 2.0
            
            #     prob.set_val(pt+'.rec.rec.s_RPC', s_RPC, units='m')
            #     prob.set_val(pt+'.rec.rec.s_INS', s_INS, units='m')
            #     prob.set_val(pt+'.rec.rec.L', L, units='m')
                
    
            prob.set_solver_print(level=-1)
            prob.set_solver_print(level=2, depth=1)
            prob.run_model()
            
            m_dot=float(patent_cycle.get_val('DESIGN.inlet.Fl_O:stat:W', units='kg/s'))
            m_dot_log.append(m_dot)
            
            print("time", time.time() - st)
            st = time.time()
            
            # sankey(prob,'DESIGN')
            # viewer_generation(prob, 'DESIGN')
            w = m_dot
            
            diff=abs(1-w/w_ini)
            w_ini=w
            
            diff_log.append(diff)
            print(f"L = {float(prob.get_val('DESIGN.rec.rec.L', units='m'))} m")
            print(f"INS = {float(prob.get_val('DESIGN.rec.rec.s_INS', units='m'))} m ")
            print(f"RPC = {float(prob.get_val('DESIGN.rec.rec.s_RPC', units='m'))} m")
            print(f"mass_flow = {w} kg/s")
            
            if diff>limit:
                prob.cleanup()
    
    
    # Generation after optimization
    prob = om.Problem()
    # TODO: set od 
    gen_no_od = False
    patent_cycle = prob.model = MPgeneration(No_od=gen_no_od)
    
    prob.setup(check=False)
    
    prob.set_val('DESIGN'+'.rec.rec.s_RPC', s_RPC, units='m')
    prob.set_val('DESIGN'+'.rec.rec.s_INS', s_INS, units='m')
    prob.set_val('DESIGN'+'.rec.rec.L', L, units='m')
    #Define the design point
    prob.set_val('DESIGN.fc.alt', alt, units='ft')
    prob.set_val('DESIGN.fc.MN', fc_MN)
    
    prob.set_val('DESIGN.balance.pwr_target', pwr_target, units='W')
    prob.set_val('DESIGN.balance.T4_target', T_4, units='degC') 
    prob.set_val('DESIGN.comp.PR', 5.2)
    prob.set_val('DESIGN.comp.eff', comp_eff)
    prob.set_val('DESIGN.turb.eff', turb_eff)
    prob.set_val('DESIGN.gen.eff', turb_eff)
    prob.set_val('DESIGN.rec.Q_Solar_In', Q_Solar, units='W')
    
    # initial guesses
    prob['DESIGN.balance.W'] = 0.0018 #0.00122811 #147/100000
    prob['DESIGN.balance.turb_PR'] = 1.8
    prob['DESIGN.balance.gen_PR'] = 2.3
    # prob['DESIGN.balance.comp_PR'] = 4.489
    prob['DESIGN.fc.balance.Pt'] = 14.696
    prob['DESIGN.fc.balance.Tt'] = 518.670 #518.665288153
    
    if not gen_no_od:
        for i,pt in enumerate(patent_cycle.od_pts):
            
            # initial guesses
            prob[pt+'.balance.W'] = 0.0018
            prob[pt+'.balance.Gen_Nmech'] = 15000
            prob[pt+'.balance.Nmech'] = 25000
            prob[pt+'.fc.balance.Pt'] = 14.696
            prob[pt+'.fc.balance.Tt'] = 518.670                         
            prob[pt+'.turb.PR'] = 2.
            prob[pt+'.gen.PR'] = 2.3
            prob[pt+'.comp.PR'] = 5.2
            prob[pt+'.comp.map.RlineMap'] = 2.0
        
            prob.set_val(pt+'.rec.rec.s_RPC', s_RPC, units='m')
            prob.set_val(pt+'.rec.rec.s_INS', s_INS, units='m')
            prob.set_val(pt+'.rec.rec.L', L, units='m')
        
    prob.set_solver_print(level=-1)
    prob.set_solver_print(level=2, depth=1)
    
    st = time.time()
    prob.run_model()
    print("time", time.time() - st)
    st = time.time()
        
    # motoring class
    
    comp_s_PR = float(prob.get_val('DESIGN.comp.s_PR'))
    comp_s_Wc = float(prob.get_val('DESIGN.comp.s_Wc'))
    comp_s_eff = float(prob.get_val('DESIGN.comp.s_eff'))
    comp_s_Nc = float(prob.get_val('DESIGN.comp.s_Nc'))
    comp_area = float(prob.get_val('DESIGN.comp.Fl_O:stat:area'))
    
    turb_s_PR = float(prob.get_val('DESIGN.turb.s_PR'))
    turb_s_Wp = float(prob.get_val('DESIGN.turb.s_Wp'))
    turb_s_eff = float(prob.get_val('DESIGN.turb.s_eff'))
    turb_s_Np = float(prob.get_val('DESIGN.turb.s_Np'))
    turb_area = float(prob.get_val('DESIGN.turb.Fl_O:stat:area'))
    
    L = float(prob.get_val('DESIGN.rec.rec.L', units='m'))
    s_INS=float(prob.get_val('DESIGN.rec.rec.s_INS', units='m'))
    s_RPC=float(prob.get_val('DESIGN.rec.rec.s_RPC', units='m'))
    rec_area = float(prob.get_val('DESIGN.rec.Fl_O:stat:area'))
    
    prob_m = om.Problem()
    # TODO: set od.s
    motoring_no_od = True
    motoring_cycle = prob_m.model = MPmotoring(No_od=motoring_no_od)

    prob_m.setup(check=False)
    
    prob_m.set_val('DESIGN.fc.alt', alt, units='ft')
    prob_m.set_val('DESIGN.fc.MN', fc_MN)
    
    motor_power = -50
    Q_solar_motor = 1000
    
    # assign generating cycle parameters
    prob_m.set_val('DESIGN.balance.pwr_target', motor_power, units='W')
    prob_m.set_val('DESIGN.balance.T4_target', T_4, units='degC') 
    # prob_m.set_val('DESIGN.comp.PR', 2.)
    prob_m.set_val('DESIGN.comp.eff', comp_eff)
    prob_m.set_val('DESIGN.motor.eff', comp_eff)
    prob_m.set_val('DESIGN.turb.eff', turb_eff)

    prob_m.set_val('DESIGN.rec.Q_Solar_In', Q_solar_motor, units='W')
    
    
    # od data 
    prob_m.set_val('DESIGN.comp.s_PR', comp_s_PR)
    prob_m.set_val('DESIGN.comp.s_Wc', comp_s_Wc)
    prob_m.set_val('DESIGN.comp.s_eff', comp_s_eff)
    prob_m.set_val('DESIGN.comp.s_Nc', comp_s_Nc)
    prob_m.set_val('DESIGN.comp.area', comp_area, units='inch**2')
    
    prob_m.set_val('DESIGN.turb.s_PR', turb_s_PR)
    prob_m.set_val('DESIGN.turb.s_Wp', turb_s_Wp)
    prob_m.set_val('DESIGN.turb.s_eff', turb_s_eff)
    prob_m.set_val('DESIGN.turb.s_Np', turb_s_Np)
    prob_m.set_val('DESIGN.turb.area', turb_area, units='inch**2')
    
    prob_m.set_val('DESIGN.rec.rec.s_RPC', s_RPC)
    prob_m.set_val('DESIGN.rec.rec.s_INS', s_INS)
    prob_m.set_val('DESIGN.rec.rec.L', L)
    prob_m.set_val('DESIGN.rec.area', rec_area, units='inch**2')
    
    
    # initial guesses
    prob_m['DESIGN.balance.W'] = 0.00118 #0.00122811 #147/100000
    prob_m['DESIGN.balance.Nmech'] = 15000
    # prob_m['DESIGN.balance.motor_PR'] = 2.0
    prob_m['DESIGN.fc.balance.Pt'] = 14.696
    prob_m['DESIGN.fc.balance.Tt'] = 518.670 #518.665288153
    
    # od for motoring
    if not motoring_no_od:
        for i,pt in enumerate(motoring_cycle.od_pts):
            
            # initial guesses
            prob_m[pt+'.balance.W'] = 0.0018
            prob_m[pt+'.balance.Gen_Nmech'] = 15000
            prob_m[pt+'.balance.Nmech'] = 25000
            prob_m[pt+'.fc.balance.Pt'] = 14.696
            prob_m[pt+'.fc.balance.Tt'] = 518.670                         
            prob_m[pt+'.turb.PR'] = 1.7
            prob_m[pt+'.motor.PR'] = 1.7
            prob_m[pt+'.comp.PR'] = 3.
            prob_m[pt+'.comp.map.RlineMap'] = 2.
        
            prob_m.set_val(pt+'.rec.rec.s_RPC', s_RPC, units='m')
            prob_m.set_val(pt+'.rec.rec.s_INS', s_INS, units='m')
            prob_m.set_val(pt+'.rec.rec.L', L, units='m')
            
            prob_m.set_val(pt+'.turb.s_PR', turb_s_PR)
            prob_m.set_val(pt+'.turb.s_Wp', turb_s_Wp)
            prob_m.set_val(pt+'.turb.s_eff', turb_s_eff)
            prob_m.set_val(pt+'.turb.s_Np', turb_s_Np)
            # prob_m.set_val('DESIGN.turb.Fl_O:stat:area', turb_area)
            prob_m.set_val(pt+'.turb.area', turb_area,units='inch**2')
            
            prob_m.set_val(pt+'.comp.s_PR', comp_s_PR)
            prob_m.set_val(pt+'.comp.s_Wc', comp_s_Wc)
            prob_m.set_val(pt+'.comp.s_eff', comp_s_eff)
            prob_m.set_val(pt+'.comp.s_Nc', comp_s_Nc)
            # prob_m.set_val('DESIGN.comp.Fl_O:stat:area', comp_area)
            prob_m.set_val(pt+'.comp.area', comp_area,units='inch**2')
            
            prob_m.set_val(pt+'.rec.area', rec_area, units='inch**2')
    
    prob_m.set_solver_print(level=-1)
    prob_m.set_solver_print(level=2, depth=1)
    
    st = time.time()
    prob_m.run_model()
    print("time", time.time() - st)  
        
    viewer_generation(prob, 'DESIGN')
    viewer_motoring(prob_m, 'DESIGN')
    
    if not gen_no_od:
        for pt in patent_cycle.od_pts:
            viewer_generation(prob, pt)
        comp_map(prob,gen=True)
        turb_map(prob,gen=True)

    if not motoring_no_od:
        for pt in motoring_cycle.od_pts:
            viewer_motoring(prob_m, pt)
        comp_map(prob_m,gen=False)
        turb_map(prob_m,gen=False)
        
        
    print()
    print("time", time.time() - st)
    
    mail('')
    
    print('shaft power [W]:  ')
    print(patent_cycle.get_val('DESIGN.LPshaft.pwr_net', units='W'))
    print('receiver outlet temperature  [oC]:')
    print(patent_cycle.get_val('DESIGN.rec.Fl_O:tot:T', units='degC'))
    print('mass flow rate [kg/s]:')
    print(patent_cycle.get_val('DESIGN.inlet.Fl_O:stat:W', units='kg/s'))