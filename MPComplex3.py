#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 13:10:08 2022

@author: tufanakba
LP - HP turbo model
MG connected to HP
"""

import openmdao.api as om
import pycycle.api as pyc
from py_Receiver import py_Receiver
from components.comp_map import AXI5
from components.MG3 import MG
from viewer2 import viewer, viewer2, map_plots, sankey
from receiver import ReceiverSubProblem

class Complex3(pyc.Cycle):

    def initialize(self):
        # Initialize the model here by setting option variables such as a switch for design vs off-des cases
        self.options.declare('setting_mode', default='T4', values=['T4', 'nozzle'])

        super().initialize()
    
    def setup(self):
        
        design = self.options['design']

        self.add_subsystem('fc', pyc.FlightConditions())
        self.add_subsystem('inlet', pyc.Inlet())
        
        # TODO: set maps here and assign the comp.s
        comp_map = AXI5
        # comp_map = pyc.AXI5
        turb_map = pyc.LPT2269
        
        self.add_subsystem('LPcomp', pyc.Compressor(map_data=comp_map, map_extrap=True), promotes_inputs = [('Nmech','LP_Nmech')])
        self.add_subsystem('HPcomp', pyc.Compressor(map_data=comp_map, map_extrap=True), promotes_inputs =[('Nmech','HP_Nmech')])
        
        self.add_subsystem('rec', py_Receiver())
        
        self.add_subsystem('HPturb', pyc.Turbine(map_data=turb_map, map_extrap=True), promotes_inputs =[('Nmech','HP_Nmech')])
        self.add_subsystem('LPturb', pyc.Turbine(map_data=turb_map, map_extrap=True), promotes_inputs =[('Nmech','LP_Nmech')])
        
        self.add_subsystem('nozz', pyc.Nozzle(nozzType='CD', lossCoef='Cv'))
        
        self.add_subsystem('MG', MG(), promotes_inputs=[('n','LP_Nmech')])
        
        self.add_subsystem('HPshaft', pyc.Shaft(num_ports=2), promotes_inputs =[('Nmech','HP_Nmech')])
        self.add_subsystem('LPshaft', pyc.Shaft(num_ports=2), promotes_inputs =[('Nmech','LP_Nmech')])
        
        self.pyc_connect_flow('fc.Fl_O', 'inlet.Fl_I', connect_w=False)
        self.pyc_connect_flow('inlet.Fl_O', 'LPcomp.Fl_I')
        self.pyc_connect_flow('LPcomp.Fl_O', 'HPcomp.Fl_I')
        self.pyc_connect_flow('HPcomp.Fl_O', 'rec.Fl_I')
        self.pyc_connect_flow('rec.Fl_O', 'HPturb.Fl_I')
        self.pyc_connect_flow('HPturb.Fl_O', 'LPturb.Fl_I')
        self.pyc_connect_flow('LPturb.Fl_O', 'nozz.Fl_I')
        
        self.connect('HPcomp.trq', 'HPshaft.trq_0')
        self.connect('HPturb.trq', 'HPshaft.trq_1')
        self.connect('HPshaft.trq_net', 'MG.trq')
        
        self.connect('LPcomp.trq', 'LPshaft.trq_0')
        self.connect('LPturb.trq', 'LPshaft.trq_1')

        
        self.connect('fc.Fl_O:stat:P', 'nozz.Ps_exhaust')
        
        balance = self.add_subsystem('balance', om.BalanceComp())
        if design:
            
            balance.add_balance('W', lower=0.0001, upper=0.01, units='lbm/s', eq_units='degC', rhs_name='T4_target')
            self.connect('balance.W', 'inlet.Fl_I:stat:W')
            self.connect('rec.Fl_O:tot:T', 'balance.lhs:W')
            
            balance.add_balance('HPturb_PR', val=2., lower=2., upper=5., eq_units='W', rhs_name='pwr_target')
            self.connect('balance.HPturb_PR', 'HPturb.PR')
            self.connect('MG.P_el', 'balance.lhs:HPturb_PR')
            
            balance.add_balance('LPturb_PR', val=2.0, lower=1.25, upper=2.9, eq_units='hp', rhs_val=0.)
            self.connect('balance.LPturb_PR', 'LPturb.PR')
            self.connect('LPshaft.pwr_net', 'balance.lhs:LPturb_PR')
            
        
        else:
            
            balance.add_balance('HP_Nmech', units='rpm', lower=10000., upper=17250., eq_units='W', rhs_name='pwr_target')
            self.connect('balance.HP_Nmech', 'HP_Nmech')
            self.connect('MG.P_el', 'balance.lhs:HP_Nmech')
            
            balance.add_balance('LP_Nmech', lower=19000., upper=29000., units='rpm', eq_units='hp', rhs_val=0.)
            self.connect('balance.LP_Nmech', 'LP_Nmech')
            self.connect('LPshaft.pwr_net', 'balance.lhs:LP_Nmech')
            
            if self.options['setting_mode'] == 'T4':
                # Nozzle alanı ile receiver outlet temperature'u korole etmek gerekecek! 1050 W'dan işlemek mantıklı!
                balance.add_balance('W', lower=0.0001, upper=0.01, units='lbm/s', eq_units='degC', rhs_val=1000,
                                    rhs_name='T4_target')
                # 1020'de çalışıyor
                self.connect('balance.W', 'inlet.Fl_I:stat:W')
                self.connect('rec.Fl_O:tot:T', 'balance.lhs:W')

            if self.options['setting_mode'] == 'nozzle':
                # balance.add_balance('W', lower=0.0001, upper=0.01, units='lbm/s', eq_units='inch**2')
                # self.connect('balance.W', 'inlet.Fl_I:stat:W')
                # self.connect('nozz.Throat:stat:area', 'balance.lhs:W')
                balance.add_balance('W', lower=0.0001, upper=0.01, units='lbm/s', eq_units=None, rhs_val=2.0)
                self.connect('balance.W', 'inlet.Fl_I:stat:W')
                self.connect('HPcomp.map.RlineMap', 'balance.lhs:W')
        
        self.set_order(['fc', 'inlet', 'LPcomp', 'HPcomp', 'rec', 'HPturb','LPturb', 'nozz','HPshaft','LPshaft', 'MG', 'balance'])
        
        newton = self.nonlinear_solver = om.NewtonSolver()
        newton.options['atol'] = 1e-6
        newton.options['rtol'] = 1e-6
        newton.options['iprint'] = 2
        newton.options['maxiter'] = 30
        newton.options['solve_subsystems'] = True
        newton.options['max_sub_solves'] = 100
        newton.options['reraise_child_analysiserror'] = False
        # Stall definition
        newton.options['stall_limit'] = 4
        newton.options['stall_tol'] = 1e-5

        newton.linesearch = om.ArmijoGoldsteinLS()
        newton.linesearch.options['iprint'] = 1
        newton.linesearch.options['maxiter'] = 4
        newton.linesearch.options['rho'] = 0.85  # work on impact of rho 0.85 for sample brayton
        # TODO: Make this false later
        newton.linesearch.options['print_bound_enforce']=False
       
        self.linear_solver = om.DirectSolver()

        super().setup()
        
class MPComplex3(pyc.MPCycle):
    
    def setup(self):
        
        self.pyc_add_pnt('DESIGN', Complex3(design=True))
        # for inlet area calculation MN must be set
        self.set_input_defaults('DESIGN.inlet.MN', 0.0250)
        self.set_input_defaults('DESIGN.LPcomp.MN', 0.030)
        self.set_input_defaults('DESIGN.HPcomp.MN', 0.040)
        self.set_input_defaults('DESIGN.rec.MN', 0.04)
        self.set_input_defaults('DESIGN.HPturb.MN', 0.03)
        self.set_input_defaults('DESIGN.LPturb.MN', 0.02)
        # design point:
        self.set_input_defaults('DESIGN.HP_Nmech', 15000.0, units='rpm')
        self.set_input_defaults('DESIGN.LP_Nmech', 25000.0, units='rpm')
        
        self.pyc_add_cycle_param('nozz.Cv', 0.99)
        
        self.od_MNs = 0.000001
        self.od_alts = 0.0
        
        # # simple optimization case!
        # self.od_pts = ['Od170']
        # self.od_pwrs = [170.]
        # self.Q_Solar = [960.]
        # setting_mode = ['T4']
        
        # self.od_pts = ['SelfSupplied','Motoring','Max_105', 'Min_75']
        # self.od_pwrs = [0.,-50.,180., 100.]
        # self.Q_Solar = [500.,475.,1050., 750.]
        # setting_mode = ['nozzle','nozzle','T4', 'nozzle']
        
        # self.od_pts = ['Od170','Max190','Max180','Min160','Min150','Min140','Min130','Min120','Min110','Min100']
        # self.od_pwrs = [170.,190.,180.,160.,150.,140.,130.,120.,110.,100]
        # self.Q_Solar = [850.,980.,910.,810.,770.,750.,740.,700.,660.,620.]
        # setting_mode = ['T4','T4','T4','T4','T4','T4','T4','nozzle','nozzle','nozzle']
        
        # self.od_pts = ['SS1000','SS900','SS800','SS700','SS600']
        # self.od_pwrs = [0.,0.,0.,0.,0.]
        # self.Q_Solar = [1000.,900.,800.,700.,600.]
        # setting_mode = ['T4','T4','T4','T4','nozzle']
        
        # This area needs to be set according to od conditions and balances
        for i, pt in enumerate(self.od_pts):
            self.pyc_add_pnt(pt, Complex3(design=False, setting_mode=setting_mode[i]))

            self.set_input_defaults(pt + '.fc.MN', val=self.od_MNs)
            self.set_input_defaults(pt + '.fc.alt', self.od_alts, units='ft')
            self.set_input_defaults(pt + '.balance.pwr_target', self.od_pwrs[i], units='W')
            self.set_input_defaults(pt + '.rec.Q_Solar_In', self.Q_Solar[i], units='W')
        
        # transfering design conditions to od.s
        self.pyc_connect_des_od('LPcomp.s_PR', 'LPcomp.s_PR')
        self.pyc_connect_des_od('LPcomp.s_Wc', 'LPcomp.s_Wc')
        self.pyc_connect_des_od('LPcomp.s_eff', 'LPcomp.s_eff')
        self.pyc_connect_des_od('LPcomp.s_Nc', 'LPcomp.s_Nc')
        self.pyc_connect_des_od('HPcomp.s_PR', 'HPcomp.s_PR')
        self.pyc_connect_des_od('HPcomp.s_Wc', 'HPcomp.s_Wc')
        self.pyc_connect_des_od('HPcomp.s_eff', 'HPcomp.s_eff')
        self.pyc_connect_des_od('HPcomp.s_Nc', 'HPcomp.s_Nc')
        
        self.pyc_connect_des_od('LPturb.s_PR', 'LPturb.s_PR')
        self.pyc_connect_des_od('LPturb.s_Wp', 'LPturb.s_Wp')
        self.pyc_connect_des_od('LPturb.s_eff', 'LPturb.s_eff')
        self.pyc_connect_des_od('LPturb.s_Np', 'LPturb.s_Np')
        self.pyc_connect_des_od('HPturb.s_PR', 'HPturb.s_PR')
        self.pyc_connect_des_od('HPturb.s_Wp', 'HPturb.s_Wp')
        self.pyc_connect_des_od('HPturb.s_eff', 'HPturb.s_eff')
        self.pyc_connect_des_od('HPturb.s_Np', 'HPturb.s_Np')
        
        self.pyc_connect_des_od('inlet.Fl_O:stat:area', 'inlet.area')
        self.pyc_connect_des_od('LPcomp.Fl_O:stat:area', 'LPcomp.area')
        self.pyc_connect_des_od('HPcomp.Fl_O:stat:area', 'HPcomp.area')
        self.pyc_connect_des_od('rec.Fl_O:stat:area', 'rec.area')
        self.pyc_connect_des_od('LPturb.Fl_O:stat:area', 'LPturb.area')
        self.pyc_connect_des_od('HPturb.Fl_O:stat:area', 'HPturb.area')
        
        super().setup()
        
        
        
        
        
        
        
        
        
        
        
        