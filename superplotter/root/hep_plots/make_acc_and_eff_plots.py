#!/usr/bin/env python

#--------------------------------------------------------------------------#
# plot, in the (mc1,mn1) plane the signal acceptance and efficiency
#
# acceptance = N_{fiducial} / N_{generated}
#            = (N events in SR with selection on truth objects) / ((N_{events generated} / (BR * filter_eff))
# efficiency = N_{fiducial-reco} / N_{fiducial}
#            = (N events in SR with selection on reco objects) / (N events in SR with selection on truth objects)
#
# For more details on these definitions, see
# https://indico.cern.ch/event/159188/material/slides/0?contribId=37
# and
# http://arxiv.org/pdf/1403.4853v1.pdf (appendix A)
#--------------------------------------------------------------------------#

# superplotter
from superplotter.region import *
from superplotter.signal import *
from superplotter.utils import *
from superplotter.plot_utils import *

# standard
import argparse
import glob
import sys

# ROOT
import ROOT as r
r.gROOT.SetBatch(True)
r.PyConfig.IgnoreCommandLineOptions = True

def get_n_passing_selection(signals, region, is_truth) :
    for sig in signals :
        hist = myTH1F("hist","hist", 2, 0, 2,"","")
        hist.Reset("ICE")
        cmd = "isOS>>hist" # TODO: find out why "isMC" won't work, "isOS" is unsafe
        cut = ""
        if is_truth :
            cut = "(%s) * isr_weight_nom"%(get_region_tcut(region)) # apply c1c1 re-weighting to truth
        else :
            cut = "(%s) * eventweight"%(get_region_tcut(region)) # reco samples' "eventweight" contains isr re-weighting
        sig.tree.Draw(cmd, cut)
        n_passing = hist.Integral(0,-1)
        if is_truth :
            sig.n_fiducial = n_passing
            print "N_fiducial(%s,%s): %s"%(sig.mX, sig.mY, str(n_passing))
        else :
            sig.n_fiducial_reco = n_passing
            print "N_fiducial_reco(%s,%s): %s"%(sig.mX, sig.mY, str(n_passing))
        hist.Delete()

def calculate_acceptance(signals) :
    '''
    We stored the N_generated in the truth_signals in the beginning
    so we use the truth signals in this function
    '''
    for sig in signals :
        n_fiducial = float(sig.n_fiducial)
        n_events_generated = float(sig.n_generated)
        branching_ratio = float(sig.branching_ratio)
        filter_eff = float(sig.filter_efficiency)
        acceptance = n_fiducial /( (n_events_generated)/(branching_ratio * filter_eff) )
        sig.acceptance = acceptance

def calculate_efficiency(truth, reco) :
    '''
    Store the final efficiencies in the truth Signals for consistency and 
    to avoid having to pass both truth and reco collections around
    '''
    for ts in truth :
        for rs in reco :
            if rs==ts : ts.efficiency = float(rs.n_fiducial_reco / ts.n_fiducial)
    
    
def calculate_acceptance_and_efficiency(truth_signals, reco_signals) :
    calculate_acceptance(truth_signals)
    calculate_efficiency(truth_signals, reco_signals)


# ------------------------------------------ #
#  Begin plotting
# ------------------------------------------ #
def make_acceptance_and_efficiency_graphs(signals, region, grid, outdir) :
    title = ''
    if grid=="SMCwslep" :
        title += '; m_{#tilde{#chi}_{1}^{#pm}} [GeV]'
        title += '; m_{#tilde{#chi}_{1}^{0}} [GeV]'
    
    m_xrange = {'min': min([float(sig.mX) for sig in signals]), 'max': max([float(sig.mX) for sig in signals])}
    m_yrange = {'min': min([float(sig.mY) for sig in signals]), 'max': max([float(sig.mY) for sig in signals])}

    histo_master = r.TH2F('h_acceptance_'+region, title,
                    50, 90, 250,
                    50, 0.0, 250)
 #   percent = 100.
 #   acceptance_scale_factor = 1.0e4
 #   acceptance_scale_label = '10^{4}'
    
    # put pen to paper
    r.gStyle.SetPaintTextFormat('.3f')
    #for s in ['acceptance', 'efficiency', 'ngen', 'xsec'] :
    for s in ['xsec'] :
        histo_master = r.TH2F('h_'+s+"_"+region, title, 50, 90, 250, 50, 0, 250)
        g = r.TGraph2D(1)
        g.SetName('g_'+s)
        g.SetMarkerStyle(r.kFullSquare)
        g.SetMarkerSize(2.0*g.GetMarkerSize())
        for sig in signals :
            x, y, z= sig.mX, sig.mY, 0.0
            if s=='acceptance' :
                z = sig.acceptance
            elif s=='efficiency' :
                z = sig.efficiency
            elif s=='ngen' :
                z = sig.n_generated
            elif s=='xsec' :
                z = sig.xsec
            if float(x) > 400 : continue
            if float(y) > 400 : continue
            if s=='acceptance' or s=='efficiency' :
                g.SetPoint(g.GetN(), float(x), float(y), float(z)*100) # storing as percentage!!
            elif s=='ngen' :
                g.SetPoint(g.GetN(), float(x), float(y), float(z) / 1000)
            elif s=='xsec' :
                g.SetPoint(g.GetN(), float(x), float(y), float(z))
        c = r.TCanvas('c_'+g.GetName(),'',800,600)
        c.cd()
        c.SetRightMargin(2.5*c.GetRightMargin())
        histo_master.Draw('axis')
        g.Draw('colz same')
        c.Update()

        z_title = ''
        if 'accept' in g.GetName() : z_title = 'Acceptance [%]'
        elif 'eff' in g.GetName()  : z_title = 'Efficiency [%]'
        elif 'ngen' in g.GetName() : z_title = 'Events generated [k]'
        elif 'xsec' in g.GetName() : z_title = 'Production Cross-Section [pb]'
        z_title_x = 282
        z_title_y = 150
        if s=='ngen' : z_title_y = 110
        elif s=='xsec' : z_title_y = 60
        z_tex = r.TLatex(z_title_x, z_title_y, z_title)
        z_tex.SetTextAngle(90)
        z_tex.Draw('same')
        
        for sig in signals :
            tex = r.TLatex(0.0, 0.0, '')
            tex.SetTextFont(42)
            tex.SetTextSize(0.6*tex.GetTextSize())
            x, y, z = sig.mX, sig.mY, 0.0
            if 'accept' in g.GetName() :
                z = sig.acceptance
            elif 'effic' in g.GetName() :
                z = sig.efficiency
            elif 'ngen' in g.GetName() :
                z = float(sig.n_generated) / 1000.
            elif 'xsec' in g.GetName() :
                z = float(sig.xsec)
            if float(x) >= 225 : continue
            if float(y) >= 225 : continue
            if 'accept' in g.GetName() or 'effic' in g.GetName() :
                tex.DrawLatex(float(x), float(y), "%.2f"%(100*float(z)))
            elif 'ngen' in g.GetName() : tex.DrawLatex(float(x), float(y), "%.0f"%(float(z)))
            elif 'xsec' in g.GetName() : tex.DrawLatex(float(x), float(y), "%.2f"%(float(z)))
        c.Update()
        xax = histo_master.GetXaxis()
        yax = histo_master.GetYaxis()
        xax.SetTitle("m_{#tilde{#chi}_{1}^{#pm}} [GeV]")
        yax.SetTitle("m_{#tilde{#chi}_{1}^{0}} [GeV]")
        minTitleSize = min(a.GetTitleSize() for a in [xax, yax])
        xax.SetTitleSize(minTitleSize)
        yax.SetTitleSize(minTitleSize)
        xax.SetTitleOffset(1.1*xax.GetTitleOffset())
        yax.SetTitleOffset(1.1*yax.GetTitleOffset())
        c.Update()

        r.gPad.RedrawAxis()
        
        # labels, etc...
        drawAtlasLabel(c, "Internal",ypos=0.92)
        topLeftLabel(c, '#sqrt{s} = 8 TeV, 20.3 fb^{-1}', ypos=0.88)
        process_y = 0.84
        if s=='ngen' : process_y = 0.87
        if s=='xsec' : process_y = 0.83
        topLeftLabel(c, get_prod_label(grid),ypos=process_y)
        #topLeftLabel(c, "#bf{%s}"%get_nice_region_name(region),ypos=0.74)
        c.Update()

        outname = region
        if 'accep' in g.GetName() : outname += '_acc'
        elif 'eff' in g.GetName() : outname += '_eff'
        elif 'ngen' in g.GetName() : outname += '_ngen'
        elif 'xsex' in g.GetName() : outname += '_xsec'
        outname += '.eps'
        c.SaveAs(outname)
        
        # move the file to the destination directory
        mv_file_to_dir(outname, str(outdir), True)


if __name__=="__main__" :
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--grid", help="Provide the signal grid (default: 'SMCwslep')")
    parser.add_argument("-r", "--region",help="Provide the region (default: 'eeSuper1a')")
    parser.add_argument("-o", "--outdir", help="Store the plots in this directory (default: plots/")
    parser.add_argument("-d", "--dbg",action="store_true")
    args = parser.parse_args()
    grid = args.grid
    region = args.region
    outdir = args.outdir
    dbg = args.dbg
    # check whether requested region is available
    if not is_valid_region(region) :
        print "Region '%s' not supported! Available regions are:"%region
        print_available_regions()
        print "Exitting"
        sys.exit()
    print "--------------------------------------"
    print " Plotting signal acceptance and eff   "
    print "- - - - - - - - - - - - - - - - - - - "
    print "  grid:      %s                       "%(grid)
    print "  region:    %s                       "%(region)
    print "  outdir:    %s                       "%(outdir)
    print "--------------------------------------\n"

    # Fill the truth signal points
    truth_signals = []
    truth_files = glob.glob(get_signal_file_directory(grid,True) + 'truthRazor_*.root')
    for file in truth_files :
        s = Signal(file, grid, dbg)
        s.get_tree()
        s.fill_mass_info()
        s.fill_xsec_br_eff()
        s.get_n_generated()
        truth_signals.append(s)
    # Fill the reconststructed signal points
    reco_signals = []
    reco_files = glob.glob(get_signal_file_directory(grid,False) + 'CENTRAL_*.root')
    for file in reco_files :
        s = Signal(file, grid, dbg)
        s.get_tree()
        s.fill_mass_info()
        reco_signals.append(s)
    # Summary of points
    print "--------------------------------------"
    print "  Signal points for grid %s"%grid
    print "\t%s truth points, %s reco points"%(str(len(truth_signals)), str(len(reco_signals)))
    print "--------------------------------------"

    # give c1c1 weight to truth samples
    # get N_{fiducial} <==> N events in SR with selection applied on truth objects
    get_n_passing_selection(truth_signals, region, True) 
    # get N_{fiducial_reco} <==> N events in SR with selection applied on reconstructed objects
    get_n_passing_selection(reco_signals, region, False)
    # calculate acceptance and efficiency
    calculate_acceptance_and_efficiency(truth_signals, reco_signals)

    # test TGuiTutils Style
    #setAtlasStyle_TGui()
    setAtlasStyle()

    
    make_acceptance_and_efficiency_graphs(truth_signals, region, grid, outdir) 
