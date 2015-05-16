import ROOT as r
import math
from array import array

r.TH1F.__init__._creates = False
r.TH2F.__init__._creates = False
r.TCanvas.__init__._creates = False
r.TPad.__init__._creates = False
r.TLine.__init__._creates = False



''' -----------------------------------------------------'''
'''   Canvas Methods                                     '''
''' -----------------------------------------------------'''
class RatioCanvas :
    '''
    Container class for a canvas with two pads divided 
    to make ratio plots
    '''
    def __init__(self, name) :
        self.canvas = r.TCanvas(name, name, 768, 768)
        self.upper_pad = r.TPad("upper","upper", 0.0, 0.0, 1.0, 1.0)
        self.lower_pad = r.TPad("lower","lower", 0.0, 0.0, 1.0, 1.0)
        self.set_pad_dimensions()

    def set_pad_dimensions(self) :
        can = self.canvas
        up  = self.upper_pad
        dn  = self.lower_pad
        
        can.cd()
        up_height = 0.75
        dn_height = 0.31
        up.SetPad(0.0, 1.0-up_height, 1.0, 1.0)
        dn.SetPad(0.0, 0.0, 1.0, dn_height)
        
        up.SetTickx(0)
        dn.SetGrid(1)
       
        up.SetFrameFillColor(0)
        up.SetFillColor(0)
        up.SetLeftMargin(0.1)
        up.SetRightMargin(0.075)
    
        dn.SetFrameFillColor(0)
        dn.SetFillColor(0)
        dn.SetLeftMargin(0.1)
        dn.SetRightMargin(0.075)
        dn.SetBottomMargin(0.4)
        dn.SetTopMargin(0.05) 

        up.Draw()
        dn.Draw()
        can.Update()
        
        self.canvas = can
        self.upper_pad = up
        self.lower_pad = dn


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

def remove_x_title(h) :
    h.GetXaxis().SetTitleOffset(999)
def remove_y_title(h) :
    h.GetYaxis().SetTitleOffset(999)

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

def divide_histograms(h1, h2, xtitle, ytitle) :
    '''
    Provide two histograms and divide h1/h2.
    Converts final result into tgraph.
    '''
    nbins = h1.GetNbinsX()
    xlow = h1.GetBinCenter(1)
    xhigh = h1.GetBinCenter(nbins+1)
    h3 = h1.Clone("ratio")
    h3.GetYaxis().SetTitle(ytitle)
    h3.GetXaxis().SetTitle(xtitle)

    h3.GetYaxis().SetTitleOffset(0.45*h3.GetYaxis().GetTitleOffset())
    h3.GetYaxis().SetLabelSize(2*h3.GetYaxis().GetLabelSize())
    h3.GetYaxis().SetTitleFont(42)
    h3.GetYaxis().SetTitleSize(0.09)

    h3.GetXaxis().SetTitleOffset(1.75*h3.GetYaxis().GetTitleOffset())
    h3.GetXaxis().SetLabelSize(3*h3.GetXaxis().GetLabelSize())
    h3.GetXaxis().SetTitleSize(0.15)
    h3.GetXaxis().SetTitleFont(42)
    #h3 = myTH1F("ratio", "ratio", nbins, xlow, xhigh, xtitle, ytitle)
    
    for i in range(1, nbins+1) :
        c1 = float(h1.GetBinContent(i))
        c2 = float(h2.GetBinContent(i))
        if c2 == 0 : break
        c3 = c1 / c2
        h3.SetBinContent(i, c3)
    
    return h3
        
    


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
'''   TLine Methods                                      '''
''' -----------------------------------------------------'''
def draw_line(xl, yl, xh, yh, color=r.kBlack) :
    l = r.TLine(xl, yl, xh, yh)
    l.SetLineColor(color)
    l.Draw('same')

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
    
    
    
    
    
