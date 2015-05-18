#!/usr/bin/env python
# superplotter
from superplotter.region import *
from superplotter.signal import *
from superplotter.utils import *
from superplotter.plot_utils import *

import array 

# standard
import argparse
import glob
import sys

# ROOT
import ROOT as r
r.gROOT.SetBatch(True)
r.PyConfig.IgnoreCommandLineOptions = True

def make_isr_plots(signals, v, outdir) :
    ytitle = "entries"
    xtite = ""
    var = ""
    bins = []
    nb = 0
    nb = xlow = xhigh = 0
    if v=="lept1Pt" :
        xtitle = "p_{T}^{lead lep} [GeV]"
        var = "lept1Pt"
        nb, xlow, xhigh = 15, 10, 100
    elif v=="lept2Pt" :
        xtitle = "p_{T}^{sub-lead lep} [GeV]"
        var = "lept2Pt"
        nb, xlow, xhigh = 8, 10, 90
    elif v=="mDeltaR" :
        xtitle = "M_{#Delta}^{R} [GeV]"
        var = "mDeltaR"
        nb, xlow, xhigh = 8, 0, 80
    elif v=="jet1Pt" :
        xtitle = "p_{T}^{lead jet} [GeV]"
        var = "jet1Pt"
        nb, xlow, xhigh = 10, 20, 200
    elif v=="mll" :
        xtitle = "m_{ll} [GeV]"
        var = "mll"
        nb, xlow, xhigh = 11, 20, 240
    elif v=="dpb" :
        var='dphi_ll_vBetaT'
        xtitle = "#Delta#phi_{#beta}^{R}"
        nb, xlow, xhigh = 10, 0, 3.0
    elif v=="R2" :
        var = 'R2'
        xtitle = "R_{2}"
        nb, xlow, xhigh = 10, 0, 1.0
    elif v=="met" :
        var = 'met' 
        xtitle = "E_{T}^{miss} [GeV]"
        nb, xlow, xhigh = 15, 0, 175
    elif v=="njets" :
        var = 'nCentralLightJets'
        xtitle = "N_{jets}^{CL20}"
        nb, xlow, xhigh = 5, 0, 5
    elif v=="pTll" :
        var = "pTll"
        xtitle = "p_{T}^{ll} [GeV]"
        nb, xlow, xhigh = 12, 10, 80
       
    h_nom       = myTH1F("herwig",          "herwig",               nb, xlow, xhigh, xtitle, ytitle)
    h_isr_nom   = myTH1F("herwig+isr",      "+ isr reweight",       nb, xlow, xhigh, xtitle, ytitle)
    h_up        = myTH1F("herwig+isrUP",    "+ isr reweight +1#sigma",      nb, xlow, xhigh, xtitle, ytitle)
    h_down      = myTH1F("herwig+isrDOWN",  "+ isr reweight -1#sigma",    nb, xlow, xhigh, xtitle, ytitle)
    
    colors = {}
    colors["herwig"] = r.kBlack
    colors["herwig+isr"] = r.kGreen
    colors["herwig+isrUP"] = r.kBlue
    colors["herwig+isrDOWN"] = r.kRed
    h_nom.SetLineColor(r.kBlack)
    h_isr_nom.SetLineColor(r.kGreen)
    h_up.SetLineColor(r.kBlue)
    h_down.SetLineColor(r.kRed)
    
    canvas = r.TCanvas("can","can",768,768)
    canvas.SetLogy(True)
    if v=="dpb" :
        leg = r.TLegend(0.2, 0.69, 0.53, 0.93)
    else :
        leg = r.TLegend(0.57,0.69,0.90,0.93)
    leg.SetBorderSize(0)
    leg.SetLineColor(0)
    leg.SetLineWidth(0)
    leg.SetTextFont(42)
    leg.SetFillStyle(0)
    leg_name = "(%s,%s)"%(signals[0].mX,signals[0].mY)
    leg.SetHeader(leg_name)
    
    for h in [h_nom, h_isr_nom, h_up, h_down] :
        h.SetLineWidth(2)
        h.GetYaxis().SetTitleOffset(1.1*h.GetYaxis().GetTitleOffset())
        sel = r.TCut("(isOS==1 && lept1Pt>10000. && lept2Pt>10000. && lept1Eta<2.5 && lept2Eta<2.5)")
        weight = ""
        if h.GetName()=="herwig" :
            weight = r.TCut("eventweight/isr_weight_nom")
        elif h.GetName()=="herwig+isr" :
            weight = r.TCut("eventweight")
        elif h.GetName()=="herwig+isrUP" :
            weight = r.TCut("eventweight*syst_ISRUP")
        elif h.GetName()=="herwig+isrDOWN" :
            weight = r.TCut("eventweight*syst_ISRDOWN")
        
        cmd = ''
        if v=='dpb' or v=='R2' or v=='njets':
            cmd = var+">>"+h.GetName()
        else :
            cmd = var+"/1000>>"+h.GetName() 
        signals[0].tree.Draw(cmd, sel*weight) 
        leg.AddEntry(h,h.GetTitle(),"l")
    
    # ratio
    ratio = RatioCanvas("rcan")
    print ratio
    ratio.canvas.cd()
    ratio.upper_pad.cd()
    h_nom.Draw("hist e")
    h_isr_nom.Draw("hist same e")
    h_up.Draw("hist same e")
    h_down.Draw("hist same e")
    if v=="dpb" or v=="lept2Pt" or v=="lept1Pt" or v=="mDeltaR" or v=="mll" or v=="pTll" :
        h_nom.GetYaxis().SetRangeUser(0, 1.3*h_nom.GetMaximum())
    
    h_ratio_nom_up = divide_histograms (h_up,       h_nom,  xtitle, "#frac{weighted}{un-weighted}")
    h_ratio_nom_dn = divide_histograms (h_down,     h_nom,  "", "")
    h_ratio_nom_isr = divide_histograms(h_isr_nom,  h_nom,  "", "")
    h_nom.GetXaxis().SetLabelOffset(999)
    h_nom.GetXaxis().SetTitleOffset(999)
    h_nom.GetYaxis().SetTitleOffset(0.9*h_nom.GetYaxis().GetTitleOffset())
    yl = 0.5
    yh = 2.0
    if v=="jet1Pt" :
        yl, yh = 0.8, 2.4
    elif v=="mDeltaR" :
        yl, yh = 0.7, 2.4
    elif v=="met" :
        yl, yh = 0.7, 2.4
    elif v=="R2" :
        yl, yh = 0.7, 2.4
    elif v=="pTll" and signals[0].mY==80 :
        yl, yh = 0.7, 2.4
    h_ratio_nom_up.GetYaxis().SetRangeUser(yl,yh)
    h_ratio_nom_up.SetLineColor(r.kBlue)
    h_ratio_nom_up.SetLineWidth(2)
    h_ratio_nom_dn.GetYaxis().SetRangeUser(yl,yh)
    h_ratio_nom_dn.SetLineColor(r.kRed)
    h_ratio_nom_dn.SetLineWidth(2)
    h_ratio_nom_isr.GetYaxis().SetRangeUser(yl,yh)
    h_ratio_nom_isr.SetLineColor(r.kGreen)
    h_ratio_nom_isr.SetLineWidth(2)
    ratio.lower_pad.cd()

    h_ratio_nom_up.Draw("hist")
    h_ratio_nom_dn.Draw("hist same")
    h_ratio_nom_isr.Draw("hist same")

    ratio.upper_pad.cd()
    leg.Draw('same')
    outname = var+"_sr_"+str(signals[0].mX)+"_"+str(signals[0].mY)+".eps"
    ratio.canvas.SaveAs(outname)
    mv_file_to_dir(outname, str(outdir), True)
    
#################################        
if __name__=="__main__" :
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input dataset")
    parser.add_argument("-o", "--outdir", help="Store the plots in this directory (default: plots/")
    parser.add_argument("-v", "--var", help="Choose the var to print",default="")
    args = parser.parse_args()
    input = args.input
    outdir = args.outdir
    var = args.var
    # check whether requested region is available
    print "--------------------------------------"
    print " Plotting ISR                         "
    print "- - - - - - - - - - - - - - - - - - - "
    print "  input :    %s                       "%(input)
    print "  outdir:    %s                       "%(outdir)
    print "--------------------------------------\n"


    files = glob.glob(input + "CENTRAL*root")
    print files
    signals = []
    for file in files :
        s = Signal(file, "SMCwslep", False)
        s.get_tree()
        s.fill_mass_info()
        signals.append(s)

    setAtlasStyle()
    vars = [ 'lept1Pt', 'lept2Pt', 'mDeltaR', 'jet1Pt',
             'mll', 'dpb', 'R2', 'met', 'njets', 'pTll' ]
    if var != "" :
        make_isr_plots(signals, str(var), outdir)
    else :
        for v in vars :
            make_isr_plots(signals, str(v), outdir)
    
