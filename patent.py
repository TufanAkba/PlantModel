#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 8 ağustos pazartesi

@author: tufanakba
patent cycle 
#1 receiver designer - generation mode  C-R-HPT-LPT
#2 supercharger designer - motoring mode LPC-HPC-R-T

"""

import openmdao.api as om
import pycycle.api as pyc
from py_Receiver import py_Receiver
from components.comp_map import AXI5
from components.MG3 import MG
# from viewer2 import viewer, viewer2, map_plots, sankey
from receiver import ReceiverSubProblem

class generation(pyc.Cycle):
    
    def initialize(self):
        
        self.options.declare('setting_mode', default='T4', values=['T4', 'comp'])
        
        super().initialize()
        
    def setup(self):
        
        # TODO: set maps here and assign the comp.s
        comp_map = AXI5
        turb_map = pyc.LPT2269
        gen_map = pyc.LPT2269
        
        design = self.options['design']

        self.add_subsystem('fc', pyc.FlightConditions())
        self.add_subsystem('inlet', pyc.Inlet())
        self.add_subsystem('comp', pyc.Compressor(map_data=comp_map, map_extrap=True), promotes_inputs =['Nmech'])
        self.add_subsystem('rec', py_Receiver())
        self.add_subsystem('turb', pyc.Turbine(map_data=turb_map, map_extrap=True), promotes_inputs =['Nmech'])
        self.add_subsystem('gen', pyc.Turbine(map_data=gen_map, map_extrap=True), promotes_inputs =[('Nmech','Gen_Nmech')])
        self.add_subsystem('nozz', pyc.Nozzle(nozzType='CD', lossCoef='Cv'))
        self.add_subsystem('MG', MG(), promotes_inputs=[('n','Gen_Nmech')])
        self.add_subsystem('HPshaft', pyc.Shaft(num_ports=2), promotes_inputs =[('Nmech','Nmech')])
        self.add_subsystem('LPshaft', pyc.Shaft(num_ports=1), promotes_inputs =[('Nmech','Gen_Nmech')])
        
        self.pyc_connect_flow('fc.Fl_O', 'inlet.Fl_I', connect_w=False)
        self.pyc_connect_flow('inlet.Fl_O', 'comp.Fl_I')
        self.pyc_connect_flow('comp.Fl_O', 'rec.Fl_I')
        self.pyc_connect_flow('rec.Fl_O', 'turb.Fl_I')
        self.pyc_connect_flow('turb.Fl_O', 'gen.Fl_I')
        self.pyc_connect_flow('gen.Fl_O', 'nozz.Fl_I')
        
        self.connect('comp.trq', 'HPshaft.trq_0')
        self.connect('turb.trq', 'HPshaft.trq_1')
        
        self.connect('gen.trq', 'LPshaft.trq_0')
        self.connect('LPshaft.trq_net', 'MG.trq')
        
        self.connect('fc.Fl_O:stat:P', 'nozz.Ps_exhaust')
        
        balance = self.add_subsystem('balance', om.BalanceComp())
        if design:
            
            balance.add_balance('W', lower=0.0005, upper=0.005, units='lbm/s', eq_units='degC', rhs_name='T4_target')
            self.connect('balance.W', 'inlet.Fl_I:stat:W')
            self.connect('rec.Fl_O:tot:T', 'balance.lhs:W')
            
            balance.add_balance('turb_PR', val=2.0, lower=1.5, upper=3., eq_units='W', rhs_val=0.)
            self.connect('balance.turb_PR', 'turb.PR')
            self.connect('HPshaft.pwr_net', 'balance.lhs:turb_PR')
            
            balance.add_balance('gen_PR', val=2.0, lower=1.5, upper=3., eq_units='W', rhs_name='pwr_target')
            self.connect('balance.gen_PR', 'gen.PR')
            self.connect('LPshaft.pwr_net', 'balance.lhs:gen_PR')
            
        else:
            
            balance.add_balance('Nmech', lower=15000., upper=30000., units='rpm', eq_units='hp', rhs_val=0.)
            self.connect('balance.Nmech', 'Nmech')
            self.connect('HPshaft.pwr_net', 'balance.lhs:Nmech')
            
            balance.add_balance('Gen_Nmech', units='rpm', lower=10000., upper=25000., eq_units='W', rhs_name='pwr_target')
            self.connect('balance.Gen_Nmech', 'Gen_Nmech')
            self.connect('MG.P_el', 'balance.lhs:Gen_Nmech')
            
            if self.options['setting_mode'] == 'T4':
                
                balance.add_balance('W', lower=0.0005, upper=0.005, units='lbm/s', eq_units='degC', rhs_val=1000,
                                    rhs_name='T4_target')
                
                self.connect('balance.W', 'inlet.Fl_I:stat:W')
                self.connect('rec.Fl_O:tot:T', 'balance.lhs:W')
                
            if self.options['setting_mode'] == 'comp':
                
                balance.add_balance('W', lower=0.0005, upper=0.005, units='lbm/s', eq_units=None, rhs_val=2.0)
                self.connect('balance.W', 'inlet.Fl_I:stat:W')
                self.connect('comp.map.RlineMap', 'balance.lhs:W')
            
        self.set_order(['fc', 'inlet', 'comp', 'rec', 'turb','gen', 'nozz','HPshaft','LPshaft', 'MG', 'balance'])
            
        newton = self.nonlinear_solver = om.NewtonSolver()
        newton.options['atol'] = 1e-6
        newton.options['rtol'] = 1e-6
        newton.options['iprint'] = 2
        newton.options['maxiter'] = 30
        newton.options['solve_subsystems'] = True
        newton.options['max_sub_solves'] = 100
        newton.options['reraise_child_analysiserror'] = False
        # Stall definition
        newton.options['stall_limit'] = 3# update to 4
        newton.options['stall_tol'] = 1e-4# update to -5
        # Line Search
        newton.linesearch = om.ArmijoGoldsteinLS()
        newton.linesearch.options['iprint'] = 1
        newton.linesearch.options['maxiter'] = 4
        newton.linesearch.options['rho'] = 0.85  # work on impact of rho 0.85 for sample brayton
        # TODO: Make this false later
        newton.linesearch.options['print_bound_enforce'] = False
        
        self.linear_solver = om.DirectSolver()

        super().setup()
        
class motoring(pyc.Cycle):
    
    def initialize(self):
        
        self.options.declare('setting_mode', default='T4', values=['T4', 'comp'])
        
        self.options.declare('comp_s_PR', types=float, desc='HPC scaled PR')
        
        super().initialize()
        
    def setup(self):
        
        # TODO: set maps here and assign the comp.s
        comp_map = AXI5
        motor_map = AXI5
        turb_map = pyc.LPT2269
        
        design = self.options['design']

        self.add_subsystem('fc', pyc.FlightConditions())
        self.add_subsystem('inlet', pyc.Inlet())
        self.add_subsystem('motor', pyc.Compressor(map_data=motor_map, map_extrap=True), promotes_inputs =[('Nmech','Gen_Nmech')])
        self.add_subsystem('comp', pyc.Compressor(map_data=comp_map, map_extrap=True, od_only=True), promotes_inputs =['Nmech'])
        self.add_subsystem('rec', py_Receiver(od_only=True))
        self.add_subsystem('turb', pyc.Turbine(map_data=turb_map, map_extrap=True, od_only=True), promotes_inputs =['Nmech'])
        self.add_subsystem('nozz', pyc.Nozzle(nozzType='CD', lossCoef='Cv'))
        self.add_subsystem('MG', MG(), promotes_inputs=[('n','Gen_Nmech')])
        self.add_subsystem('HPshaft', pyc.Shaft(num_ports=2), promotes_inputs =[('Nmech','Nmech')])
        self.add_subsystem('LPshaft', pyc.Shaft(num_ports=1), promotes_inputs =[('Nmech','Gen_Nmech')])
        
        self.pyc_connect_flow('fc.Fl_O', 'inlet.Fl_I', connect_w=False)
        self.pyc_connect_flow('inlet.Fl_O', 'motor.Fl_I')
        self.pyc_connect_flow('motor.Fl_O', 'comp.Fl_I')
        self.pyc_connect_flow('comp.Fl_O', 'rec.Fl_I')
        self.pyc_connect_flow('rec.Fl_O', 'turb.Fl_I')
        self.pyc_connect_flow('turb.Fl_O', 'nozz.Fl_I')
        
        self.connect('comp.trq', 'HPshaft.trq_0')
        self.connect('turb.trq', 'HPshaft.trq_1')
        
        self.connect('motor.trq', 'LPshaft.trq_0')
        self.connect('LPshaft.trq_net', 'MG.trq')
        
        self.connect('fc.Fl_O:stat:P', 'nozz.Ps_exhaust')
        
        balance = self.add_subsystem('balance', om.BalanceComp())
        if design:
            
            balance.add_balance('W', lower=0.0005, upper=0.005, units='lbm/s', eq_units='degC', rhs_name='T4_target')
            self.connect('balance.W', 'inlet.Fl_I:stat:W')
            self.connect('rec.Fl_O:tot:T', 'balance.lhs:W')
            
            # balance.add_balance('turb_PR', val=2.0, lower=1.1, upper=2.9, eq_units='W', rhs_val=0.)
            # self.connect('balance.turb_PR', 'turb.PR')
            # self.connect('HPshaft.pwr_net', 'balance.lhs:turb_PR')
            
            balance.add_balance('Nmech', lower=15000., upper=25000., units='rpm', eq_units='hp', rhs_val=0.)
            self.connect('balance.Nmech', 'Nmech')
            self.connect('HPshaft.pwr_net', 'balance.lhs:Nmech')
            
            balance.add_balance('motor_PR', val=2.0, lower=1.1, upper=3., eq_units='W', rhs_name='pwr_target')
            self.connect('balance.motor_PR', 'motor.PR')
            self.connect('LPshaft.pwr_net', 'balance.lhs:motor_PR')
            
            # balance.add_balance('comp_PR', val=1.5, lower=1.3, upper=2.1 ,rhs_val=1.)
            # self.connect('balance.comp_PR', 'nozz.PR')
            # self.connect('comp.PR', 'balance.lhs:comp_PR')
            
            
            
        else:
            
            balance.add_balance('Nmech', lower=15000., upper=30000., units='rpm', eq_units='hp', rhs_val=0.)
            self.connect('balance.Nmech', 'Nmech')
            self.connect('HPshaft.pwr_net', 'balance.lhs:Nmech')
            
            balance.add_balance('Gen_Nmech', units='rpm', lower=10000., upper=25000., eq_units='W', rhs_name='pwr_target')
            self.connect('balance.Gen_Nmech', 'Gen_Nmech')
            self.connect('MG.P_el', 'balance.lhs:Gen_Nmech')
            
            balance.add_balance('Q_solar', val=900., upper=1000., lower=400., units='W', rhs_val=2.0) # lower is 400 for -10 an -15!
            self.connect('balance.Q_solar', 'rec.Q_Solar_In')
            self.connect('motor.map.RlineMap', 'balance.lhs:Q_solar')
            
            if self.options['setting_mode'] == 'T4':
                
                balance.add_balance('W', lower=0.0005, upper=0.005, units='lbm/s', eq_units='degC', rhs_val=1000,
                                    rhs_name='T4_target')
                
                self.connect('balance.W', 'inlet.Fl_I:stat:W')
                self.connect('rec.Fl_O:tot:T', 'balance.lhs:W')
                
            if self.options['setting_mode'] == 'comp':
                
                balance.add_balance('W', lower=0.0005, upper=0.005, units='lbm/s', eq_units=None, rhs_val=2.0)
                self.connect('balance.W', 'inlet.Fl_I:stat:W')
                self.connect('comp.map.RlineMap', 'balance.lhs:W')
            
        self.set_order(['fc', 'inlet','motor', 'comp', 'rec', 'turb', 'nozz','LPshaft', 'HPshaft','MG', 'balance'])
            
        newton = self.nonlinear_solver = om.NewtonSolver()
        newton.options['atol'] = 1e-6
        newton.options['rtol'] = 1e-6
        newton.options['iprint'] = 2
        newton.options['maxiter'] = 30
        newton.options['solve_subsystems'] = True
        newton.options['max_sub_solves'] = 100
        newton.options['reraise_child_analysiserror'] = False
        # Stall definition
        newton.options['stall_limit'] = 3# update to 4
        newton.options['stall_tol'] = 1e-4# update to -5
        # Line Search
        newton.linesearch = om.ArmijoGoldsteinLS()
        newton.linesearch.options['iprint'] = 1
        newton.linesearch.options['maxiter'] = 4
        newton.linesearch.options['rho'] = 0.85  # work on impact of rho 0.85 for sample brayton
        # TODO: Make this false later
        newton.linesearch.options['print_bound_enforce'] = False
        
        self.linear_solver = om.DirectSolver()

        super().setup()

class MPgeneration(pyc.MPCycle):
    
    def initialize(self):
        
        self.options.declare('SS_Solar',types=float,default=500., desc='SelfSupplied Solar Resource', upper=1000, lower=200)
        self.options.declare('Min_Solar',types=float,default=840., desc='SelfSupplied Solar Resource', upper=1000, lower=500)
        self.options.declare('Max_Solar',types=float,default=1020., desc='SelfSupplied Solar Resource', upper=1300, lower=1000)#1050 cyclic sol.n
        
        self.options.declare('No_od', default=False, desc='Solves only design mode')
        
        super().initialize()
    
    def setup(self):
        
        self.pyc_add_pnt('DESIGN', pnt=generation(design=True))
        
        # for inlet area calculation MN must be set
        self.set_input_defaults('DESIGN.inlet.MN', 0.0250)
        self.set_input_defaults('DESIGN.comp.MN', 0.030)
        self.set_input_defaults('DESIGN.rec.MN', 0.04)
        self.set_input_defaults('DESIGN.turb.MN', 0.03)
        self.set_input_defaults('DESIGN.gen.MN', 0.02)
        # design point:
        self.set_input_defaults('DESIGN.Nmech', 25000.0, units='rpm')
        self.set_input_defaults('DESIGN.Gen_Nmech', 15000.0, units='rpm')
        
        self.pyc_add_cycle_param('nozz.Cv', 0.99)
        
        # nozzle trial
        # self.set_input_defaults('DESIGN.nozz.PR',1.)
        
        # OD part starts here!
        if not self.options['No_od']:
            self.od_MNs = 1e-6
            self.od_alts = 1e-6
            
            # ss_Solar = self.options['SS_Solar']
            # min_Solar = self.options['Min_Solar']
            # max_Solar = self.options['Max_Solar']
            
            # self.od_pts = ['Max_180','Max_180_2','Max_180_3','Max_180_4','Max_180_5']
            # self.od_pwrs = [180.,180.,180.,180.,180.]
            # self.Q_Solar = [1020.,1030.,1005.,1005.,1015.]
            # setting_mode = ['comp','comp','comp','T4','comp']
                    
            # self.od_pts = ['Min_100','Min_110','Min_120','Min_130','Min_140', 'Min_150', 'Min_160']
            # self.od_pwrs = [ 100.,110.,120.,130.,140., 150., 160.]
            # self.Q_Solar = [840.,850.,860.,870.,880.,890.,900.]
            # setting_mode = ['comp','comp','comp','comp','comp','comp','comp']
            
            # self.od_pts = ['Max_180_1']#,'Max_180_2']
            # self.od_pwrs = [ 180.,180.,180.]
            # self.Q_Solar = [1010.,1020.,1030.]
            # setting_mode = ['T4','T4','T4']
            
            # self.od_pts = ['Min90_1','Min_90_2']
            # self.od_pwrs = [ 90.,90.,90.]
            # self.Q_Solar = [750.,740.,730.]
            # setting_mode = ['comp','comp','comp']
            
            self.od_pts = ['Od_170','Max_160','Min_150','Min_140','Min_130','Min_120','Min_110','Min_100']
            self.od_pwrs = [170.,160.,150.,140.,130.,120.,110.,100.]
            self.Q_Solar = [970.,930.,880.,840.,800.,760.,750.,750.]
            setting_mode = ['T4','comp','comp','comp','comp','comp','comp','comp']
            
            # self.od_pts = ['Max_190','Max_180','Min_160','Min_150','Min_140','Min_130','Min_120','Min_110','Min_100']
            # self.od_pwrs = [ 190.,180.,160.,150.,140.,130.,120.,110.,100.]
            # self.Q_Solar = [1020.,1010.,980.,960.,920.,880.,860.,850.,840.]
            # setting_mode = ['T4','T4','comp','comp','comp','comp','comp','comp','comp']
            
            
            for i, pt in enumerate(self.od_pts):
                
                self.pyc_add_pnt(pt, pnt=generation(design=False, setting_mode=setting_mode[i]))
                self.set_input_defaults(pt + '.fc.MN', val=self.od_MNs)
                self.set_input_defaults(pt + '.fc.alt', self.od_alts, units='ft')
                self.set_input_defaults(pt + '.balance.pwr_target', self.od_pwrs[i], units='W')
                self.set_input_defaults(pt + '.rec.Q_Solar_In', self.Q_Solar[i], units='W')
                
                
            
            self.pyc_use_default_des_od_conns()
        
        # transfering design conditions to od.s
        # self.pyc_connect_des_od('comp.s_PR', 'comp.s_PR')
        # self.pyc_connect_des_od('comp.s_Wc', 'comp.s_Wc')
        # self.pyc_connect_des_od('comp.s_eff', 'comp.s_eff')
        # self.pyc_connect_des_od('comp.s_Nc', 'comp.s_Nc')

        
        # self.pyc_connect_des_od('turb.s_PR', 'turb.s_PR')
        # self.pyc_connect_des_od('turb.s_Wp', 'turb.s_Wp')
        # self.pyc_connect_des_od('turb.s_eff', 'turb.s_eff')
        # self.pyc_connect_des_od('turb.s_Np', 'turb.s_Np')
        
        # self.pyc_connect_des_od('gen.s_PR', 'gen.s_PR')
        # self.pyc_connect_des_od('gen.s_Wp', 'gen.s_Wp')
        # self.pyc_connect_des_od('gen.s_eff', 'gen.s_eff')
        # self.pyc_connect_des_od('gen.s_Np', 'gen.s_Np')
        
        # self.pyc_connect_des_od('inlet.Fl_O:stat:area', 'inlet.area')
        # self.pyc_connect_des_od('comp.Fl_O:stat:area', 'comp.area')

        # self.pyc_connect_des_od('turb.Fl_O:stat:area', 'turb.area')
        # self.pyc_connect_des_od('gen.Fl_O:stat:area', 'gen.area')
        
        super().setup()
        
class MPmotoring(pyc.MPCycle):
    
    def initialize(self):
        
        self.options.declare('SS_Solar',types=float,default=500., desc='SelfSupplied Solar Resource', upper=1000, lower=200)
        self.options.declare('Min_Solar',types=float,default=700., desc='SelfSupplied Solar Resource', upper=1000, lower=500)
        self.options.declare('Max_Solar',types=float,default=1100., desc='SelfSupplied Solar Resource', upper=1300, lower=1000)
        
        self.options.declare('No_od', default=False, desc='Solves only design mode')
        
        super().initialize()
        
    def setup(self):
        
        self.pyc_add_pnt('DESIGN', pnt=motoring(design=True))
        
        # for inlet area calculation MN must be set
        self.set_input_defaults('DESIGN.inlet.MN', 0.025)
        self.set_input_defaults('DESIGN.motor.MN', 0.025)
        # self.set_input_defaults('DESIGN.comp.MN', 0.03)
        # self.set_input_defaults('DESIGN.rec.MN', 0.04)
        # self.set_input_defaults('DESIGN.turb.MN', 0.03)
        
        # design point:
        self.set_input_defaults('DESIGN.Nmech', 25000.0, units='rpm')
        self.set_input_defaults('DESIGN.Gen_Nmech', 15000.0, units='rpm')
        
        # nozzle trial
        # self.set_input_defaults('DESIGN.nozz.PR',1.)
        
        self.pyc_add_cycle_param('nozz.Cv', 0.99)
        
        # Assign generation comp., rec., and turb.
        
        # self.set_input_defaults('DESIGN.comp.s_PR', self.options['comp_s_PR'])
        # self.set_input_defaults('DESIGN.comp.s_Wc', self.options['comp_s_Wc'])
        # self.set_input_defaults('DESIGN.comp.s_eff', self.options['comp_s_eff'])
        # self.set_input_defaults('DESIGN.comp.s_Nc', self.options['comp_s_Nc'])
        # self.set_input_defaults('DESIGN.comp.Fl_O:stat:area', self.options['comp_area'])
        
        # self.set_input_defaults('DESIGN.turb.s_PR', self.options['turb_s_PR'])
        # self.set_input_defaults('DESIGN.turb.s_Wp', self.options['turb_s_Wp'])
        # self.set_input_defaults('DESIGN.turb.s_eff', self.options['turb_s_eff'])
        # self.set_input_defaults('DESIGN.turb.s_Np', self.options['turb_s_Np'])
        # self.set_input_defaults('DESIGN.turb.Fl_O:stat:area', self.options['turb_area'])
        
        # self.set_input_defaults('DESIGN.rec.rec.s_RPC', self.options['rec_sRPC'])
        # self.set_input_defaults('DESIGN.rec.rec.s_INS', self.options['rec_sINS'])
        # self.set_input_defaults('DESIGN.rec.rec.L', self.options['rec_L'])
        # self.set_input_defaults('DESIGN.rec.Fl_O:stat:area', self.options['rec_area'])
        
        # OD part starts here!
        if not self.options['No_od']:
            self.od_MNs = 1e-6
            self.od_alts = 1e-6
            
            # ss_Solar = self.options['SS_Solar']
            # min_Solar = self.options['Min_Solar']
            # max_Solar = self.options['Max_Solar']
            
            # self.od_pts = ['T4_40','T4_30','T4_20']
            # self.od_pwrs = [ -40.,-30.,-20.]
            # self.Q_Solar = [min_Solar]
            # setting_mode = ['T4','T4','T4']
            
            self.od_pts = ['comp10','comp15','comp20','comp25','comp30','comp35','comp40','comp45','comp50']
            self.od_pwrs = [-10.,-15.,-20.,-25.,-30.,-35.,-40.,-45.,-50]
            # self.Q_Solar = [min_Solar]
            # setting_mode = ['comp']
            
            
            for i, pt in enumerate(self.od_pts):
                
                self.pyc_add_pnt(pt, pnt=motoring(design=False, setting_mode='comp'))#setting_mode[i]))
                self.set_input_defaults(pt + '.fc.MN', val=self.od_MNs)
                self.set_input_defaults(pt + '.fc.alt', self.od_alts, units='ft')
                self.set_input_defaults(pt + '.balance.pwr_target', self.od_pwrs[i], units='W')
                # self.set_input_defaults(pt + '.rec.Q_Solar_In', self.Q_Solar[i], units='W')
            
            # transfering design conditions to od.s
            self.pyc_connect_des_od('motor.s_PR', 'motor.s_PR')
            self.pyc_connect_des_od('motor.s_Wc', 'motor.s_Wc')
            self.pyc_connect_des_od('motor.s_eff', 'motor.s_eff')
            self.pyc_connect_des_od('motor.s_Nc', 'motor.s_Nc')
            self.pyc_connect_des_od('motor.Fl_O:stat:area', 'motor.area')

            self.pyc_connect_des_od('inlet.Fl_O:stat:area', 'inlet.area')

        super().setup()
        
        
        
        
        