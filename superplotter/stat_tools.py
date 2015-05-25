#
# Useful statistics tools used often
#
# daniel.joseph.antrim@cern.ch
# May 2015
#

import ROOT as r
import math 
from array import array


def get_sigma_from_pvalue(pvalue) :
    '''
    Convert p-value in standard deviations ("nsigma")
    Taken from HistFitter/src/StatTools::GetSigma( Double_t p )
    Equivalent: S = TMath::NormQuantile(1-p)
    '''
    if ( pvalue > (1.0-1e-16) ) : return -7.4
    if ( pvalue < (1e-16)) : return 7.4
    nsigma = 0.0
    if ( pvalue > 1.0e-16 ) :
        nsigma = r.TMath.ErfInverse( 1.0 - 2.0 * pvalue ) * r.TMath.Sqrt(2.0)
    elif ( pvalue > 0 ) :
        # use approximation, ok for sigma > 1.5
        u = -2.0 * r.TMath.Log( pvalue * r.TMath.Sqrt(2.0 * r.TMath.Pi() ) )
        nsigma = r.TMath.Sqrt( u - r.TMath.Log(u) )
    else :
        nsigma = -1
    return nsigma
