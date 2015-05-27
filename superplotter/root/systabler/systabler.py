#!/usr/bin/env python
#
####################################
# Script for mkaing a summary table
# for the systematics in a given 
# region. Looks through the output
# from SysTable.py from HistFitter
#
# daniel.joseph.antrim@cern.ch
# May 26
#
####################################
#

import os
import sys
import glob
import argparse
import math

############################################
# These are the systematic groupings
# { group : name-that-appears-in-tables }

systematics_by_group = {}
systematics_by_group['Jet'] = ['JES', 'JER']
systematics_by_group['Lepton'] = [ 'EESZ', 'EER', 'EESMAT', 'ESF', 'MEFF', 'EESLOW', 'TES', 'EESPS', 'MS', 'MID', 'Electron trigger efficiency', 'Muon trigger efficiency' ]
systematics_by_group['b-tagging'] = [ 'BJET', 'BMISTAG', 'CJET' ]
systematics_by_group['MET soft-term'] = [ 'RESOST', 'SCALEST' ]
systematics_by_group['Non-prompt leptons'] = [ 'Fake estimate combined' ]
systematics_by_group['Modelling-Top'] = [ 'Top theory/generator', 'Top normalization' ]
systematics_by_group['Modelling-WW'] = [ 'WW theory/generator', 'WW normalization' ]
systematics_by_group['Modelling-ZV'] = [ 'ZV theory/generator', 'ZV normalization' ]
systematics_by_group['Luminosity'] = [ 'Lumi' ]

############################################

class Region :
    '''
    Keep track of which regions to gather
    '''
    def __init__(self, region) :
        self.regions = []
        if region=="Super1a" :
            self.regions = [ "sfSuper1a", "emSuper1a" ]
        elif region=="Super1c" :
            self.regions = [ "sfSuper1c", "emSuper1c" ]
        else :
            print "Region initialization error: requested region not supported. Exitting."
            sys.exit()
        
        # container to hold the systematic groups 
        # for this region
        self.groups = []

        # total background expectation
        self.total_bkg_exp = {}
    
        # total statistical uncertainty for region
        self.total_stat_err = {}

        # total systematic uncertainty for region
        self.total_sys_err = {}
        
        # container to hold the table files
        self.table_files = []

    def collect_systables(self, texdir) :
        for sr in self.regions :
            self.table_files += glob.glob(texdir + "*%s*.tex"%sr)
        for table in self.table_files :
            print "collect_systables     table at %s"%table
        
            

class Group :
    ''' Class to hold systematic groups
    and the associated systematics
    '''
    def __init__(self, groupname) :
        
        # group name for the contained sytematics
        # e.g. "lepton"
        self.groupname = groupname

        # container for the systematics
        # within this group
        self.systematics = []

        # combined systematic value for this group
        # (systematics[0] + systematics[1] + ...)
        self.combined = {}

class Systematic :
    '''
    Class to hold the systemiatic values
    for a specifc systematic
    '''
    def __init__(self, sysname) :
        
        # sys name for this systematic
        # e.g. EESZ
        self.sysname = sysname
        
        # value of the systematic variation (w.r.t. 
        # the region yield)
        # --> Stored a dict { sub-region : variation }
        # --> e.g. requested region==Super1a
        #          sub-region == sfSuper1a
        self.variation = {}



# -------------------------------------------
def get_table(reg, region_) :
    tables = region_.table_files
    for tab in tables :
        if reg in tab :
            return tab

def passline(line) :
    passes = True
    if "&" not in line : passes = False  # lines with sys numbers must have & since it is a latex table!
    if line.startswith("%") : passes = False # ignore any column entries for latex-commented out lines
    if "(MC)" in line : passes = False
    return passes

def clean_sys_entry(entry) :
    '''
    Grab the systematic variation (in # of events) from this line entry
    
    Example line:
    Top theory/generator uncertainty         & $\pm 19.03\ [25.2\%] $          & $\pm 0.00\ [0.00\%] $          & $\pm 0.00\ [0.00\%] $       \\
    '''
    entry = entry[entry.find('pm')+3 : entry.find('pm')+7]
    return entry


def get_systematic(file, sys) :
    '''
    Given the SysTable.tex file and the specific systematic
    collect the systematic variation. Add together the 
    variations for each background process (i.e. treat them
    as correlated).
    '''
    lines = open(file).readlines()
    for line in lines :
        if not passline(line) : continue 
        line = line.strip()
        fields = line.split("&")
        if sys.sysname in fields[0] :
            # the line we are at in the table is the line for the 
            # systematic we are after. Now add together each 
            # background process.
            var = 0.0
            for process in fields[1:] : # each bkg process is a subsequent column
                var += float(clean_sys_entry(process))
            if(dbg) : print "%s: %s"%(sys.sysname, var)
            return var

def fill_systematics(region_) :
    # collect numbers for a single region at a time
    for reg in region_.regions :
        table_file = get_table(reg, region_)
        # collect numbers for a single group at a time
        for group in region_.groups :
            # collect the numbers for each systematic within this group
            for sys in group.systematics :
                sys.variation[reg] = get_systematic(table_file, sys)


def get_total_exp_mc(file) :
    '''
    Collect the total background expectation from a 
    given input SysTable.tex file (corresponds to the
    total background expectation of the signal region
    for which SysTable is made).
    '''
    lines = open(file).readlines()
    for line in lines :
        if "Total background expectation" in line :
            line = line.strip()
            fields = line.split("&")
            total_bkg = 0.0
            for col in fields[1:] :
                col = col.replace("$", "")
                col = col.replace("\\\\","")
                total_bkg += float(col)
            return total_bkg

def get_total_stat_err(file) :
    '''
    Collect the total statistical uncertainty on the
    background esimate from a given input SysTable.tex file
    (corresponds to the total statistical uncertainty
    on the signal region exp. yield for which the SysTable is made).
    
    Add in quadrature the "mcstat" values for each background
    process.
    '''
    lines = open(file).readlines()
    total_stat = 0.0
    for line in lines :
        if not passline(line) : continue
        if 'mcstat' not in line : continue
        line = line.strip()
        fields = line.split('&')
        for entry in fields[1:] :
            entry = clean_sys_entry(entry)
            total_stat += float(entry) * float(entry) # each column <==> one bkg process and mcstat are split between bkg processes
    total_stat = math.sqrt(total_stat)
    return total_stat

def get_total_sys_err(file) :
    '''
    Collect the total systematic uncertainty on the background
    estimate from a given input SysTable.tex file
    (corresponds to the total systematic uncertainty on the
    signal region exp. yield for which the SysTable is made).

    Add the Total background systematic values for each process
    in quadature and divide by total mc exp yield.
    '''
    lines = open(file).readlines()
    total_sys = 0.0
    for line in lines :
        if "Total background systematic" in line :
            line = line.strip()
            fields = line.split("&")
            for col in fields[1:] :
                col = col.replace("$","")
                col = col.replace("\\\\", "")
                total_sys += float(clean_sys_entry(col)) * float(clean_sys_entry(col))
    return math.sqrt(total_sys) 
        
        

def collect_region_totals(region_) :
    # collect numbers for a single region at a time
    for reg in region_.regions :
        table_file = get_table(reg, region_)
        region_.total_bkg_exp[reg] = get_total_exp_mc(table_file)
        region_.total_stat_err[reg] = get_total_stat_err(table_file)
        region_.total_sys_err[reg] = get_total_sys_err(table_file)

def combine_systematics(region_) :
    for reg in region_.regions :
        for group in region_.groups :
            g_combined = 0.0
            for sys in group.systematics :
                 g_combined += sys.variation[reg] * sys.variation[reg]
            group.combined[reg] = math.sqrt(g_combined)
        


#################################################
if __name__=="__main__" :
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--texdir", default="", help="Provide the directory containing the .tex SysTables")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Print out some more goings-on")
    parser.add_argument("-r", "--region", default="", help="Provide the base region (e.g. Super1)")
    args = parser.parse_args()
    global dbg, region
    dbg = args.verbose
    base_region = args.region
    texdir = args.texdir


    region_ = Region(base_region)
    print region_.regions
    region_.collect_systables(texdir)

    for group in systematics_by_group.keys() :
        g = Group(group)
        for sys in systematics_by_group[group] :
            g.systematics.append(Systematic(sys))
        region_.groups.append(g)


    # fill the systematics within each group
    fill_systematics(region_)
    # combine the systmeatics within each group
    # by adding them with one another in quadrature
    combine_systematics(region_)

    # now collect the total region expected yields, total systematic variation
    # and region statistical uncertainties
    collect_region_totals(region_)

    if dbg :
        for r in region_.regions :
            print 15*"+ "
            print "yield: %.2f    stat: %.2f     sys: %.2f"%(region_.total_bkg_exp[r], region_.total_stat_err[r], region_.total_sys_err[r])
            for g in region_.groups :
                print "%s %s"%(r, g.groupname)
                for sys in g.systematics :
                    print "\t{}: {}".format(sys.sysname, sys.variation[r])
                print "--> combined: %.2f"%g.combined[r]

    ########################################
    # make table for summary
    ########################################
    col_width = 15
    lstr_col = ('{:<'+str(col_width)+'s}')
    rstr_col = ('{:>'+str(col_width)+'s}')
    num_col  = ('{:>'+str(col_width)+'.2f}')
    sf_region, df_region = "", ""
    for r in region_.regions :
        if "sf" in r : sf_region = r
        if "df" in r or "em" in r : df_region = r
    fields = ['contribution', sf_region + " (+/- #evt)", df_region + " (+/- #evt)"]
    header_template = ' '.join([lstr_col]+[rstr_col for f in fields[1:]])
    line_template   = ' '.join([lstr_col]+[num_col for f in fields[1:]])
    header = header_template.format(*fields)
    line_break = '-'*(col_width*len(fields)+1*(len(fields)-1))

    print (line_break)
    print (header)
    print (line_break)

    sys_summary = [ {'contribution': g.groupname,
                     sf_region + " (+/- #evt)" : g.combined[sf_region],
                     df_region + " (+/- #evt)": g.combined[df_region] 
                    }
                    for g in region_.groups]
    sys_stat = [ {'contribution' : "MC statistics",
                  sf_region + " (+/- #evt)" : region_.total_stat_err[sf_region],
                  df_region + " (+/- #evt)" : region_.total_stat_err[df_region] } ]
    sys_summary += sys_stat
    lines = [line_template.format(*(a[k] for k in fields)) for a in sys_summary]
    print ('\n'.join(lines))
    print (line_break)
    sys_total = [ {'contribution' : "Total",
                   sf_region + " (+/- #evt)" : region_.total_sys_err[sf_region],
                   df_region + " (+/- #evt)" : region_.total_sys_err[df_region] } ]
    lines = [line_template.format(*(a[k] for k in fields)) for a in sys_total]
    print ('\n'.join(lines))
    print (line_break)
    yld = [ {'contribution' : "Yields (#evt)",
             sf_region + " (+/- #evt)" : region_.total_bkg_exp[sf_region],
             df_region + " (+/- #evt)" : region_.total_bkg_exp[df_region] }]
    lines = [line_template.format(*(a[k] for k in fields)) for a in yld]
    print ('\n'.join(lines))
    print (line_break)
    
