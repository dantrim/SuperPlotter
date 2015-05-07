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
    if v=="lept1Pt" :
        xtitle = "p_{T}^{lead} [GeV]"
        var = "lept1Pt"
        bins = [10,20,30,40,50,60,70,80,90,100,110,120,130]
    elif v=="lept2Pt" :
        xtitle = "p_{T}^{sub-lead} [GeV]"
        var = "lept2Pt"
        bins = [10,20,30,40,50,60,70,80,90]
    elif v=="mDeltaR" :
        xtitle = "M_{#Delta}^{R} [GeV]"
        var = "mDeltaR"
        bins = [0,10,20,30,40,60,95,120]
    elif v=="jet1Pt" :
        xtitle = "p_{T}^{lead-jet} [GeV]"
        var = "jet1Pt"
        bins = [20,60,100,140,180,220,260,300,340,380]
    elif v=="mll" :
        xtitle = "m_{ll} [GeV]"
        var = "mll"
        bins = [20,40,60,80,100,120,160,200,240]
    elif v=="dpb" :
        var='dphi_ll_vBetaT'
        xtitle = "#Delta#phi_{#beta}^{R}"
        bins = [0,0.3,0.6,0.9,1.2,1.5,1.8,2.1,2.4,2.7,3.0]
    elif v=="R2" :
        var = 'R2'
        xtitle = "R_{2}"
        bins = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
    elif v=="met" :
        var = 'met' 
        xtitle = "E_{T}^{miss} [GeV]"
        bins = [0,40,80,120,160,200,240,290,350,475]
    elif v=="njets" :
        var = 'nCentralLightJets'
        xtitle = "N_{jets}^{CL20}"
        bins = [0,1,2,3,4,5,6,7,8]
    elif v=="pTll" :
        var = "pTll"
        xtitle = "p_{T}^{ll} [GeV]"
        bins = [10,20,30,40,50,60,70,80]
        
    x = array.array('d',bins)
    h_nom      = r.TH1F("herwig", "herwig;%s;%s" %(xtitle,ytitle),len(bins)-1,x)
    h_isr_nom  = r.TH1F("herwig+isr", "herwig+isr;%s;%s" %(xtitle,ytitle),len(bins)-1,x)
    h_up       = r.TH1F("herwig+isrUP",  "up;%s;%s"  %(xtitle,ytitle),len(bins)-1,x)
    h_down     = r.TH1F("herwig+isrDOWN","down;%s;%s"%(xtitle,ytitle),len(bins)-1,x)
    
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
     #   sel = "1"
        sel = r.TCut("1")
        weight = ""
        if h.GetName()=="herwig" :
         #   weight = "eventweight/isr_weight_nom"
            weight = r.TCut("eventweight/isr_weight_nom")
        elif h.GetName()=="herwig+isr" :
           # weight = "eventweight"
            weight = r.TCut("eventweight")
        elif h.GetName()=="herwig+isrUP" :
           # weight = "eventweight*syst_ISRUP"
            weight = r.TCut("eventweight*syst_ISRUP")
        elif h.GetName()=="herwig+isrDOWN" :
           # weight = "eventweight*syst_ISRDOWN"
            weight = r.TCut("eventweight*syst_ISRDOWN")
        
        cmd = ''
        if v=='dpb' or v=='R2' or v=='njets':
            cmd = var+">>"+h.GetName()
        else :
            cmd = var+"/1000>>"+h.GetName() 
        signals[0].tree.Draw(cmd, sel*weight) 
        leg.AddEntry(h,h.GetName(),"l")
    canvas.cd()
    max = 4000
    miny = 0.1
    h_nom.GetYaxis().SetRangeUser(miny,1.3*max)
    h_isr_nom.GetYaxis().SetRangeUser(miny,1.3*max)
    h_up.GetYaxis().SetRangeUser(miny,1.3*max)
    h_down.GetYaxis().SetRangeUser(miny,1.3*max)
    h_nom.Draw('hist e')
    x = h_nom.Integral()
    m = h_nom.GetMean()
    h_isr_nom.Draw('hist e same')
    h_up.Draw('hist e same')
    h_down.Draw('hist e same')
    leg.Draw('same')
    outname = var+"_sr_"+str(signals[0].mX)+"_"+str(signals[0].mY)+".eps"
    canvas.SaveAs(outname)
    
    mv_file_to_dir(outname, str(outdir), True)
    
        

if __name__=="__main__" :
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input dataset")
    parser.add_argument("-o", "--outdir", help="Store the plots in this directory (default: plots/")
    parser.add_argument("-v", "--var", help="Choose the var to print")
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
    for v in vars :
        make_isr_plots(signals, str(v), outdir)
    
