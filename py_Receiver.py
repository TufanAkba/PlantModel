#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 01:22:54 2022

@author: tufanakba
pyCycle class definition for receiver
"""

from pycycle.element_base import Element
import openmdao.api as om
import pycycle.api as pyc

from pycycle.flow_in import FlowIn
from pycycle.thermo.thermo import Thermo

from pycycle.passthrough import PassThrough

from receiver import ReceiverSubProblem

class py_Receiver(Element):
    
    """
    A receiver design element that heats up the air and sizes the receiver.
    
    --------------
    Flow Stations
    --------------
    Fl_I
    Fl_O

    -------------
    Design
    -------------
        inputs
        --------
        I_solar
        r_1 & min. thickness
        Mat.s
        Max. T_allow
        tol (as percentage)
        m_dot


        outputs
        --------
        t_RPC
        t_INS
        lenght
        T_out
        eff


    -------------
    Off-Design
    -------------
        inputs
        --------
        I_solar
        dimensions
        Mat.s
        Max. T_allow
        tol (as percentage)
        m_dot

        outputs
        --------
        T_out
        eff
    
    """
    
    def initialize(self):
        
        self.options.declare('statics', default=True, desc='If True, calculate static properties.')
        self.options.declare('opt',types=bool, default=False, desc='If True, optimizes the receiver, in design mode')
        
        self.default_des_od_conns = [
            # (design src, off-design target)
            ('Fl_O:stat:area', 'area')
        ]
        
        self.options.declare('od_only', default=False, desc='For motoring prevents design mode')
        
        super().initialize()
        
    def pyc_setup_output_ports(self):
        
        self.copy_flow('Fl_I', 'Fl_O')
    
    def setup(self):
        
        thermo_method = self.options['thermo_method']
        thermo_data = self.options['thermo_data']
        statics = self.options['statics']
        design = self.options['design']
        if self.options['od_only']:
            design=False
        
        opt = self.options['opt']

        # elements = self.options['elements']
        composition = self.Fl_I_data['Fl_I']

        # Create inlet flow station
        flow_in = FlowIn(fl_name='Fl_I')
        self.add_subsystem('flow_in', flow_in, promotes=['Fl_I:tot:*', 'Fl_I:stat:*'])

        if statics:
            if design:
                #   Calculate static properties
                
                # self._problem = prob = om.Problem()
                # prob.driver = om.ScipyOptimizeDriver()
                # prob.driver.options["optimizer"] = "SLSQP"
                
                # prob.model.add_subsystem('rec', Receiver(),
                #                     promotes_inputs=[('Mass_Flow', 'Fl_I:stat:W'),('cp','Fl_I:tot:Cp'),('T_fluid_in','Fl_I:tot:T'),'Tamb','Q_Solar_In'],
                #                     promotes_outputs=[])
                
                # prob.model.set_input_defaults('rec.L',0.6, units='m')
                # prob.model.add_design_var('rec.L',lower = 0.02,upper = 0.07, units='m', scaler= 15)
                # prob.model.add_objective('rec.eff_S2G',scaler=-1, adder=-1)#, adder=-1,scaler=100)#scaling should be increased
                # prob.setup()
                
                # prob.run_driver()
                
                # self.add_subsystem('rec', Receiver(),
                #                    promotes_inputs=[('Mass_Flow', 'Fl_I:stat:W'),('cp','Fl_I:tot:Cp'),('T_fluid_in','Fl_I:tot:T'),'Tamb','Q_Solar_In'],
                #                    promotes_outputs=[])
                
                self.add_subsystem('rec', ReceiverSubProblem(design=design,opt=opt),
                                   promotes_inputs=[('Mass_Flow', 'Fl_I:stat:W'),('cp','Fl_I:tot:Cp'),('T_fluid_in','Fl_I:tot:T'),'Tamb','Q_Solar_In'],
                                   promotes_outputs=['*'])
                
                # Calculate real flow station properties
                real_flow = Thermo(mode='total_TP', fl_name='Fl_O:tot', 
                                   method=thermo_method, 
                                   thermo_kwargs={'composition':composition, 
                                                  'spec':thermo_data})
                self.add_subsystem('real_flow', real_flow,
                                   # promotes_inputs=[('T','Fl_I:tot:T'),('composition', 'Fl_I:tot:composition'),('P','Fl_I:tot:P')],
                                   promotes_inputs=[('composition', 'Fl_I:tot:composition'),('P','Fl_I:tot:P')],
                                   promotes_outputs=['Fl_O:*'])
                
                self.connect('T_fluid_out', 'real_flow.T')
                
                out_stat = Thermo(mode='static_MN', fl_name='Fl_O:stat', 
                                  method=thermo_method, 
                                  thermo_kwargs={'composition':composition, 
                                                 'spec':thermo_data})
                self.add_subsystem('out_stat', out_stat,
                                   promotes_inputs=[('composition', 'Fl_I:tot:composition'), ('W', 'Fl_I:stat:W'), 'MN'],
                                   promotes_outputs=['Fl_O:stat:*'])

                self.connect('Fl_O:tot:S', 'out_stat.S')
                self.connect('Fl_O:tot:h', 'out_stat.ht')
                self.connect('Fl_O:tot:P', 'out_stat.guess:Pt')
                self.connect('Fl_O:tot:gamma', 'out_stat.guess:gamt')
                

            else:
                
                self.add_subsystem('rec', ReceiverSubProblem(design=design),
                                   promotes_inputs=[('Mass_Flow', 'Fl_I:stat:W'),('cp','Fl_I:tot:Cp'),('T_fluid_in','Fl_I:tot:T'),'Tamb','Q_Solar_In'],
                                   promotes_outputs=['*'])
                
                # Calculate real flow station properties
                real_flow = Thermo(mode='total_TP', fl_name='Fl_O:tot', 
                                   method=thermo_method, 
                                   thermo_kwargs={'composition':composition, 
                                                  'spec':thermo_data})
                self.add_subsystem('real_flow', real_flow,
                                   promotes_inputs=[('composition', 'Fl_I:tot:composition'),('P','Fl_I:tot:P')],
                                   promotes_outputs=['Fl_O:*'])
                
                self.connect('T_fluid_out', 'real_flow.T')
                
                # Calculate static properties
                out_stat = Thermo(mode='static_A', fl_name='Fl_O:stat', 
                                  method=thermo_method, 
                                  thermo_kwargs={'composition':composition, 
                                                 'spec':thermo_data})
                prom_in = [('composition', 'Fl_I:tot:composition'),
                           ('W', 'Fl_I:stat:W'),
                           'area']
                prom_out = ['Fl_O:stat:*']
                self.add_subsystem('out_stat', out_stat, promotes_inputs=prom_in,
                                   promotes_outputs=prom_out)

                self.connect('Fl_O:tot:S', 'out_stat.S')
                self.connect('Fl_O:tot:h', 'out_stat.ht')
                self.connect('Fl_O:tot:P', 'out_stat.guess:Pt')
                self.connect('Fl_O:tot:gamma', 'out_stat.guess:gamt')
                

        else:
            self.add_subsystem('W_passthru', PassThrough('Fl_I:stat:W', 'Fl_O:stat:W', 0.0, units= "lbm/s"),
                               promotes=['*'])

        super().setup()