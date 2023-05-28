#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 19:55:14 2022

@author: tufanakba
Surr visualization
Meta model test for optimization
"""

import numpy as np
import openmdao.api as om

class surr(om.MetaModelUnStructuredComp):
    
    def initialize(self):
        self.options.declare('test_folder',default='test_folder',
                             desc='Test folder location of resp. surf.')
        self.options.declare('kriging',default=False,
                             desc='Select kriging or response surface method')
        
        super().initialize()
    
    def setup(self):
        
        test_folder = self.options['test_folder']

        self.add_input('Tfi',training_data=np.loadtxt(test_folder + '/Tfi.csv'), units='K')
        self.add_input('m_dot',training_data=np.loadtxt(test_folder + '/m_dot.csv'), units='kg/s')
        self.add_input('rpc',training_data=np.loadtxt(test_folder + '/rpc.csv'), units='m')
        self.add_input('ins',training_data=np.loadtxt(test_folder + '/ins.csv'), units='m')
        self.add_input('L',training_data=np.loadtxt(test_folder + '/L.csv'), units='m')
        
        if self.options['kriging']:
            self.add_output('vol',training_data=np.loadtxt(test_folder + '/vol.csv'), surrogate=om.KrigingSurrogate(eval_rmse= True), units='m**3')
            self.add_output('Tfo',training_data=np.loadtxt(test_folder + '/Tfo.csv'), surrogate=om.KrigingSurrogate(eval_rmse= True), units='K')
            self.add_output('T_o',training_data=np.loadtxt(test_folder + '/T_o.csv'), surrogate=om.KrigingSurrogate(eval_rmse= True), units='K')
        
        else:
            self.add_output('vol',training_data=np.loadtxt(test_folder + '/vol.csv'), surrogate=om.ResponseSurface(), units='m**3')
            self.add_output('Tfo',training_data=np.loadtxt(test_folder + '/Tfo.csv'), surrogate=om.ResponseSurface(), units='K')
            self.add_output('T_o',training_data=np.loadtxt(test_folder + '/T_o.csv'), surrogate=om.ResponseSurface(), units='K')
            
        self.declare_partials(['Tfo','T_o'],'*', method='fd')
        self.declare_partials('vol', ['rpc','ins','L'], method='fd')
        
        super().setup()
        
if __name__ == "__main__":
    
    import time
    
    st = time.time()
    test_folder='test_folder'
    
    meta = om.MetaModelUnStructuredComp(default_surrogate=om.ResponseSurface())
    
    meta.add_input('Tfi',training_data=np.loadtxt(test_folder + '/Tfi.csv'), units='K')
    meta.add_input('m_dot',training_data=np.loadtxt(test_folder + '/m_dot.csv'), units='kg/s')
    meta.add_input('rpc',training_data=np.loadtxt(test_folder + '/rpc.csv'), units='m')
    meta.add_input('ins',training_data=np.loadtxt(test_folder + '/ins.csv'), units='m')
    meta.add_input('L',training_data=np.loadtxt(test_folder + '/L.csv'), units='m')
    
    meta.add_output('vol',training_data=np.loadtxt(test_folder + '/vol.csv'), units='m**3')
    meta.add_output('Tfo',training_data=np.loadtxt(test_folder + '/Tfo.csv'), units='K')
    meta.add_output('T_o',training_data=np.loadtxt(test_folder + '/T_o.csv'), units='K')
    
    p = om.Problem()
    p.model.add_subsystem('meta', meta)
    p.setup()
    
    
    p.run_model()
    
    p.model.list_outputs(units=True,prom_name=True,shape=False)
    p.model.list_inputs(units=True,prom_name=True,shape=False)

    print("time", time.time() - st)

    # for running the viewer code paste to iPython Console
    # !openmdao view_mm MDAOMetaModel_Vis.py
    

