#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 12:49:01 2022

@author: tufanakba

viewer patent
"""

import sys
import openmdao.api as om
import pycycle.api as pyc

def viewer_generation(prob, pt, file=sys.stdout):
    
    """
    print a report of all the relevant cycle properties
    """

    # summary_data = (prob[pt + '.fc.Fl_O:stat:MN'], prob[pt + '.fc.alt'], prob[pt + '.inlet.Fl_O:stat:W'],
    #                 prob[pt + '.perf.Fn'], prob[pt + '.perf.Fg'], prob[pt + '.inlet.F_ram'],
    #                 prob[pt + '.perf.OPR'])  # , prob[pt+'.perf.TSFC'])
    
    summary_data = (prob[pt + '.fc.Fl_O:stat:MN'], prob[pt + '.fc.alt'], prob[pt + '.inlet.Fl_O:stat:W'])

    print(file=file, flush=True)
    print(file=file, flush=True)
    print(file=file, flush=True)
    print("----------------------------------------------------------------------------", file=file, flush=True)
    print("                              POINT:", pt, file=file, flush=True)
    print("----------------------------------------------------------------------------", file=file, flush=True)
    print("                       PERFORMANCE CHARACTERISTICS", file=file, flush=True)
    print("    Mach      Alt       W      Fn      Fg    Fram     OPR     TSFC  ", file=file, flush=True)
    print(" %7.5f  %7.1f %7.5f  -  -  -  -  -" % summary_data, file=file, flush=True)

    fs_names = ['fc.Fl_O', 'inlet.Fl_O', 'comp.Fl_O', 'rec.Fl_O',
                'turb.Fl_O','gen.Fl_O', 'nozz.Fl_O']
    fs_full_names = [f'{pt}.{fs}' for fs in fs_names]
    pyc.print_flow_station(prob, fs_full_names, file=file)

    comp_names = ['comp']
    comp_full_names = [f'{pt}.{c}' for c in comp_names]
    pyc.print_compressor(prob, comp_full_names, file=file)

    # pyc.print_burner(prob, [f'{pt}.burner'])

    turb_names = ['turb','gen']
    turb_full_names = [f'{pt}.{t}' for t in turb_names]
    pyc.print_turbine(prob, turb_full_names, file=file)

    noz_names = ['nozz']
    noz_full_names = [f'{pt}.{n}' for n in noz_names]
    pyc.print_nozzle(prob, noz_full_names, file=file)

    shaft_names = ['HPshaft','LPshaft']
    shaft_full_names = [f'{pt}.{s}' for s in shaft_names]
    pyc.print_shaft(prob, shaft_full_names, file=file)
    
    viewer2(prob, pt, file=sys.stdout)
    map_plots(prob, pt)
    
def viewer_motoring(prob, pt, file=sys.stdout):
    
    """
    print a report of all the relevant cycle properties
    """

    # summary_data = (prob[pt + '.fc.Fl_O:stat:MN'], prob[pt + '.fc.alt'], prob[pt + '.inlet.Fl_O:stat:W'],
    #                 prob[pt + '.perf.Fn'], prob[pt + '.perf.Fg'], prob[pt + '.inlet.F_ram'],
    #                 prob[pt + '.perf.OPR'])  # , prob[pt+'.perf.TSFC'])
    
    summary_data = (prob[pt + '.fc.Fl_O:stat:MN'], prob[pt + '.fc.alt'], prob[pt + '.inlet.Fl_O:stat:W'])

    print(file=file, flush=True)
    print(file=file, flush=True)
    print(file=file, flush=True)
    print("----------------------------------------------------------------------------", file=file, flush=True)
    print("                              POINT:", pt, file=file, flush=True)
    print("----------------------------------------------------------------------------", file=file, flush=True)
    print("                       PERFORMANCE CHARACTERISTICS", file=file, flush=True)
    print("    Mach      Alt       W      Fn      Fg    Fram     OPR     TSFC  ", file=file, flush=True)
    print(" %7.5f  %7.1f %7.5f  -  -  -  -  -" % summary_data, file=file, flush=True)

    fs_names = ['fc.Fl_O', 'inlet.Fl_O','motor.Fl_O', 'comp.Fl_O', 'rec.Fl_O',
                'turb.Fl_O', 'nozz.Fl_O']
    fs_full_names = [f'{pt}.{fs}' for fs in fs_names]
    pyc.print_flow_station(prob, fs_full_names, file=file)

    comp_names = ['motor','comp']
    comp_full_names = [f'{pt}.{c}' for c in comp_names]
    pyc.print_compressor(prob, comp_full_names, file=file)

    # pyc.print_burner(prob, [f'{pt}.burner'])

    turb_names = ['turb']
    turb_full_names = [f'{pt}.{t}' for t in turb_names]
    pyc.print_turbine(prob, turb_full_names, file=file)

    noz_names = ['nozz']
    noz_full_names = [f'{pt}.{n}' for n in noz_names]
    pyc.print_nozzle(prob, noz_full_names, file=file)

    shaft_names = ['HPshaft','LPshaft']
    shaft_full_names = [f'{pt}.{s}' for s in shaft_names]
    pyc.print_shaft(prob, shaft_full_names, file=file)
    
    viewer2(prob, pt, file=sys.stdout)
    map_plots_motoring(prob, pt)
    
    
def viewer2(prob, pt, file=sys.stdout):
    """
    print a report of all the relevant cycle properties with solar power
    """

    summary_data = (prob[pt + '.rec.Q_Solar_In'],
                    prob.get_val(pt + '.balance.pwr_target', units='W'))

    print(file=file, flush=True)
    print(file=file, flush=True)
    print(file=file, flush=True)
    print("----------------------------------------------------------------------------", file=file, flush=True)
    print("                              POINT:", pt, file=file, flush=True)
    print("----------------------------------------------------------------------------", file=file, flush=True)
    print("                       PERFORMANCE CHARACTERISTICS", file=file, flush=True)
    print("    Q_In      Power ", file=file, flush=True)
    print(" %7.5f  %7.1f " % summary_data, file=file, flush=True)
    
def map_plots(prob, pt):
    
    comp_names = ['comp']
    comp_full_names = [f'{pt}.{c}' for c in comp_names]
    pyc.plot_compressor_maps(prob, comp_full_names)

    turb_names = ['turb','gen']
    turb_full_names = [f'{pt}.{c}' for c in turb_names]
    pyc.plot_turbine_maps(prob, turb_full_names)
    
def map_plots_motoring(prob, pt):
    
    comp_names = ['motor','comp']
    comp_full_names = [f'{pt}.{c}' for c in comp_names]
    pyc.plot_compressor_maps(prob, comp_full_names)

    turb_names = ['turb']
    turb_full_names = [f'{pt}.{c}' for c in turb_names]
    pyc.plot_turbine_maps(prob, turb_full_names)
    

def sankey(prob, pt):
    
    
    # not ready yet
    m = prob.get_val(pt+'.balance.W', units='g/s')
    
    
    # h_comp_in = prob.get_val(pt+'.inlet.Fl_O:tot:h', units='kJ/kg') #h1
    h_rec_in = prob.get_val(pt+'.comp.Fl_O:tot:h', units='kJ/kg') #h2
    h_rec_out = prob.get_val(pt+'.rec.Fl_O:tot:h', units='kJ/kg') #h3
    h_turb_out = prob.get_val(pt+'.turb.Fl_O:tot:h', units='kJ/kg') #h4
    
    P_comp_in = prob.get_val(pt+'.comp.power', units='W')*-1 #P_comp
    # P_comp_out = m*(h_rec_in-h_comp_in) 
    
    # del_comp = P_comp_in-P_comp_out
    
    P_rec_in = prob.get_val(pt+'.rec.Q_Solar_In', units='W')
    P_rec_out = m*(h_rec_out-h_rec_in)
    
    del_rec = float(P_rec_in - P_rec_out)
    
    P_turb_in = m*(h_rec_out-h_turb_out)
    # P_turb_out = prob.get_val(pt+'.turb.power', units='W')
    
    # del_turb = P_turb_in-P_turb_out
    
    P_MG_in = prob.get_val(pt+'.shaft.pwr_net', units='W')
    P_MG_out = prob.get_val(pt + '.balance.pwr_target', units='W')
    
    del_MG = P_MG_in-P_MG_out
    turb_loss = float(P_rec_out - P_turb_in)
    

    
    from matplotlib.sankey import Sankey
    from matplotlib import pyplot as plt
    
    fig = plt.figure(figsize=(15,8))
    ax = fig.add_subplot(1, 1, 1, xticks=[], yticks=[],
                        title="Energy Transfer in "+pt+" Condition")
    sankey = Sankey(ax=ax, 
                    scale=0.0005, 
                    offset= 0.1,
                    format = '%d')
    sankey.add(flows=[float(P_rec_in),float(-(P_rec_out)),-float(del_rec)],
                labels=['Q_Solar','Turbine','Loss'],
                orientations=[0,0,-1],
                # trunklength = 1,
                edgecolor = '#58A4B0',
                facecolor = '#58A4B0')
    sankey.add(flows=[float(P_rec_out), -float(P_MG_in), -float(turb_loss), -float(P_comp_in)], 
                labels = ['Receiver', 'MG', 'Heat_loss', 'P_comp',], 
                orientations=[0, 0, -1, 1],#arrow directions,
                # pathlengths = [3,3,3,3,3],
                prior=0, #which sankey are you connecting to (0-indexed)
                connect=(1,0), #flow number to connect: (prior, this)
    #             # trunklength = 1,
                edgecolor = '#027368',
                facecolor = '#027368')
    sankey.add(flows=[float(P_MG_in), -float(P_MG_out), -float(del_MG)], 
                labels = ['Shaft', 'P_El', 'MG_loss'], 
                orientations=[0, 0, -1],#arrow directions,
                # pathlengths = [3,3,3,3,3],
                prior=1, #which sankey are you connecting to (0-indexed)
                connect=(1,0), #flow number to connect: (prior, this)
    #             # trunklength = 1,
                edgecolor = '#05F3F8',
                facecolor = '#05F3F8')
    sankey.finish()

    
    # print([Q,P_comp_in,P_rec,P_turb,P_comp,P_MG_in,P_el])
    # print(float(Q),float(P_comp_in),float(P_rec),float(P_turb),float(-P_comp),float(P_MG_in),float(P_el))
    
    # # Sankey(flows=[float(Q),float(P_comp_in),float(P_rec),float(P_turb),float(-P_comp),float(P_MG_in),float(P_el)], labels=['Q','P_comp_in','P_rec','P_turb','P_comp','P_MG_in','P_el'], orientations=[0, -1, 1, 1, 1, 0,0]).finish()
    # Sankey(flows=[0.0,float(P_comp_in),float(-P_comp)], labels=['','P_comp_in','P_comp_out'], orientations=[0,0,-1]).finish()
    # plt.show()
    
    
    
    
    
    