import ROOT as r
import math
from array import array


''' -----------------------------------------------------'''
'''   Canvas Methods                                     '''
''' -----------------------------------------------------'''
def myCanvas(name, width, height, nxpads=1, nypads=1) :
    '''
    Book a TCanvas and return it
    '''
    c = r.TCanvas(name, name, 10, 10, w, h)
    c.Divide(nx,ny)
    c.cd(1)
    c.Modified()
    return c
    
''' -----------------------------------------------------'''
'''   TH1 Methods                                        '''
''' -----------------------------------------------------'''
def myTH1F(name, title, nbin, nlow, nhigh, xtitle, ytitle) :
    '''
    Book a TH1F and return it
    '''
    h = r.TH1F(name, title, nbin, nlow, nhigh)
    h.GetXaxis().SetTitle(xtitle)
    h.GetYaxis().SetTitle(ytitle)
    h.Sumw2()
    return h

def show_under_overflow(hist, option) :
    '''
    Plot the underflow or overflow bins of a TH1F
    '''
    if option=="both" or option=="under" :
        c_under = hist.GetBinContent(0)
        e_under = hist.GetBinError(0)
        e_first = hist.GetBinError(1)
        e_first_new = math.sqrt(e_first*e_first + e_under+e_under)
        hist.AddBinContent(1, c_under)
        hist.SetBinError(1, e_first_new)
        hist.SetBinContent(0,0)
        hist.SetBinError(0,0)
    if option=="both" or option=="over" :
        nbins = hist.GetNbinsX()
        c_over = hist.GetBinContent(nbins+1)
        e_over = hist.GetBinError(nbins+1)
        e_last = hist.GetBinError(nbins)
        e_last_new = math.sqrt(e_last*e_last + e_over*e_over)
        hist.AddBinContent(nbins, c_over)
        hist.SetBinError(nbins, e_last_new)
        hist.SetBinContent(nbins+1, 0)
        hist.SetBinError(nbins+1, 0)
def th1_to_tgraph(hist) :
    '''
    The provided histogram is turned into a TGraphErrors object
    '''
    if not hist : print "th1_to_tgraph error: histogram not found "
    g = r.TGraphErrors()
    for ibin in xrange(len(hist.GetNbinsX())) :
        y = hist.GetBinContent(ibin)
        ey = hist.GetBinError(ibin)
        x = hist.GetBinCenter(ibin)
        ex = hist.GetBinWidth(i)
        
        g.SetPoint(ibin)
        g.SetPointError(ibin, ex, ey)
    return g

def th1_to_tgraph_asym(hist) :
    '''
    The provided  histogram is turned into a TGraphAsymErrors object
    '''
    if not hist : print "th1_to_graph_asym error: histogram not found "
    g = r.TGraphAsymmErrors()
    for ibin in xrange(len(hist.GetNbinsX())) :
        y = hist.GetBinContent(ibin)
        ey = hist.GetBinError(ibin)
        x = hist.GetBinCenter(ibin)
        ex = hist.GetBinWidth(ibin)/2.0
        g.SetPoint(ibin-1, x, y)
        g.SetPointError(ibin-1, ex, ex, ey, ey)
    g.SetMarkerSize(0)
    g.SetFillStyle(3004)
    g.SetFillColor(r.kBlack)
    return g


''' -----------------------------------------------------'''
'''   TH2 Methods                                        '''
''' -----------------------------------------------------'''
def myTH2F(name, title, nxbin, xlow, xhigh, nybin, ylow, yhigh, xtitle, ytitle) :
    '''
    Book a TH2F and return it
    '''
    h = r.TH2F(name, title, nxbin, xlow, xhigh, nybin, ylow, yhigh)
    h.GetXaxis().SetTitle(xtitle)
    h.GetYaxis().SetTitle(ytitle)
    h.Sumw2()
    return h

''' -----------------------------------------------------'''
'''   Text and Label Methods                             '''
''' -----------------------------------------------------'''
def myText(x, y, color, text, size, angle=0.0) :
    l = r.TLatex()
    l.SetTextSize(size)
    l.SetNDC()
    l.SetTextColor(color)
    l.SetTextAngle(angle)
    l.DrawLatex(x, y, text)

def topRightLabel(pad, label, xpos=None, ypos=None, align=33) :
    pad.cd()
    tex = r.TLatex(0.0, 0.0, "")
    tex.SetTextFont(42)
    tex.SetTextSize(0.75*tex.GetTextSize())
    tex.SetNDC()
    tex.SetTextAlign(align)
    tex.DrawLatex((1.0-1.1*pad.GetRightMargin()) if not xpos else xpos,
                    (1.0-1.1*pad.GetTopMargin()) if not ypos else ypos,
                    label)
    if hasattr(pad, '_labels') : pad._labels.append(tex)
    else : pad._labels = [tex]
    return tex

def topLeftLabel(pad, label, xpos=None, ypos=None, align=13) :
    pad.cd()
    tex = r.TLatex(0.0, 0.0, '')
    tex.SetTextFont(42)
    tex.SetTextSize(0.75*tex.GetTextSize())
    tex.SetNDC()
    tex.SetTextAlign(align)
    tex.DrawLatex((0.0+1.2*pad.GetLeftMargin()) if not xpos else xpos,
                    (1.0-1.1*pad.GetTopMargin()) if not ypos else ypos,
                    label)
    if hasattr(pad, '_labels') : pad._labels.append(tex)
    else : pad._labels = [tex]
    return tex

def drawAtlasLabel(pad, descriptor, xpos=None, ypos=None) :
    ''' 
    Draw the ATLAS label.
        "descriptor" : "Internal", "Work in Progress", "Official", "Preliminary" 
    '''
    label = "#bf{#it{ATLAS}} %s"%descriptor
    return topLeftLabel(pad, label, xpos, ypos)


''' -----------------------------------------------------'''
'''   Style Methods                                      '''
''' -----------------------------------------------------'''
def set_palette(name='', ncontours=999) :
    if name == "gray" or name == "grayscale" :
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        red   = [1.00, 0.84, 0.61, 0.34, 0.00]
        green = [1.00, 0.84, 0.61, 0.34, 0.00]
        blue  = [1.00, 0.84, 0.61, 0.34, 0.00] 
    else :
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        red   = [0.00, 0.00, 0.87, 1.00, 0.51]
        green = [0.00, 0.81, 1.00, 0.20, 0.00]
        blue  = [0.51, 1.00, 0.12, 0.00, 0.00] 
    s = array.array('d', stops)
    R = array.array('d', red)
    g = array.array('d', green)
    b = array.array('d', blue)
    npoints = len(s)
    r.TColor.CreateGradientColorTable(npoints, s, R, g, b, ncontours)
    r.gStyle.SetNumberContours(ncontours)


def getAtlasStyle() :
    ''' 
    Definition of the ATLAS plotting style 
    '''
    style = r.TStyle('ATLAS', 'Atlas style')
    white = 0
    style.SetFrameBorderMode(white)
    style.SetFrameFillColor(white)  
    style.SetCanvasBorderMode(white)
    style.SetCanvasColor(white)
    style.SetPadBorderMode(white)
    style.SetPadColor(white)
    #style.SetPaperSize(20,26)
    style.SetPadTopMargin(0.05)
    style.SetPadRightMargin(0.05)
    nokidding = 0.75
    style.SetPadBottomMargin(nokidding*0.16)
    style.SetPadLeftMargin(nokidding*0.16)
    style.SetPadRightMargin(nokidding*0.10)
    style.SetTitleXOffset(nokidding*1.25)
    style.SetTitleYOffset(nokidding*1.25)
    style.SetTitleXSize(1.25*style.GetTitleSize())
    style.SetTitleYSize(1.25*style.GetTitleSize())
    font, fontSize = 42, 0.04 # helvetica, large
    style.SetTextFont(font)
    #style.SetTextSize(fontSize)
    style.SetLabelFont(font,"xyz")
    style.SetTitleFont(font,"xyz")
    style.SetPadTickX(1)
    style.SetPadTickY(1)
    style.SetOptStat(0)
    style.SetOptTitle(0)
    style.SetEndErrorSize(0)
    return style

def setAtlasStyle() :
    ''' 
    Set the ATLAS plotting style 
    '''
    aStyle = getAtlasStyle()
    r.gROOT.SetStyle("ATLAS")
    r.gROOT.ForceStyle()
 #   set_palette()
    r.gStyle.SetPalette(52)
    nElementsPalette = 40
    r.gStyle.SetPalette(nElementsPalette, array('i', [61+i for i in range(nElementsPalette)]))
    r.gStyle.SetNumberContours(999)

def setAtlasStyle_TGui() :
    '''
    Set ATLAS Style (port from SusyNtuple/TGuiUtils)
    '''
    atlasStyle = r.TStyle("ATLAS", "Atlas style")
    icol = 0
    font = 42
    tsize = 0.05
    labelsize = 0.04 # ATLAS 0.05
    markerstyle = 20
    msize = 1.2 
    hlinewidth = 2

    # Canvas settings
    atlasStyle.SetFrameBorderMode(icol)
    atlasStyle.SetFrameFillColor(icol)
    atlasStyle.SetCanvasBorderMode(icol)
    atlasStyle.SetPadBorderMode(icol)
    atlasStyle.SetPadColor(icol)
    atlasStyle.SetCanvasColor(icol)
    atlasStyle.SetStatColor(icol)

    # set the paper & margin sizes 
    atlasStyle.SetPaperSize(20,26)
    atlasStyle.SetPadTopMargin(0.15)    #0.05
    atlasStyle.SetPadRightMargin(0.15)  #0.05
    atlasStyle.SetPadBottomMargin(0.15) #0.16
    atlasStyle.SetPadLeftMargin(0.15)   #0.16

    # use large fonts
    atlasStyle.SetTextFont(font)
    atlasStyle.SetTextSize(tsize)
    atlasStyle.SetTitleFont(font,"x")
    atlasStyle.SetTitleFont(font,"y")
    atlasStyle.SetTitleFont(font,"z")
    atlasStyle.SetTitleOffset(1.4,"x") #0.9
    atlasStyle.SetTitleOffset(1.4,"y") #1.5
    atlasStyle.SetTitleOffset(1.,"z")
    atlasStyle.SetTitleSize(tsize,"x")
    atlasStyle.SetTitleSize(tsize,"y")
    atlasStyle.SetTitleSize(tsize,"z")
    atlasStyle.SetTickLength(0.02,"x")
    atlasStyle.SetTickLength(0.02,"y")
    atlasStyle.SetTickLength(0.02,"z")

    atlasStyle.SetLabelFont(font,"x")
    atlasStyle.SetLabelFont(font,"y")
    atlasStyle.SetLabelFont(font,"z")
#    atlasStyle.SetLabelOffSet(0.05,"x")
#    atlasStyle.SetLabelOffset(0.02,"y")
#    atlasStyle.SetLabelOffset(0.01,"z")
    atlasStyle.SetLabelSize(labelsize,"x")
    atlasStyle.SetLabelSize(labelsize,"y")
    atlasStyle.SetLabelSize(labelsize,"z")
    
    # palette settings
    atlasStyle.SetPalette(1)
    
    # bold lines and markers
    atlasStyle.SetMarkerStyle(markerstyle)
    atlasStyle.SetMarkerSize(msize)
    atlasStyle.SetHistLineWidth(hlinewidth)
    atlasStyle.SetLineStyleString(2,"[12 12]") # postscript dashes
    atlasStyle.SetEndErrorSize(0.) # remove error bar caps
    
    # do not display any of the standard histogram decorations
    atlasStyle.SetStatX(0.99)
    atlasStyle.SetStatY(0.99)
    atlasStyle.SetStatH(0.01)
    atlasStyle.SetStatW(0.2)
    
    atlasStyle.SetStatStyle(0)
    atlasStyle.SetStatFont(font)
    atlasStyle.SetStatFontSize(0.03)
    atlasStyle.SetOptStat("nemruo")
    atlasStyle.SetStatBorderSize(1)
    atlasStyle.SetOptTitle(0)
    atlasStyle.SetOptFit(0)

    atlasStyle.SetTitleStyle(icol)
    atlasStyle.SetTitleH(0.08)

    # put tick marks on top and RHS of plots
    atlasStyle.SetPadTickX(1)
    atlasStyle.SetPadTickY(1)
    
    
    
    
    
