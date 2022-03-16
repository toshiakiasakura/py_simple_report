import dataclasses
from typing import Union, Optional, List, Dict, Tuple, Any

class QuestionDataContainer():
    def __init__(
        self, 
        var_name : Optional[str] = None, # variable name shared with original data.
        desc : Optional[str] = None,
        title : Optional[str] = None, # var_name and desc.
        missing : Optional[str] = None,
        dic : Optional[dict] = None, # correspondence dict of numrical and string categories.
        order : Optional[list] = None,
     ) -> None:
        vars_ = locals()
        for k,v in vars_.items():
            setattr(self, k, v)

    def __repr__(self):
        return(f"qdc_{self.title}")

    def show(self):
        for k in ["var_name","desc", "title", "missing", "dic", "order"]:
            print(f"{k} : {getattr(self,k)}")

class VisVariables():
    def __init__(
        self,
        figsize : Tuple[int,int]= (5,3),
        dpi : int = 150,
        rotation : Optional[int] = None,
        xlabel : Optional[str] = None,
        ylabel : Optional[str] = None,
        xlabelsize : Optional[float] = None,
        ylabelsize : Optional[float] = None,
        xticksize : Optional[float] = None,
        yticksize : Optional[float] = None,
        xlim : Optional[List[float]] = None,
        ylim : Optional[List[float]] = None,
        title : Optional[str] = None,
        titley : Optional[float] = 1.05, # To easily hide title by cropping.
        main_kwgs = None,
        save_fig_path = None,
        cmap_type : str = "cmocean",
        cmap_name : str = "balance", # "tab10"
        # cmap name should be taken from cmocean website
        # https://matplotlib.org/cmocean/
        colors : Optional[list] = None,
        show : bool = True,
        label_count : str = "Count",
        label_cont : str = "Percentage (%)",
    ) -> None:
        vars_ = locals()
        for k,v in vars_.items():
            if k == "main_kwgs" and isinstance(v, type(None)):
                v = {}
            setattr(self, k, v)
        self.locals = vars_
