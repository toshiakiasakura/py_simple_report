from typing import Union, Optional, List, Dict, Tuple, Any

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.cm as cm
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
from matplotlib.lines import Line2D
import japanize_matplotlib

import numpy as np
import pandas as pd
import cmocean

from . import variables as vs

class SingleVis():
    def __init__(self, vis_var : vs.VisVariables) -> None:
        """
        """
        self.vis_var = vis_var
        self.fig = plt.figure(figsize=vis_var.figsize, dpi=vis_var.dpi)
        self.ax = self.fig.add_subplot(111)

    def adjust_figure(self) -> None:
        vis_var = self.vis_var
        self.ax.set_title(vis_var.title, y=vis_var.titley)
        self.ax.set_xlabel(vis_var.xlabel, fontsize=vis_var.xlabelsize)
        self.ax.set_ylabel(vis_var.ylabel, fontsize=vis_var.ylabelsize)
        self.ax.set_xlim(vis_var.xlim) if vis_var.xlim else None
        self.ax.set_ylim(vis_var.ylim) if vis_var.ylim else None
        plt.xticks(rotation=vis_var.rotation)

        self.ax.tick_params(axis='x', which='major', labelsize=vis_var.xticksize)
        self.ax.tick_params(axis='y', which='major', labelsize=vis_var.yticksize)

        plt.tight_layout()
        if not isinstance(vis_var.save_fig_path, type(None)):
            plt.savefig(vis_var.save_fig_path, facecolor="white", bbox_inches="tight")
        if vis_var.show:
            plt.show()
        else:
            plt.close()

    def create_labels(self, tab : pd.DataFrame, 
                      missing : Optional[str] = None,
        ) -> None:
        patches = create_patch_for_label(
            label_names = tab.columns, #["test1", "test2", "test3"], 
            color = self.vis_var.colors,
            missing=missing,
            line=False)
        self.fig.patch.set_visible(False)
        self.ax.axis('off')
        self.ax.axes.xaxis.set_visible(False)
        self.ax.axes.yaxis.set_visible(False)
        plt.legend(handles=patches, frameon=False)
        if not isinstance(self.vis_var.save_fig_path, type(None)):
            plt.savefig(self.vis_var.save_fig_path, bbox_inches="tight")
        if self.vis_var.show:
            plt.show()
        else:
            plt.close()

    def one_cate_bar_plot(self, tab : pd.Series) -> None:
        self.ax.bar(tab.index, tab.values, **self.vis_var.main_kwgs)
        self.adjust_figure()

    def crosstab_cate_barplot(
        self,
        tab : pd.DataFrame,
        legend = True,
        percentage : bool = True,
    ) -> None:
        ax = tab.plot(kind="bar", ax=self.ax, stacked=False, color=self.vis_var.colors, 
                 **self.vis_var.main_kwgs)
        if percentage:
            format_percentage(self.ax, axis="y")
        draw_grid(self.ax, axis="y")
        if legend:
            self.ax.legend(bbox_to_anchor=(1,1))
        else:
            self.ax.get_legend().remove()
        self.adjust_figure()

    def crosstab_cate_stacked_barplot(
        self, 
        tab: pd.DataFrame, 
        legend=True, 
        percentage:bool=True,
    ) -> None:
        ax = tab.plot(kind="barh", ax=self.ax, stacked=True, color=self.vis_var.colors,
                 **self.vis_var.main_kwgs)
        if self.vis_var.annotate:
            n_rows, n_cols = tab.shape
            annotate_horizontal_stacked_barplot(ax, n_rows, n_cols, 
                                                fontsize=self.vis_var.annotate_fontsize,
                                                fmt=self.vis_var.annotate_fmt,
                                                cutoff_annotate=self.vis_var.annotate_cutoff,
                                                )
        if percentage:
            format_percentage(self.ax, axis="x")
        draw_grid(self.ax, axis="x")
        if legend:
            self.ax.legend(bbox_to_anchor=(1,1))
        else:
            self.ax.get_legend().remove()
        self.adjust_figure()

    def barplot_multi_binaries_with_strat(self, tab : pd.DataFrame, legend=True) -> None:
        self.vis_var.main_kwgs["width"] = self.vis_var.main_kwgs.get("width",0.9)
        tab.plot(kind="bar", ax=self.ax, stacked=False, color=self.vis_var.colors,
                 **self.vis_var.main_kwgs)
        format_percentage(self.ax, axis="y")
        draw_grid(self.ax, axis="y")
        if legend:
            self.ax.legend(bbox_to_anchor=(1,1))
        else:
            self.ax.get_legend().remove()
        self.adjust_figure()

def format_percentage(ax, axis="x"):
    # add %.
    fmt = '%.0f%%'
    ticks = mtick.FormatStrFormatter(fmt)
    if axis=="x":
        ax.xaxis.set_major_formatter(ticks)
    elif axis=="y":
        ax.yaxis.set_major_formatter(ticks)

def draw_grid(
    ax, 
    axis : str ="both", 
    color : str ="black", 
    linewidth : float = 0.2,
    linestyle : str = "dashed",
) -> None:
    # draw grid for y
    ax.grid(axis=axis, color=color, linewidth=linewidth, linestyle=linestyle)
    ax.set_axisbelow(True)

def annotate_horizontal_stacked_barplot(
    ax, 
    n_rows : int,
    n_cols : int,
    x_offset : float = 1,
    y_offset : float = 0,
    fmt : str = ".1f",
    cutoff_annotate : float = 10,
    fontsize : Optional[float] = None,
) -> None:
    """Annotate number/percentage of each category for horizontal stacked barplot. 

    Args:
        ax : axis returned by pd.plot.
        n_rows : number of rows (length of index if dataframe).
        n_cols : number of columns (length of columns if dataframe).
        fmt : string format for annotation.
        cutoff_annotate : If a value is smaller than this value, number/pecentage are hidden.
    """
    pos = (get_bbox_positions_as_df(ax)
           .sort_values(by=["y0", "x0", "x1"])
           .reset_index(drop=True)
          )
    for i in range(n_rows):
        st = i*n_cols
        fin = (i+1)*n_cols
        dfM = pos.loc[pos.index[st:fin]]
        #display(each)
        v = dfM["x1"]
        v_1 = v.shift(1).replace(np.nan,0)
        dfM["cate"] = v.sub(v_1)
        for i,b in dfM.iterrows():
            val = f"{b.cate:{fmt}}"
            if b.cate > cutoff_annotate:
                x_pos = b.x0 + x_offset
                y_pos = b.y0*3/4 + b.y1*1/4 + y_offset
                ax.annotate(val,  (x_pos , y_pos), color=b.color, fontsize=fontsize)

def get_bbox_positions_as_df(ax, cutoff_bright : float = 0.75) -> pd.DataFrame:
    """Get bbox positions of barplot to show number/percentage as annotations.
    Also, colors(white/black) is contained based on the brightness of filled colors.

    Args:
        ax : axis returned by pd.plot.

    Returns:
        DataFrame of positions and brightness, and text color. 
    """
    dic = dict(x0=[], x1=[], y0=[], y1=[], bright=[], color=[])
    for p in ax.patches:
        # Positions.
        b = p.get_bbox()
        for pos in ["x0","x1","y0","y1"]:
            dic[pos].append(getattr(b,pos))
        # Brightness. 
        bright = max(p.get_facecolor()[:3])
        c = "white" if bright <= cutoff_bright else "black"
        dic["bright"].append(bright)
        dic["color"].append(c)
    df = pd.DataFrame(dic)
    return(df)

def create_patch_for_label(
    label_names: List[str], 
    label_title: str = "", 
    cmap_type : str = "cmocean",
    cmap_name: str = "tab10", 
    color : Union[List[str], List[Tuple]] = None,
    line : bool = False,
    marker : Optional[List[str]] = None,
    markersize : Optional[int] = None,
    missing : str = "NaN"
    ) -> List[mpatches.Patch]:
    """Create list of patches for legend.

    Args:
        label_names : list of label names. 
        label_title : title of label handle.
        cmap_name : colormap name. 
        color : If color is specified, use this color set to display.
        line : legend becomes line style. 
        marker : marker for Line2D.
        markersize : markersize for Line2D

    Examples:
        >>> patches = utils.create_patch_for_label(label_names = ["test1", "test2", "test3"], color=["red","blue", "orange"] , line=True)
        >>> fig = plt.figure(figsize=(6,6), dpi=300 )
        >>> ax = fig.add_subplot(111)
        >>> ax.axes.xaxis.set_visible(False)
        >>> ax.axes.yaxis.set_visible(False)
        >>> plt.legend(handles=patches, frameon=False)
        >>> plt.show()
    """
    if isinstance(color, type(None)):
        cmap = get_cmap(cmap_type, cmap_name)
        cmap_cont = judge_cmap_is_continuous_or_not(cmap_type, cmap_name)
    patches = []
    #for c, name in zip(["blue","orange","green"],["男","女","不明"]):
    if marker is None:
        marker = [ None for i in range(len(label_names))]

    n = len(label_names)
    for i, name in enumerate(label_names):
        if name == missing:
            c = "grey"
        elif not isinstance(color, type(None)):
            c = color[i]
        elif cmap_cont:
            c = cmap(i/n)
        else:
            c = cmap(i)

        if line:
            patch = Line2D([0], [0], color=c, label=name, 
                        marker=marker[i], markersize=markersize)
        else:
            patch = mpatches.Patch(color=c, label=name)
        patches.append(patch)
    return(patches)

def label_only_fig(vis_var : vs.VisVariables, tab : pd.DataFrame, missing : str = np.nan) -> None:
    """Create label only figure. 

    Args:
        missing : If not given, missing color is not used.
    """
    vis = SingleVis(vis_var=vis_var)
    tab = tab.loc[tab.index[::-1]]
    vis.create_labels(tab, missing)

def obtain_cmap4labels(
    order : List[str],
    missing : str,
    vis_var: vs.VisVariables
) -> List[str]:
    """Obtain cmap for labels.

    Args:
        order : order of labels. 
        missing : a string of missing.
        vis_var : Visualization parameters.
    """
    cmap = get_cmap(vis_var.cmap_type, vis_var.cmap_name)
    cmap_cont = judge_cmap_is_continuous_or_not(vis_var.cmap_type, vis_var.cmap_name)
    colors = []
    n = len(order)
    for i, name in enumerate(order):
        if name == missing:
            c = "grey"
        else:
            c = cmap(i/n) if cmap_cont else cmap(i)
        colors.append(c)
    vis_var.colors = colors
    return(vis_var)

def get_cmap(cmap_type : str = "cmocean", cmap_name : str = "haline") -> Any:
    """Get cmap from matplotlib or cmocean. 

    Args:
        cmap_type : Takes "matplotlib" or "cmocean"
        cmap_name : a color map name.
    """
    if cmap_type == "matplotlib":
        cmap = plt.get_cmap(cmap_name)
    elif cmap_type == "cmocean":
        cmap = getattr(cmocean.cm, cmap_name)
    else:
        raise Exception("cmap_type takes 'matplotlib' or 'cmocean'")
    return cmap

def judge_cmap_is_continuous_or_not(
    cmap_type : str = "cmocean", cmap_name : str = "haline"
) -> bool:
    if cmap_type == "cmocean":
        bool_ = True
    else:
        qual = ['Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2',
                  'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b','tab20c']
        if cmap_name in qual:
            bool_ = False
        else:
            bool_ = True
    return (bool_)

