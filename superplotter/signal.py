import ROOT as r
import glob


def get_signal_file_directory(grid, truth=False) :
    if grid=='SMCwslep' :
        if not truth :
            return '/gdata/atlas/dantrim/SusyAna/histoAna/TAnaOutput/SMCwslep/S0_Dec2/Raw/'
        elif truth :
            return '/gdata/atlas/dantrim/SusyAna/histoAna/TAnaOutput/SMCwslep/Truth_Apr27/Raw/'
    else : print "get_signal_file_directory error: requested grid not supported"

def get_prod_label(grid) :
    if grid=='SMCwslep' :
        return "#tilde{#chi}^{#pm}_{1}#tilde{#chi}^{#mp}_{1} #rightarrow 2 #times #tilde{l}#nu (l#tilde{#nu}) #rightarrow 2 #times #tilde{#chi}_{1}^{0}l#nu"        
    else : print "get_prod_label error: requested grid not supported"

class Signal :
    def __init__(self, file, grid, dbg=False) :
        self.dbg = dbg
        self.file = file
        self.grid = grid
        self.dsid = str(self.dsid_from_file(file))
        self.tree = None
        # info about masses
        self.mX = 0.0
        self.mY = 0.0
        
        # info about signal MC prod 
        self.n_generated = 0.0
        self.production_xsec = 0.0
        self.filter_efficiency = 0.0
        self.branching_ratio = 0.0

        # info for acceptance and efficiency calculations
        self.n_fiducial = 0.0
        self.n_fiducial_reco = 0.0
        self.acceptance = 0.0
        self.efficiency = 0.0

    def __eq__(self, other) :
        ''' 
        Equality method to compare two signal points to test if 
        they are the same
        '''
        return (self.mX==other.mX) and (self.mY==other.mY)

    # method to grab the dsid from the input file
    def dsid_from_file(self, file) :
        dsid = ''
        if 'truthRazor' in file :
            dsid = file[file.find('truthRazor_')+11 : file.find('.root')]
        elif 'CENTRAL' in file :
            dsid = file[file.find('CENTRAL_')+8 : self.file.find('.root')]
        return dsid
    # method to get the tree from the file
    def get_tree(self) :
        tree_name = ''
        if 'truthRazor' in self.file :
            tree_name = 'truthNt'
        elif 'CENTRAL' in self.file :
            tree_name = 'id_' + str(self.dsid)
        infile = r.TFile.Open(self.file)
        chain = r.TChain(tree_name)
        chain.Add(self.file)
        self.tree = chain
    # based on the input grid, get the masses for the dsid
    def fill_mass_info(self) :
        if self.grid=='SMCwslep' :
            txtfile='/gdata/atlas/dantrim/SusyAna/Super/SusyXSReader/data/modeC_lightslep_MC1eqMN2_DiagonalMatrix.txt'
            lines = open(txtfile).readlines()
            fields = lines[0].split()
            dsIdx = fields.index('DS')
            mc1Idx = fields.index('MC1,MN2[GeV]')
            mn1Idx = fields.index('MN1[GeV]')
            for line in lines[1:]:
                line = line.strip()
                if not line : continue
                fields = line.split()
                if fields[0]!=self.dsid : continue
                self.mX = float(fields[mc1Idx])
                self.mY = float(fields[mn1Idx])

                if self.dbg : print "Signal %s found at (%s,%s)"%(self.dsid, self.mX, self.mY)
        else : print "fill_mass_info error: requested grid not supported"
    # based on the input grid, get the xsec, BR, and filter efficiency
    def fill_xsec_br_eff(self) :
        if self.grid=='SMCwslep' :
            txtfile='/gdata/atlas/dantrim/SusyAna/Super/SUSYTools/data/mc12_8TeV/Herwigpp_UEEE3_CTEQ6L1_simplifiedModel_wC.txt'
            dsid = self.dsid
            lines = open(txtfile).readlines()
            for line in lines[5:]:
                line = line.strip()
                if not line : continue
                fields = line.split()
                if fields[0]!=self.dsid : continue
                self.xsec = float(fields[2])
                self.branching_ratio = float(fields[3])
                self.filter_efficiency = float(fields[4])
                if self.dbg : print "   xsec: %s br: %s eff: %s"%(self.xsec, self.branching_ratio, self.filter_efficiency)

        else : print "fill_xsec_br_eff error: requested grid not supported"
    # get the number of events generated at truth level MC
    def get_n_generated(self) :
        if self.grid=='SMCwslep' :
            file='info/SMCwslep_modelNgen.txt'
            lines=open(file).readlines()
            fields=lines[0].split()
            for line in lines :
                line = line.strip()
                if not line : continue
                fields = line.split()
                if fields[0]!=self.dsid : continue
                self.n_generated = fields[1]
                
                if self.dbg : print "   n_generated: %s"%self.n_generated
        else : print "get_n_generated error: requested grid not supported"

