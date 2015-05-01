''' These are the regions that will be avilable to the user. 
    Defined in terms of the user's input ntuples' leaf names.
    To be used in TTree::Draw (as TCut)'''  
# base regions strings
super1a = "isOS && nCentralLightJets==1 && nForwardJets==0 && nCentralBJets==0 && jet1Pt>80000. && mDeltaR>20000."
super1b = "isOS && nCentralLightJets==1 && nForwardJets==0 && nCentralBJets==0 && jet1Pt>80000. && mDeltaR>50000."
super1c = "isOS && nCentralLightJets==1 && nForwardJets==0 && nCentralBJets==0 && mDeltaR>20000."

# from the base regions, fill the sub-regions
regions = {}
regions['eeSuper1a'] = " isElEl && !(mll>(91200-10000) && mll<(91200+10000)) && dphi_ll_vBetaT>2 && R2>0.5 && " + super1a
regions['mmSuper1a'] = " isMuMu && !(mll>(91200-10000) && mll<(91200+10000)) && dphi_ll_vBetaT>2 && R2>0.5 && " + super1a
regions['emSuper1a'] = " isElMu && dphi_ll_vBetaT>2.5 && R2>0.7 && " + super1a

regions['eeSuper1b'] = " isElEl && !(mll>(91200-10000) && mll<(91200+10000)) && dphi_ll_vBetaT>2 && R2>0.5 && " + super1b
regions['mmSuper1b'] = " isMuMu && !(mll>(91200-10000) && mll<(91200+10000)) && dphi_ll_vBetaT>2 && R2>0.5 && " + super1b
regions['emSuper1b'] = " isElMu && dphi_ll_vBetaT>2.5 && R2>0.7 && " + super1b

regions['eeSuper1c'] = " isElEl && !(mll>(91200-10000) && mll<(91200+10000)) && jet1Pt>60000. && dphi_ll_vBetaT>2 && R2>0.65 && pTll<40000. && " + super1c
regions['mmSuper1c'] = " isMuMu && !(mll>(91200-10000) && mll<(91200+10000)) && jet1Pt>60000. && dphi_ll_vBetaT>2 && R2>0.65 && pTll<40000. && " + super1c
regions['emSuper1c'] = " isElMu && jet1Pt>80000. && dphi_ll_vBetaT>2.5 && R2>0.75 && pTll<50000. && " + super1c

''' These are the names that will be used on the plot legends, etc...
    The "official" names of the regions.'''
nice_names = {}
nice_names['eeSuper1a'] = 'eeSR2l-1a'
nice_names['mmSuper1a'] = 'mmSR2l-1a'
nice_names['eeSuper1a'] = 'eeSR2l-1a'
nice_names['mmSuper1b'] = 'mmSR2l-1b'
nice_names['emSuper1b'] = 'emSR2l-1b' 
nice_names['eeSuper1b'] = 'eeSR2l-1b' 
nice_names['mmSuper1c'] = 'mmSR2l-1c'
nice_names['emSuper1c'] = 'emSR2l-1c' 
nice_names['eeSuper1c'] = 'eeSR2l-1c' 


# -------------------------------------------- #
# Basic region functionality                   #
# -------------------------------------------- #
def is_valid_region(region) :
    if region not in regions.keys() : return False
    return True
def print_available_regions() :
    print regions.keys()

def get_region_tcut(region) :
    if regions[region] : return regions[region]
    else : print "get_region_tcut error: requested region not supported"

def get_nice_region_name(region) :
    if nice_names[region] : return nice_names[region]
    else : print "get_nice_region_name error: requested region not supported"

