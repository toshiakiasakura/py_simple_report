from typing import Union, Optional, List, Dict, Tuple, Any
from collections import OrderedDict
import os
import subprocess

import numpy as np
import pandas as pd

from . import variables as vs

def item_str2dict(s : str, missing : Optional[str] =None) -> dict:
    """Convert strings in items column into dictionary format.
    If keys can be converted into float type, convert into float. 

    Args:
        s : string containing information of match patterns between 
            numerical categories and string categories. 
        missing : items for missing. If a string is specified, that string is 
            used to display the name of missing.

    Returns:
        Keys are numerical categories. Values are string categories.
    """
    lis = s.replace("，", ",")\
            .split(",")
    dic = OrderedDict()
    for l in lis:
        try:
            k,v = l.split("=")
        except:
            raise Exception(f"Split by '=' should be 2 compositions :\nItems: {lis}")
        k = k.strip(" ").strip("　")
        if isinstance(k, str) and k.isnumeric():
            k = float(k)
        dic[k] = v
    if not isinstance(missing, type(None)):
        dic[np.nan] = missing
    return(dic)

def imputate_reorder_table(
    table_: pd.DataFrame, 
    cols_: List[str], 
    rows_: List[str], 
    fill_value: int = 0,
    allow_except: bool = True 
) -> pd.DataFrame:
    """Insert and reorder dataframe that is created from ".pivot_table" or ".crosstab".

    Args:
        table_ : dataframe that contains crosstabulated. 
        cols_ : columns are reordered by this list. 
        rows_ : rows are reordered by this list.
        fill_value : values to be filled.
        allow_except : If True, cols and rows that are not contained 
            in "cols_" and "rows_" remain. 
    
    Returns: 
        Reordered table.
    """
    cols_ = cols_.copy()
    rows_ = rows_.copy()
    for c in cols_:
        if c not in table_.columns:
            table_[c]=0
    for i in rows_:
        if i not in table_.index:
            table_.loc[i]=0

    # Accept "All"
    for c in table_.columns:
        if c == "All":
            cols_.append(c)
    for i in table_.index:
        if i == "All":
            rows_.append(i)

    if allow_except:
        for c in table_.columns:
            if c not in cols_:
                cols_.append(c) 
        for i in table_.index:
            if i not in rows_:
                rows_.append(i)
    else:
        if set(table_.columns) != set(cols_):
            s = f"Columns include some irregular items\n"
            s += f"original data : {table_.columns}\ncols : {cols_}"
            raise Exception(s)

    table_ = table_[cols_] 
    table_ = table_.loc[rows_]
    return(table_)

def save_number_to_data(
    tab : pd.DataFrame, 
    save_num_path : str,
    title : str = "",
    decimal : Optional[int] = None,
) -> None:
    """Add the number to data.
    """
    if not isinstance(decimal, type(None)):
        tab = tab.round(decimal)

    if os.path.exists(save_num_path):
        with open(save_num_path, "r", encoding="utf_8_sig") as f:
            s = f.read()
    else:
        s = ""

    s += f"\n\n{title}\n" + tab.to_csv()

    with open(save_num_path, "w", encoding="utf_8_sig") as f:
        f.write(s)

def delete_and_create_csv(save_num_path : str) -> None:
    """Delete and create csv file.
    """
    if os.path.exists(save_num_path):
        os.remove(save_num_path)
    with open(save_num_path,"w") as f:
        f.write("")

class PathOutput:
    def __init__(self, path : Optional[str]) -> None:
        """Generate a list of output path from one path.
        """
        self.raw = path
        if not isinstance(path, type(None)):
            name, ext = os.path.splitext(path)
            self.label_only = name + "_label_only" + ext
            self.no_label = name + "_no_label" + ext
        else:
            self.label_only = None
            self.no_label = None

def delete_All_from_index_column(tab : pd.DataFrame) -> pd.DataFrame:
    """Delete "All" row and column from dataframe. 
    """
    All = "All"
    if All in tab.index: 
        tab = tab.drop(index=All)
    if All in tab.columns:
        tab = tab.drop(columns=All)
    return(tab)



