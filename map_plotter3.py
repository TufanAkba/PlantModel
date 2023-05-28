#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  3 21:49:34 2022

@author: tufanakba
map plotter for patent cycle
"""

import numpy as np
# protection incase env doesn't have matplotlib installed, since its not strictly required
try: 

    import matplotlib.pyplot as plt
except ImportError: 
    plt = None
  
  
def comp_map(prob, gen):
    eff_vals=np.array([0,0.5,0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95,1.0])
    alphas=[0]
    
    if gen:
        comp_names = ['comp']
    else:
        comp_names = ['motor','comp']
    
    element_names = [f'DESIGN.{c}' for c in comp_names]
    
    
    for e_id, e_name in enumerate(element_names):
        
        comp = prob.model._get_subsystem(e_name)
        map_data = comp.options['map_data']
        
        s_Wc = prob[e_name+'.s_Wc']
        s_PR = prob[e_name+'.s_PR']
        s_eff = prob[e_name+'.s_eff']
        s_Nc = prob[e_name+'.s_Nc']
        
        RlineMap, NcMap = np.meshgrid(map_data.RlineMap, map_data.NcMap, sparse=False)
        
        for alpha in alphas:
            scaled_PR = (map_data.PRmap[alpha,:,:] - 1.) * s_PR + 1.
            
            plt.figure(figsize=(11,8))
            Nc = plt.contour(map_data.WcMap[alpha,:,:]*s_Wc,scaled_PR,NcMap*s_Nc,colors='k',levels=map_data.NcMap*s_Nc)
            R = plt.contour(map_data.WcMap[alpha,:,:]*s_Wc,scaled_PR,RlineMap,colors='k',levels=map_data.RlineMap)
            eff = plt.contourf(map_data.WcMap[alpha,:,:]*s_Wc,scaled_PR,map_data.effMap[alpha,:,:]*s_eff,levels=eff_vals)
    
            plt.colorbar(eff)
            comp_pt = comp_names[e_id]
            
            comp_name = f'DESIGN.{comp_pt}'
            plt.plot(prob[comp_name+'.Wc'], prob[comp_name+'.PR'][0], 'rs')
            
            for pt in prob.model.od_pts:
                
                comp_name = f'{pt}.{comp_pt}'
                plt.plot(prob[comp_name+'.Wc'], prob[comp_name+'.PR'][0], 'ko')
              
            plt.clabel(Nc, fontsize=9, inline=False)
            plt.clabel(R, fontsize=9, inline=False)
            # plt.clabel(eff, fontsize=9, inline=True)
            
            plt.xlabel('Wc, lbm/s')
            plt.ylabel('PR')
            plt.title(e_name)
            plt.show()
            # plt.savefig(e_name+'.pdf')

def turb_map(prob,gen):
    eff_vals=np.array([0,0.5,0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95,1.0])
    alphas=[0]
    
    if gen:
        turb_names = ['turb','gen']
    else:
        turb_names = ['turb']
    
    element_names = [f'DESIGN.{c}' for c in turb_names]
    
    for e_id, e_name in enumerate(element_names):
        comp = prob.model._get_subsystem(e_name)
        map_data = comp.options['map_data']

        s_Wp = prob[e_name+'.s_Wp']
        s_PR = prob[e_name+'.s_PR']
        s_eff = prob[e_name+'.s_eff']
        s_Np = prob[e_name+'.s_Np']

        PRmap, NpMap = np.meshgrid(map_data.PRmap, map_data.NpMap, sparse=False)
        
        for alpha in alphas:
            scaled_PR = (PRmap - 1.) * s_PR + 1.
    
            plt.figure(figsize=(11,8))
            Nc = plt.contour(map_data.WpMap[alpha,:,:]*s_Wp,scaled_PR,NpMap*s_Np,colors='k',levels=map_data.NpMap*s_Np)
            eff = plt.contourf(map_data.WpMap[alpha,:,:]*s_Wp,scaled_PR,map_data.effMap[alpha,:,:]*s_eff,levels=eff_vals)
    
            plt.colorbar(eff)
            
            turb_pt = turb_names[e_id]
            turb_name = f'DESIGN.{turb_pt}'
            plt.plot(prob[turb_name+'.Wp'], prob[turb_name+'.PR'][0], 'rs')
            
            for pt in prob.model.od_pts:
                
                turb_name = f'{pt}.{turb_pt}'
                plt.plot(prob[turb_name+'.Wp'], prob[turb_name+'.PR'][0], 'ko')
                
            plt.clabel(Nc, fontsize=9, inline=False)
            # plt.clabel(eff, fontsize=9, inline=True)

            plt.xlabel('Wc, lbm/s')
            plt.ylabel('PR')
            plt.title(e_name)
            plt.show()
            # plt.savefig(e_name+'.pdf')