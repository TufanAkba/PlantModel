#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 16:34:25 2022

@author: tufanakba
viewer code for complex2
"""

import sys
import openmdao.api as om
import pycycle.api as pyc

def viewer(prob, pt, file=sys.stdout):
    """
    print a report of all the relevant cycle properties
    """

    # summary_data = (prob[pt + '.fc.Fl_O:stat:MN'], prob[pt + '.fc.alt'], prob[pt + '.inlet.Fl_O:stat:W'],
    #                 prob[pt + '.perf.Fn'], prob[pt + '.perf.Fg'], prob[pt + '.inlet.F_ram'],
    #                 prob[pt + '.perf.OPR'])  # , prob[pt+'.perf.TSFC'])
    
    summary_data = (prob[pt + '.fc.Fl_O:stat:MN'], prob[pt + '.fc.alt'], prob[pt + '.inlet.Fl_O:stat:W'])#,
                    # prob[pt + '.perf.Fn'], prob[pt + '.perf.Fg'], prob[pt + '.inlet.F_ram'],
                    # prob[pt + '.perf.OPR'])  # , prob[pt+'.perf.TSFC'])

    print(file=file, flush=True)
    print(file=file, flush=True)
    print(file=file, flush=True)
    print("----------------------------------------------------------------------------", file=file, flush=True)
    print("                              POINT:", pt, file=file, flush=True)
    print("----------------------------------------------------------------------------", file=file, flush=True)
    print("                       PERFORMANCE CHARACTERISTICS", file=file, flush=True)
    print("    Mach      Alt       W      Fn      Fg    Fram     OPR     TSFC  ", file=file, flush=True)
    print(" %7.5f  %7.1f %7.5f  -  -  -  -  -" % summary_data, file=file, flush=True)

    fs_names = ['fc.Fl_O', 'inlet.Fl_O', 'LPcomp.Fl_O','HPcomp.Fl_O', 'rec.Fl_O',
                'HPturb.Fl_O','LPturb.Fl_O', 'nozz.Fl_O']
    fs_full_names = [f'{pt}.{fs}' for fs in fs_names]
    pyc.print_flow_station(prob, fs_full_names, file=file)

    comp_names = ['LPcomp','HPcomp']
    comp_full_names = [f'{pt}.{c}' for c in comp_names]
    pyc.print_compressor(prob, comp_full_names, file=file)

    # pyc.print_burner(prob, [f'{pt}.burner'])

    turb_names = ['LPturb','HPturb']
    turb_full_names = [f'{pt}.{t}' for t in turb_names]
    pyc.print_turbine(prob, turb_full_names, file=file)

    noz_names = ['nozz']
    noz_full_names = [f'{pt}.{n}' for n in noz_names]
    pyc.print_nozzle(prob, noz_full_names, file=file)

    shaft_names = ['HPshaft','LPshaft']
    shaft_full_names = [f'{pt}.{s}' for s in shaft_names]
    pyc.print_shaft(prob, shaft_full_names, file=file)
    
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
    
    comp_names = ['LPcomp','HPcomp']
    comp_full_names = [f'{pt}.{c}' for c in comp_names]
    pyc.plot_compressor_maps(prob, comp_full_names)

    turb_names = ['LPturb','HPturb']
    turb_full_names = [f'{pt}.{c}' for c in turb_names]
    pyc.plot_turbine_maps(prob, turb_full_names)


def sankey(prob, pt):
    
    m = prob.get_val(pt+'.balance.W', units='g/s')
    
    # h_hpcomp_in = prob.get_val(pt+'.LPcomp.Fl_O:tot:h', units='kJ/kg') #h2
    # h_lpcomp_in = prob.get_val(pt+'.inlet.Fl_O:tot:h', units='kJ/kg') #h1
    
    h_rec_in = prob.get_val(pt+'.HPcomp.Fl_O:tot:h', units='kJ/kg') #h3
    h_rec_out = prob.get_val(pt+'.rec.Fl_O:tot:h', units='kJ/kg') #h4
    
    # h_hpturb_out = prob.get_val(pt+'.HPturb.Fl_O:tot:h', units='kJ/kg') #h5
    h_lpturb_out = prob.get_val(pt+'.LPturb.Fl_O:tot:h', units='kJ/kg') #h6
    
    
    P_rec_in = prob.get_val(pt+'.rec.Q_Solar_In', units='W')
    P_rec_out = m*(h_rec_out-h_rec_in)
    del_rec = float(P_rec_in - P_rec_out)
    
    # print(f'Rec_in={P_rec_in} Rec_out={P_rec_out} del_rec={del_rec}')
    
    P_hpcomp_in = prob.get_val(pt+'.HPcomp.power', units='W')*-1 #P_hpc
    P_lpcomp_in = prob.get_val(pt+'.LPcomp.power', units='W')*-1 #P_lpc
    
    # print(f'P_hpc={P_hpcomp_in} P_lpc={P_lpcomp_in}')
    
    
    P_MG_in = prob.get_val(pt+'.LPshaft.pwr_net', units='W')
    P_MG_out = prob.get_val(pt + '.balance.pwr_target', units='W')
    
    del_MG = P_MG_in-P_MG_out
    
    # print(f'MG_in={P_MG_in} P_el={P_MG_out} del_MG={del_MG}')
    
    # print(m*(h_rec_in-h_lpturb_out))
    # print(f'm*(h5-h4)-P_hpc={m*(h_rec_out-h_hpturb_out)-P_hpcomp_in}')
    
    heatloss= float(m*(h_rec_in-h_lpturb_out))
    
    
    # P_hpcomp_out = m*(h_rec_in-h_hpcomp_in)
    # P_lpcomp_out = m*(h_hpcomp_in-h_lpcomp_in)
    
    # del_lpcomp = P_lpcomp_in - P_lpcomp_out
    # del_hpcomp = P_hpcomp_in - P_hpcomp_out
    

    
    # P_hpturb_in = m*(h_rec_out-h_hpturb_out)
    # P_hpturb_out = prob.get_val(pt+'.HPturb.power', units='W')
    
    # P_lpturb_in = m*(h_hpturb_out-h_lpturb_out)
    # P_lpturb_out = prob.get_val(pt+'.LPturb.power', units='W')
    
    # del_hpturb = P_hpturb_in - P_hpturb_out
    # del_lpturb = P_lpturb_in - P_lpturb_out
    

    
    # hpturb_loss = float(P_rec_out - P_hpturb_in)
    # lpturb_loss = float(P_hpturb_out - P_lpturb_in)
    # lpturb_loss = float(P_lpturb_in-P_lpcomp_in-P_MG_in)
    
    
    # print(f'LPcompressor: {P_lpcomp_in}-->{P_lpcomp_out} ')
    # print(f'HPcompressor: {P_hpcomp_in}-->{P_hpcomp_out} ')
    # print(f'receiver: {P_rec_in}-->{P_rec_out}')
    # print(f'HPturbine: {P_hpturb_in}-->{P_hpturb_out}')
    # print(f'LPturbine: {P_lpturb_in}-->{P_lpturb_out}')
    # print(f'MG: {P_MG_in}-->{P_MG_out}')
    
    # print(del_lpcomp,del_hpcomp, del_rec, del_hpturb, del_lpturb, del_MG, P_hpcomp_in,P_lpcomp_in,P_MG_in,lpturb_loss)
    # print(m*(h_rec_out-h_hpturb_out)-P_hpcomp_in)
    # print([float(P_rec_in),float(-(P_rec_out)),-float(del_rec)])
    # print([float(P_rec_out),float(-P_hpcomp_in)])
    
    # print([float(P_lpturb_in), -float(P_MG_in), -float(lpturb_loss), -float(P_lpcomp_in)])
    

    
    from matplotlib.sankey import Sankey
    from matplotlib import pyplot as plt
    
    fig = plt.figure(figsize=(15,8))
    ax = fig.add_subplot(1, 1, 1, xticks=[], yticks=[],
                        title="Energy Transfer in "+pt+" Condition")
    sankey = Sankey(ax=ax, 
                    scale=0.0006, 
                    offset= 0.15,
                    format = '%d')
    
    sankey.add(flows=[float(P_rec_in),float(-(P_rec_out)),-float(del_rec)], #ok
                labels=['Q_Solar','HPT','Rec_Loss'],
                orientations=[0,0,-1],
                # trunklength = 1,
                edgecolor = '#58A4B0',
                facecolor = '#58A4B0')
    
    sankey.add(flows=[float(P_rec_out), -float(P_rec_out-P_hpcomp_in), -float(P_hpcomp_in)], 
                labels = ['Rec', 'LPT', 'P_HPC',], 
                orientations=[0, 0, 1],#arrow directions,
                # pathlengths = [3,3,3,3,3],
                prior=0, #which sankey are you connecting to (0-indexed)
                connect=(1,0), #flow number to connect: (prior, this)
    #             # trunklength = 1,
                edgecolor = '#027368',
                facecolor = '#027368')
    
    sankey.add(flows=[float(P_rec_out-P_hpcomp_in), -float(P_MG_in), float(heatloss), -float(P_lpcomp_in)], 
                labels = ['', 'MG', 'Heat_loss', 'P_LPC',], 
                orientations=[0, 0, -1, 1],#arrow directions,
                # pathlengths = [3,3,3,3,3],
                prior=1, #which sankey are you connecting to (0-indexed)
                connect=(1,0), #flow number to connect: (prior, this)
    #             # trunklength = 1,
                edgecolor = '#746AB0',
                facecolor = '#746AB0')
    
    sankey.add(flows=[float(P_MG_in), -float(P_MG_out), -float(del_MG)], #ok
                labels = ['Shaft', 'P_El', 'MG_loss'], 
                orientations=[0, 0, -1],#arrow directions,
                # pathlengths = [3,3,3,3,3],
                prior=2, #which sankey are you connecting to (0-indexed)
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
    
    
    
    
    
    