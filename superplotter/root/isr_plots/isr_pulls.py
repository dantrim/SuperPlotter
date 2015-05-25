#!/usr/bin/env python
#
# A script for comparing the yields of the C1C1
# samples with and without the re-weight to MG5
# applied.
#
# daniel.joseph.antrim@cern.ch
# May 2015

# superplotter
from superplotter.signal import *
from superplotter.region import *

# ROOT
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

import os
import sys
import glob
import argparse
import math
import numpy


class Point(Signal) :
    '''
    Additional methods to store information about the
    ISR systematic uncertainties
    '''
    def __init__(self, file, grid, dbg=False) :
        Signal.__init__(self, file, grid, dbg)
        
        # nominal yield indexed by region
        self.nom_yield = {}
        # statistical error indexed by region
        self.stat_err = {}
        # ISR uncertainty +1 sigma indexed by region
        # store the up variation as var - nominal
        self.sys_err_up = {}
        # ISR uncertainty -1 sigma indexed by region
        # store the down variation as nominal - var 
        self.sys_err_dn = {}

    def sym_err(self, reg) :
        '''
        Symmetrize the ISR uncertainty
        '''
        return 0.5 * ( abs(self.sys_err_up[reg]) + abs(self.sys_err_dn[reg]))
    def total_error(self, reg) :
        '''
        Add statistical error and ISR sys in quadrature 
        and return the result (sqrt)
        '''
        sym_sys = self.sym_err(reg)
        tot_err = self.stat_err[reg] * self.stat_err[reg] + sym_sys * sym_sys
        return math.sqrt(tot_err)

def sort_by_mc1(signals) :
    '''
    Sort a list of Signal/Point objects by mX (mC1)
    in descending order
    '''
    signals.sort(key=lambda x : x.mX, reverse=True)

def draw_text(x, y, color, text, size=0.04, angle=0.0, ndc=True) :
    l = ROOT.TLatex()
    ROOT.SetOwnership(l, False)
    l.SetTextSize(size)
    if ndc : l.SetNDC()
    l.SetTextFont(62)
    l.SetTextAngle(angle)
    l.SetTextColor(color)
    l.DrawLatex(x,y,text)


def draw_line(xl, yl, xh, yh, color=ROOT.kBlack, style=2) :
    l = ROOT.TLine(xl, yl, xh, yh)
    ROOT.SetOwnership(l, False)
    l.SetLineColor(color)
    l.SetLineStyle(style)
    l.Draw("same")
    

class ISRCanvas :
    '''
    Class to hold the canvases for the pads and to size them
    '''
    def __init__(self, name) :
        self.name = name
        self.canvas = ROOT.TCanvas(name, name, 1200, 600)
        self.upper_pad = ROOT.TPad("upper","upper",0.0,0.0,1.0,1.0)
        self.lower_pad = ROOT.TPad("lower","lower",0.0,0.0,1.0,1.0)
        self.set_pad_dimensions()
    
    def set_pad_dimensions(self) :
        can = self.canvas
        up  = self.upper_pad
        dn  = self.lower_pad
        
        can.cd()
        up_height = 0.60
        dn_height = 0.40
        up.SetPad(0.0,1.0-up_height,1.0,1.0)
        dn.SetPad(0.0,0.0,1.0,dn_height)
        
        up.SetTickx(0)
        dn.SetGrid(0)
        
        up.SetFrameFillColor(0)
        up.SetFillColor(0)
        dn.SetLeftMargin(0.04)
        dn.SetRightMargin(0.01)
        dn.SetBottomMargin(0.6)
        dn.SetTopMargin(0.03)
        
        up.SetLeftMargin(0.04)
        up.SetRightMargin(0.01)
        

        up.Draw()
        dn.Draw()
        can.Update()
        
        self.canvas = can
        self.upper_pad = up
        self.lower_pad = dn


def myBook(name, nbin, xlow, xhigh, xaxis, yaxis) :
    h = ROOT.TH1F(name,name,nbin,xlow,xhigh)
    h.GetXaxis().SetTitle(xaxis)
    h.GetYaxis().SetTitle(yaxis)
    h.Sumw2()
    return h

def myBook2d(name, nxbin, xlow, xhigh, nybin, ylow, yhigh) :
    h = ROOT.TH2F(name, name, nxbin, xlow, xhigh, nybin, ylow, yhigh)
    return h

def get_nom_yields(signals, srs, c1c1=False) :
    '''
    Get the signal region yields for each point in "signals"
    
    If c1c1=True, uses the eventweight that contains the 
    isr reweight.
    '''
    for sr in srs :
        if(dbg) : print "\n" # because i said so
        for s in signals :
            tot_integral = 0.0
            tot_stat = 0.0
            for reg in regions.keys() :
                if sr in reg :
                    selection = regions[reg]
                    weight = ""
                    if c1c1 : weight = "eventweight"
                    elif not c1c1 : weight = "eventweight / isr_weight_nom"
                    h = myBook("hist", 4, -1, 3, "isMC", "entries")
                    h.Reset("ICE")
                    cmd = "isMC>>"+str(h.GetName())
                    cut = "(%s) * %s"%(selection, weight)
                    s.tree.Draw(cmd, cut)
                    
                    integral = 0.0
                    error = ROOT.Double(0.0)
                    integral = h.IntegralAndError(0,-1,error)
                    tot_integral += integral
                    tot_stat += error * error
                    h.Delete()
            tot_stat = math.sqrt(tot_stat)
            s.nom_yield[sr] = tot_integral
            s.stat_err[sr] = tot_stat
            if(dbg and c1c1) : print "%s    (%s,%s) (weighted) %.2f +/- %.2f"%(sr, s.mX, s.mY, s.nom_yield[sr], s.stat_err[sr])
            if(dbg and not c1c1) : print "%s    (%s,%s) (unweighted) %.2f +/- %.2f"%(sr, s.mX, s.mY, s.nom_yield[sr], s.stat_err[sr])
            
                    
def get_isr_error(signals, srs, up_or_down="") :
    '''
    Get the variation w.r.t. to nominal for the ISR
    systematic
    '''
    for sr in srs :
        if(dbg) : print "\n" # because i said so
        for s in signals :
            tot_integral = 0.0
            tot_sys = 0.0
            for reg in regions.keys() :
                if sr in reg :
                    selection = regions[reg]
                    weight = "eventweight" # isr combined eventweight 
                    if up_or_down == "up" : weight += " * syst_ISRUP"
                    elif up_or_down == "down" : weight += " * syst_ISRDOWN"
                    h = myBook("hist", 4, -1, 3, "isMC", "entries")
                    h.Reset("ICE")
                    cmd = "isMC>>"+str(h.GetName())
                    cut = "(%s) * %s"%(selection, weight)
                    s.tree.Draw(cmd, cut)
                    
                    integral = 0.0
                    error = ROOT.Double(0.0)
                    integral = h.IntegralAndError(0,-1,error)
                    
                    tot_integral += integral
                    
                    h.Delete()
            if up_or_down == "up" :
                s.sys_err_up[sr] = float(tot_integral) - float(s.nom_yield[sr])
            elif up_or_down == "down" :
                # store the values as positive-valued
                # remember this for later!
                s.sys_err_dn[sr] = float(s.nom_yield[sr]) - float(tot_integral)

def make_isr_pullplots(unw, isr, srs) :
    thisr="Super1a"

    isrcan = ISRCanvas("isrcan")
    isrcan.canvas.cd()
    
    # plot the yields in the lower pad
    isrcan.lower_pad.cd()
    isrcan.lower_pad.SetGrid(1,1)
    
    h_yld = ROOT.TH2F("h_yld", "", len(unw), 0, len(unw), len(srs), 0, len(srs))
    h_yld.GetYaxis().SetNdivisions(2)
    for i, s in enumerate(unw) :
        h_yld.GetXaxis().SetBinLabel(i+1, "(%.1f, %.1f)"%(s.mX,s.mY))
    h_yld.GetYaxis().SetBinLabel(1, "")
    h_yld.GetYaxis().SetBinLabel(2, "")

    h_yld.GetXaxis().LabelsOption("v")
    h_yld.GetXaxis().SetLabelFont(62)
    h_yld.GetXaxis().SetLabelOffset(5 * h_yld.GetXaxis().GetLabelOffset())
    h_yld.GetXaxis().SetLabelSize(3.8 * h_yld.GetXaxis().GetLabelSize())
    
    width = h_yld.GetXaxis().GetBinWidth(1)
    h_yld.Draw()
    isrcan.canvas.Update() 
    
    draw_text(0.016,0.26,ROOT.kBlack,"unweighted",angle=75,size=0.08)
    draw_text(0.016,0.49,ROOT.kBlack,"re-weighted",angle=75,size=0.08)
    isrcan.canvas.Update()

    for i, s in enumerate(unw) :
        t_u = " %.2f"%s.nom_yield[thisr]
        t_l = "#pm%.2f"%s.stat_err[thisr]
        print float(i+0.02)/20.0
        draw_text(i+0.1,0.58,text=t_u, color=ROOT.kBlack,ndc=False,size=0.08)
        draw_text(i+0.1,0.14,text=t_l, color=ROOT.kBlack,ndc=False,size=0.08)
        isrcan.canvas.Update()
        
    for i, s in enumerate(isr) :
        t_u = " %.2f"%s.nom_yield[thisr]
        t_l = "#pm%.2f"%s.total_error(thisr)
        print float(i+0.02)/20.0
        draw_text(i+0.1,1.58,text=t_u, color=ROOT.kBlack,ndc=False,size=0.08)
        draw_text(i+0.1,1.14,text=t_l, color=ROOT.kBlack,ndc=False,size=0.08)
        isrcan.canvas.Update()

    # plot the pull plot on upper pad
    isrcan.upper_pad.cd()
    h_pull = ROOT.TH1F("h_pull", "", 20, 0, 20)
    h_pull.Draw("axis")
    h_pull.GetXaxis().SetLabelOffset(999)
    g = ROOT.TGraphAsymmErrors(0)
    g.SetTitle("")
    ROOT.gStyle.SetHatchesSpacing(0.9)
    ROOT.gStyle.SetHatchesLineWidth(1)

    ratios = []
    for i, s in enumerate(unw) :
        unw_yld = unw[i].nom_yield[thisr]
        isr_yld = isr[i].nom_yield[thisr]
        ratio = isr_yld / unw_yld
        ratios.append(ratio)

        er_unw = unw[i].stat_err[thisr]
        er_isr = isr[i].total_error(thisr)
        ratio_err = ( er_unw / unw_yld ) ** 2 + ( er_isr / isr_yld ) ** 2
        ratio_err = math.sqrt(ratio_err)
        ratio_err *= ratio
       
        print "(%.1f,%.1f) ratio err: %.2f"%(s.mX,s.mY, ratio_err)
   #     if g.GetN()>20 : continue 
        g.SetPoint(g.GetN(), i+0.5, ratio)
        g.    SetPointEYhigh(i, ratio_err)
        g.     SetPointEYlow(i, ratio_err)
        g.    SetPointEXhigh(i, width/2.)
        g.     SetPointEXlow(i, width/2.)

 
    g.GetXaxis().SetRangeUser(0,20)
    g.GetXaxis().SetLabelOffset(999)
    g.GetYaxis().SetLabelSize(2.0 * g.GetYaxis().GetLabelSize())
    g.GetYaxis().SetLabelFont(62)

    g.SetFillColor(ROOT.kGray+3)
    g.SetFillStyle(3354)
    g.Draw("same a2")
    g.Draw("same p")

    draw_text(0.9,0.83,ROOT.kBlack,thisr,ndc=True,size=0.08)   
    isrcan.canvas.Update()
    average_ratio = numpy.mean(ratios)
    draw_line(0.0, average_ratio, len(unw), average_ratio, color=ROOT.kRed)
    print average_ratio


    ROOT.gPad.RedrawAxis()
    isrcan.canvas.Update()
    

    

    isrcan.canvas.SaveAs("test.eps")





###########################################
if __name__=="__main__" :
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--printout", action="store_true", default=False, help="Set whether to just print out the table (and not save it to file)")
    parser.add_argument("-d", "--dbg", action="store_true", default=False, help="Set the verbose level true")
    args = parser.parse_args()
    global dbg
    printout = args.printout
    dbg = args.dbg

    # grab the files
    indir = '/gdata/atlas/dantrim/SusyAna/histoAna/TAnaOutput/SMCwslep/S0_May13/Raw/'
    files = glob.glob(indir + "CENTRAL*root")
    
    # container for signal points without isr reweighting
    unw_signals = []
    # container for signal points with isr reweighting
    isr_signals = []
    for file in files :
        s = Point(file, "SMCwslep", dbg)
        s.get_tree()
        s.fill_mass_info()
        if s.mX > 200 : continue  # compare points in low mass region only
        unw_signals.append(s)
        
        r = Point(file, "SMCwslep", dbg)
        r.get_tree()
        r.fill_mass_info()
        if r.mX > 200 : continue  # compare points in low mass region only
        isr_signals.append(r)
    
    if len(unw_signals) != len(isr_signals) :
        print "WARNING    Unequal number of 'unweighted' signals and c1c1 re-weighted signals! Exitting."
        sys.exit()
    print " >>> %s unweighted signal points and %s c1c1 weighted signal points loaded"%(len(unw_signals), len(isr_signals))
       

    # sort the signal points by mC1
    sort_by_mc1(unw_signals)
    sort_by_mc1(isr_signals)

    # regions 
    srs = [ 'Super1a', 'Super1c' ] 

    # get nominal yields and stat errors
    get_nom_yields(unw_signals, srs, c1c1=False)
    get_nom_yields(isr_signals, srs, c1c1=True)

    # get the up/down variations w.r.t. to the ISR uncertainty
    # apply only to the isr weighted signals!
    get_isr_error(isr_signals, srs, "up")
    get_isr_error(isr_signals, srs, "down")

    if(dbg) :
        for reg in srs :
            print "\n"
            for s in isr_signals :
                sym_sys = 0.5*(abs(s.sys_err_up[reg])+abs(s.sys_err_dn[reg]))
                per_sys = 100. * sym_sys / s.nom_yield[reg]
                print "%s   (%s,%s): %.2f +/- %.2f +/- %.2f (+%.2f, -%.2f) (sys: %.2f percent)"%(reg, s.mX, s.mY, s.nom_yield[reg], s.stat_err[reg], sym_sys,s.sys_err_up[reg], s.sys_err_dn[reg], per_sys)

    # now we have all of the information to make the plots
    make_isr_pullplots(unw_signals, isr_signals, srs)
