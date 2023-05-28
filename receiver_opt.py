#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  1 14:46:47 2021

@author: tufan
"""
import openmdao.api as om
from math import pi
import numpy as np
import time

from draw_contour import draw_contour

from receiver import Receiver

"""
    optimization notes:
    
    tol  = 1e-5 and 1e-6 and 1e--7 same results
Optimization terminated successfully    (Exit mode 0)
            Current function value: [0.34396609]
            Iterations: 3
            Function evaluations: 27
            Gradient evaluations: 3
        Tf_out:[1297.26162676]
        eff:[65.60339077]%
    
    tol = 1e-4 not sensitive enough!..
Optimization terminated successfully    (Exit mode 0)
            Current function value: [0.34423327]
            Iterations: 1
            Function evaluations: 10
            Gradient evaluations: 1
        Tf_out:[1296.85262527]
        eff:[65.57667275]%

"""



if __name__ == '__main__':

    
    # Opt.n param.s got best soln.
    scaler = -(1)
    # optimizer='trust-constr'
    optimizer='SLSQP'
    tol = 1e-5
    print(f'\n{optimizer} optimizater with scaler: {scaler} ({tol} tolerance)')
    print('------------------------------------------------------\n')
    
    r_1 = 0.015
    s_SiC = 0.005
    s_RPC = 0.015
    s_INS  = 0.1
    L = 0.065
    vol = pi * (r_1+s_SiC+s_RPC+s_INS)**2 * L
    
    
    tic = time.time()
    
    p = om.Problem()
    
    disc_z=20
    disc_SiC=10
    disc_RPC=20
    disc_INS=10
    
    p.model.add_subsystem('receiver', Receiver(disc_z=disc_z,disc_SiC=disc_SiC,disc_RPC=disc_RPC,disc_INS=disc_INS))
    
    # this part for optimization
    debug_print = ['desvars','objs','nl_cons','totals']
    # p.driver = om.ScipyOptimizeDriver(debug_print = debug_print, optimizer='SLSQP', tol=1e-7)#,optimizer='differential_evolution')
    p.driver = om.ScipyOptimizeDriver(debug_print = debug_print, optimizer=optimizer, tol=tol)#,optimizer='differential_evolution')#scaler 900 ip.driver = om.ScipyOptimizeDriver(optimizer='shgo',debug_print = debug_print)#,optimizer='differential_evolution')#scaler 900 is optimum gain!..
    #p.driver = om.pyOptSparseDriver(debug_print = debug_print)
    # p.driver = om.DOEDriver(om.UniformGenerator(num_samples=10),debug_print = debug_print)
    
    # p.driver = om.SimpleGADriver(debug_print = debug_print)
    # p.driver.options['penalty_parameter'] = 5.
    # p.driver.options['penalty_exponent'] = 8.
    

    # this part for optimization
    # Mass_Flow = 0.00055
    s_SiC = 0.005
    s_RPC = 0.015
    s_INS = 0.1
    L = 0.065
    
    # p.model.set_input_defaults('receiver.Mass_Flow', Mass_Flow, units='kg/s')
    # p.model.set_input_defaults('receiver.s_SiC',s_SiC, units='m')
    p.model.set_input_defaults('receiver.s_RPC',s_RPC, units='m')
    p.model.set_input_defaults('receiver.s_INS', s_INS, units='m')
    p.model.set_input_defaults('receiver.L',L, units='m')
    
    # p.model.add_design_var('receiver.s_SiC',lower = 0.004, upper = 0.02, units='m',scaler= 50)
    p.model.add_design_var('receiver.s_RPC',lower = 0.005, upper = 0.025, units='m', scaler= 40)
    p.model.add_design_var('receiver.s_INS',lower = 0.05,upper = 0.15, units='m', scaler= 10)
    p.model.add_design_var('receiver.L',lower = 0.02,upper = 0.07, units='m', scaler= 15)
    # p.model.add_design_var('receiver.Mass_Flow', lower = 0.0004, upper = 0.0007, units='kg/s', scaler=1250)
    
    # p.model.add_constraint('receiver.T_outer', upper=373, units='K')
    p.model.add_constraint('receiver.T', upper=373, units='K',indices=((disc_z+2)*(3+disc_INS+disc_RPC+disc_SiC)+np.arange(disc_z+2,dtype=int)),flat_indices=True, scaler=0.003)
    p.model.add_constraint('receiver.T_fluid_out', lower=1273.15, upper=1373.15, units='K', scaler=0.001)
    p.model.add_constraint('receiver.Volume',lower=0.002, upper=0.003721609197258809, units='m**3' ,scaler=30)
    
    p.model.add_objective('receiver.eff_S2G',scaler=scaler, adder=-1)#, adder=-1,scaler=100)#scaling should be increased
    
    # Here we show how to attach recorders to each of the four objects:
    #   problem, driver, solver, and system
    
    # Create a recorder
    recorder = om.SqliteRecorder('cases.sql')
    
    # Attach recorder to the problem
    p.add_recorder(recorder)
    
    # Attach recorder to the driver
    p.driver.add_recorder(recorder)
    
    
    p.setup()    
    
    # Attach recorder to a subsystem
    p.model.receiver.add_recorder(recorder)
    
    # Attach recorder to a solver
    p.model.receiver.nonlinear_solver.add_recorder(recorder)

    
    p.set_solver_print(1)
    
    # this part for initialize
    # p.set_val('receiver.L', 0.065, units='m')

    p.set_val('receiver.r_1', r_1, units='m')
    p.set_val('receiver.s_SiC',s_SiC, units='m')
    # p.set_val('receiver.s_RPC',s_RPC, units='m')
    # p.set_val('receiver.s_INS',s_INS, units='m')
    
    p.set_val('receiver.E', 0.9)
    
    p.set_val('receiver.h_loss', 15., units='W/(m**2*K)')
    
    p.set_val('receiver.k_INS', 0.3, units='W/(m*K)')
    p.set_val('receiver.k_SiC', 33., units='W/(m*K)')
    p.set_val('receiver.k_Air', 0.08, units='W/(m*K)')
    
    # p.set_val('receiver.porosity', 0.81)
    
    # p.set_val('receiver.p', 10., units='bar')
    
    Mass_Flow = 0.00065
    p.set_val('receiver.Mass_Flow', Mass_Flow, units='kg/s')

    # p.set_val('receiver.D_nom', 0.00254, units='m')
    p.set_val('receiver.A_spec', 500.0, units='m**-1')
    p.set_val('receiver.K_ex', 200., units='m**-1')
    
    p.set_val('receiver.cp',1005.,units='J/(kg*K)')
    
    p.set_val('receiver.T_fluid_in',293, units='K')
    
    p.set_val('receiver.Tamb', 293., units='K')    
    
    # this part for radiocity
    p.set_val('receiver.Q_Solar_In', 1000., units='W')
    # p.set_val('receiver.sigma', 5.67*10**(-8), units='W/(m**2*K**4)')

    p.final_setup()
    # p.run_model()  #just for single iteration, solves not optimizes
    p.run_driver()
    p.record("final_state")
    print('Elapsed time is', time.time()-tic, 'seconds', sep=None)
    
    om.view_connections(p, outfile= "receiver.html", show_browser=False)
    om.n2(p, outfile="receiver_n2.html", show_browser=False)
    
    z_n = p.get_val('receiver.z_n')
    r_n = p.get_val('receiver.r_n')
    T = p.get_val('receiver.T').reshape(44,22)
    Mass_Flow = p.get_val('receiver.Mass_Flow')
    draw_contour(z_n[0,:], r_n[:,0], T-273, r_1+s_SiC, r_1+s_SiC+s_RPC, Mass_Flow, 10)
    
    Tf_out= p.get_val('receiver.T_fluid_out')
    print(f'Tf_out:{Tf_out}')
    m = p.get_val('receiver.Mass_Flow')
    print(f'mass flow:{m}')
    eff_S2G = p.get_val('receiver.eff_S2G')
    print(f'eff:{(eff_S2G)*100}%')
    s_SiC = p.get_val('receiver.s_SiC')
    print(f's_SiC: {s_SiC}  m')
    
    
    # data = p.check_partials(compact_print=True, show_only_incorrect=True, step_calc='rel_element', rel_err_tol=1e-5,abs_err_tol=1e-5)
    # data = data['receiver.radiocity']
    # # data_T = data['T_fluid','A_spec']['J_fd']
    # data_V = data['Q','F_BP_1']['J_fd']
    # # data_V = np.resize(data_V,(20,20))
    # data_V_calc = data['Q','F_BP_1']['J_fwd']
    # # data_V_calc = np.resize(data_V_calc,(20,20))
    
    # err = data_V-data_V_calc
    
    # max_=np.amax(err)
    # min_=np.amin(err)

    # totals = p.compute_totals('receiver.eff_S2G','receiver.m')
    # tolals2 = p.compute_totals('receiver.m','receiver.Mass_Flow')
    # totals = p.compute_totals('receiver.eff_S2G', 'receiver.Mass_Flow')
    
    # print(f'total derivative: {totals}')
    
    p.cleanup()
    
    # Q = p.get_val('receiver.radiocity.Q')
    # print(Q)
    # T = p.get_val('receiver.T')
    # print(T)