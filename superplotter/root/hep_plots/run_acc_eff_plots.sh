#!/usr/bin bash
regions=(eeSuper1a eeSuper1b eeSuper1c mmSuper1a mmSuper1b mmSuper1c emSuper1a emSuper1b emSuper1c)
grids=(SMCwslep)

for g in ${grids[@]}
do
    for region in ${regions[@]}
    do
        ./make_acc_and_eff_plots.py -r ${region} -g ${g} -o "plots/exA_plots_${g}" 
    done
done
