#!/usr/bin/env python

#
# Script to make a plot showing the total systematic
# uncertainty per signal point in the 2L Super-Razor
# analysis.
#
# daniel.joseph.antrim@cern.ch
# June 2015
#

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

class Point() :
    '''
    Methods to move around the numbers associated
    with each signal point
    '''
    def __init__(self, mc1, mn1) :
        
        self.mX = mc1
        self.mY = mn1

        self.sys = 0.0
        

def fill_signal_points(file) :
    '''
    Format :
            MC1[GeV] MN1[GeV] SYS
            mX mY X.XX
    '''
    out_points = []
    lines = open(file).readlines()
    for line in lines[1:] : # first line in header
        line = line.strip()
        if not line : continue
        fields = line.split()
        mx = float(fields[0])
        my = float(fields[1])
        this_point = Point(mx, my) 
        this_point.sys = float(fields[2])
        if dbg :
            print "fill_signal_points    Point at (%.1f,%.1f) : %.2f"%(mx,my,this_point.sys)
        out_points.append(this_point)
    return out_points

def get_region_name(region) :
    outname = ""
    if   "EE" in region : outname += "ee"
    elif "MM" in region : outname += "mm"
    elif "EM" in region : outname += "em"
    elif "SF" in region : outname += "sf"

    if   "Super1a" in region : outname += "SR2l-1a"
    elif "Super1b" in region : outname += "SR2l-1b"
    elif "Super1c" in region : outname += "SR2l-1c"

    return outname
    

def make_sig_sys_plots(points) :
    histo_master = r.TH2F("h_sigsys_"+region, "; m_{#tilde{#chi}_{1}^{#pm}} [GeV]; m_{#tilde{#chi}_{1}^{0}} [GeV]",
                            50, 90, 250,
                            50, 0,  250)
    r.gStyle.SetPaintTextFormat('.3f')
    g = r.TGraph2D(1)
    g.SetName('g_'+region)
    g.SetMarkerStyle(r.kFullSquare)
    g.SetMarkerSize(2.0 * g.GetMarkerSize())
    #g.SetMaximum(100)
    for p in points :
        x, y, z = p.mX, p.mY, p.sys
        g.SetPoint(g.GetN(), x, y, z * 100.) # plot percent uncertainty
        
    c = r.TCanvas('c_'+g.GetName(), '', 800, 600)
    c.cd()
    c.SetRightMargin(2.5 * c.GetRightMargin())
    histo_master.Draw("axis")
    g.Draw("colz same")
    g.SetMaximum(100)
    g.Draw("colz same")
    c.Update()

    z_title = "Systematic Uncertainty [%]"
    z_tex = r.TLatex(282, 77, z_title)
    z_tex.SetTextAngle(90)
    z_tex.Draw("same")
    
    for p in points :
        tex = r.TLatex(0.0, 0.0, '')
        tex.SetTextFont(42)
        tex.SetTextSize(0.6 * tex.GetTextSize())
        x, y = p.mX, p.mY
        if x > 245 : continue
        z = "%.1f"%(p.sys * 100)
        tex.DrawLatex(x, y, z)
    c.Update()
    xax = histo_master.GetXaxis()
    yax = histo_master.GetYaxis()
    minTitleSize = min(a.GetTitleSize() for a in [xax, yax])
    xax.SetTitleSize(minTitleSize)
    yax.SetTitleSize(minTitleSize)
    xax.SetTitleOffset(1.1*xax.GetTitleOffset())
    yax.SetTitleOffset(1.1*yax.GetTitleOffset())
    c.Update()
    
    r.gPad.RedrawAxis()
    
    # labels, etc...
    drawAtlasLabel(c, "Internal", ypos=0.92)
    topLeftLabel(c, "#sqrt{s} = 8 TeV, 20.3 fb^{-1}", ypos=0.88)
    topLeftLabel(c, get_prod_label("SMCwslep"), ypos=0.84)
    topLeftLabel(c, "#bf{%s}"%get_region_name(region), ypos=0.74)
    c.Update()

    outname = region
    outname += "_sigUncert"
    outname += ".eps"
    c.SaveAs(outname)

    # move the file to the destination directory
    mv_file_to_dir(outname, outDir, True)

if __name__=="__main__" :
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--region", help="Provide the region (default: 'Super1a_EE')", default="Super1a_EE")
    parser.add_argument("-o", "--outDir", help="Provide the output directory to dump the plots (default: 'sigsys_plots')", default="sigsys_plots")
    parser.add_argument("-d", "--dbg", help="Set debug level true", action="store_true")
    args = parser.parse_args()
    global region, outDir, dbg
    region = args.region
    outDir = args.outDir
    dbg = args.dbg

    # directory where files holding sys uncertainties are
    sysDir = "./info/sig_sys_uncertainty/"
    file = sysDir + "sys_uncert_" + region + ".txt"
    if not os.path.isfile(file) :
        print "ERROR: File (%s) for the systematic uncertainty for the requested region does not exist! Exitting."%(file)
        sys.exit()

    print "-----------------------------------"
    print " Plotting systematic uncertainty   "
    print " for region                        "
    print "         > %s                      "%region
    print "-----------------------------------"

    # load the file and the signal points along with it
    sigpoints = fill_signal_points(file)

    # style it up boy-eee
    setAtlasStyle()

    # now draw the plot
    make_sig_sys_plots(sigpoints)
   




