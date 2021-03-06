from dataclasses import dataclass
from typing import Union, Optional, List, Dict, Tuple, Any

@dataclass
class QuestionDataContainer():
    var_name : Optional[str] = None # variable name shared with original data.
    desc : Optional[str] = None
    title : Optional[str] = None # var_name and desc.
    missing : Optional[str] = None
    dic : Optional[dict] = None # correspondence dict of numrical and string categories.
    order : Optional[list] = None

    def __repr__(self):
        return(f"qdc_{self.title}")

    def show(self):
        for k in ["var_name","desc", "title", "missing", "dic", "order"]:
            print(f"{k} : {getattr(self,k)}")

@dataclass(repr=True)
class VisVariables():
    """This class controls visualization schemes. See each attribute explanation 
    for each role.

    Args:
        figsize : Figure size.
        dpi : dpi.
        xrotation : Rotate x label for this degree.
        yrotation : Rotate y label for this degree.
        xlabel : xlabel.
        ylabel : ylabel.
        xlabelsize : Control xlabel size.
        ylabelsize : Control ylabel size.
        xticksize : Control xtick size.
        yticksize : Control ytick size.
        cmap_type : Takes "cmocean" or "matplotlib" only. 
        cmap_name : colormap name. cmap name should be taken from cmocean website.
            See https://matplotlib.org/cmocean/
        annotate : If True, annotate each categorical values. 
        annotate_fontsize : fontsize of annotation.
        annotate_fmt : format defined by f-string for annotation.
        annotate_cutoff : If a value is smaller than this value, number/pecentage are hidden. 
    """
    figsize : Tuple[int,int]= (5,3)
    dpi : int = 150
    xrotation : Optional[int] = None
    yrotation : Optional[int] = None
    xlabel : Optional[str] = None
    ylabel : Optional[str] = None
    xlabelsize : Optional[float] = None
    ylabelsize : Optional[float] = None
    xticksize : Optional[float] = None
    yticksize : Optional[float] = None
    xlim : Optional[List[float]] = None
    ylim : Optional[List[float]] = None
    title : Optional[str] = None
    titley : Optional[float] = 1.05 # To easily hide title by cropping.
    main_kwgs = None
    save_fig_path = None
    cmap_type : str = "cmocean"
    cmap_name : str = "balance" # "tab10"
    colors : Optional[list] = None
    show : bool = True
    annotate : bool = True
    annotate_fontsize : Optional[str] = None
    annotate_fmt : str = ".1f"
    annotate_cutoff : float = 10
    label_count : str = "Count"
    label_cont : str = "Percentage (%)"

    def __post_init__(self):
        if self.main_kwgs is None:
            self.main_kwgs = {}
