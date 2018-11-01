# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib as mpl


def plotgrid(dfs, sel_col = None, squash = False, sharey = True, sharex = True, xlabel = "", ylabel = ""):
    #use colsel to select the column in the final dataframe to be plotted, if blank then plot all or series
    dfs = dfs.swaplevel(0,1).sort_index()

    levels = dfs.index.levels

    ncol = len(levels[0])
    nrow = len(levels[1])

    colname = levels[0].name
    rowname = levels[1].name
    
    if(squash):
        nrow = 1
    fig, axes = plt.subplots(nrow,ncol,sharey = sharey, sharex=sharex, figsize = (2*ncol,2*nrow))

    for i, col in enumerate(levels[0]):
        for j, row in enumerate(levels[1]):
            if len(axes.shape) == 1:
                ax = axes[i]
            else:
                ax = axes[j][i]
                
            if(i==0):
                ax.set_ylabel(rowname +": " +str(row)+ '\n\n'+ ylabel)
                
            if col in dfs.index:
                dfs_i = dfs.loc[col]

                if row in dfs_i.index:
                    trace = dfs_i.loc[row]#[0]
                    if(sel_col != None):
                        trace = trace[trace.columns[sel_col]]
                    ax.plot(trace, label = (col,row))

                if(j==0):
                    ax.set_title(colname + ": " + str(col))
                if(j==nrow-1):
                    ax.set_xlabel(xlabel)
    return fig, axes