from typing import Union, Optional, List, Dict, Tuple, Any
from collections import OrderedDict
import os
import copy

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib

from . import variables as vs
from . import utils
from . import vis_utils

def create_one_question_data_container(
    var_name: str, 
    str_items : str, 
    desc : str,
    missing : str = "missing",
) -> vs.QuestionDataContainer:
    """Create question data container object.

    Args:
        var_name : question variable name.
        str_items : strings which contain a corresponding matches for 
            all numerical values. 
            Ex. '1=very good,2=moderately good,3=moderately bad,4=bad'
        desc : a question description.
        missing : np.nan is replaced with this value.
    """
    if "=" in str_items:
        dic = utils.item_str2dict(str_items, missing)
    else:
        dic = {}
    qdc = vs.QuestionDataContainer(
        var_name = var_name, 
        dic   = dic, 
        order = dic.values(), 
        desc  = desc,
        title = f"{var_name}_{desc}",
        missing=missing 
    )
    return(qdc)

def question_data_containers_from_dataframe(
    df_var : pd.DataFrame,
    col_var_name : str,
    col_item : str,
    col_desc : str,
    missing : str = "missing",
) -> Dict[str, vs.QuestionDataContainer]:
    """QestionDataContainers for each question are constructed from 
    variable table of dataframe. 

    Args:
        df_var : a dataframe of a variable table. 
        col_var_name : a column name of variable name.
        col_item : a column name of a corresponding items.
        col_desc : a column name of a description of a question.
    """
    df_var = (df_var
              .copy()
              .set_index(col_var_name)
              )
    var_names = df_var.index
    dic = {}
    for var_name in var_names:
        ser = df_var.loc[var_name]
        item = ser[col_item]
        desc = ser[col_desc]

        if item is np.nan:
            continue
        qdc = create_one_question_data_container(
            var_name, item, desc, missing
        )
        dic[var_name] = qdc

    return dic

def one_cate_bar_data(
    df : pd.DataFrame,
    qdc : vs.QuestionDataContainer,
    percentage : bool = False,
    order : Optional[list] = None,
    skip_miss : bool = False,
) -> pd.Series:
    """Obtain summarized data for barplot. 
    1. Value_counts of a specific column. 
    2. Reorder index according to "order" parameters.
    3. Skip missing variables or not. 
    4. Adjsut percentage as 100% or not.
    """
    ser = df[qdc.var_name].replace(qdc.dic)
    tab = ser.value_counts()
    
    if not order:
        order = qdc.order

    # for calculation of excluding values of missing.
    if skip_miss: 
        tab = tab[~(tab.index==qdc.missing)]
        order = [o for o in order if o != qdc.missing]

    if set(order) != set(tab.index):
        raise Exception(f"Order : {order} and index {tab.index} are not matched")
    tab = tab.loc[order]

    if percentage:
        tab = tab.divide(tab.sum())*100
    return tab

def one_cate_bar_plot(
    tab : pd.Series,
    qdc : vs.QuestionDataContainer,
    vis_var : vs.VisVariables,
    percentage : bool = False,
) -> None:
    """Plotting bar plot for one categorical variable.
    """
    if not vis_var.title:
        vis_var.title = qdc.title
    if not vis_var.ylabel:
        vis_var.ylabel = vis_var.label_count if not percentage else vis_var.label_cont 

    vis = vis_utils.SingleVis(vis_var=vis_var)
    vis.one_cate_bar_plot(tab)

def crosstab_data(
    df : pd.DataFrame,
    qdc : vs.QuestionDataContainer,
    qdc_strf : vs.QuestionDataContainer,
    percentage : bool = True,
    skip_miss : bool = False,
    crosstab_kwgs : Optional[Dict[str, Any]] = None,  
) -> pd.DataFrame:
    """Crosstabulation of data given original dataframe, qdc and qdc_strf.
    Percentage and skip_miss are adjusted by parameters. 

    1. Cross tabulate a specific column with a column for stratification.. 
    2. Reorder index according to "order" in QuestionDataContainer..
    3. Skip missing variables or not. 
    4. Adjsut percentage as 100% or not.

    Args:
        corsstab_kwgs : a dictionary passed to pd.crosstab. 
            The "percentage" parameter edit this dictionary. 
    """
    
    if isinstance(crosstab_kwgs, type(None)):
        crosstab_kwgs = {}
        
    # cross tabulation.
    ser = df[qdc.var_name].replace(qdc.dic)
    ser_strf = df[qdc_strf.var_name].replace(qdc_strf.dic)
    if skip_miss:
        ser = ser[~(ser==qdc.missing)] 
    if percentage:
        tab = (pd.crosstab(ser_strf, ser, normalize="index", **crosstab_kwgs)
               .mul(100)
               )
    else:
        tab = pd.crosstab(ser_strf, ser, **crosstab_kwgs)
    
    # reorder data.
    q_order = list(qdc.order)
    q_strf_order = list(qdc_strf.order)
    if skip_miss and (not isinstance(qdc.missing, type(None))):
        q_order.remove(qdc.missing)
    tab = utils.imputate_reorder_table(tab, q_order, q_strf_order, fill_value=0,
                                       allow_except=False)
    return tab

def crosstab_cate_barplot(
    tab : pd.Series,
    qdc : vs.QuestionDataContainer,
    vis_var : vs.VisVariables,
    percentage : bool = False,
    legend : bool = True,
    transpose : bool = False,
) -> None:
    """Plot crosstabulational data.
    """
    if isinstance(vis_var.title, type(None)):
        vis_var.title = qdc.title[:15]
    if isinstance(vis_var.ylabel, type(None)):
        vis_var.ylabel = vis_var.label_count if not percentage else vis_var.label_cont 
    if percentage:
        if not vis_var.ylim:
            vis_var.ylim = [0,100]

    vis_var = vis_utils.obtain_cmap4labels(qdc.order, qdc.missing, vis_var)
    vis = vis_utils.SingleVis(vis_var=vis_var)
    vis.crosstab_cate_barplot(tab, legend=legend, percentage=percentage)

def crosstab_cate_stacked_barplot(
    tab : pd.Series,
    qdc : vs.QuestionDataContainer,
    vis_var : vs.VisVariables,
    percentage : bool = False,
    legend : bool = True
) -> None:
    """Plot crosstabulational data.
    """
    if isinstance(vis_var.title, type(None)):
        vis_var.title = qdc.title[:15]
    if isinstance(vis_var.xlabel, type(None)):
        vis_var.xlabel = vis_var.label_count if not percentage else vis_var.label_cont 
    if percentage:
        if not vis_var.xlim:
            vis_var.xlim = [0,100]

    vis_var = vis_utils.obtain_cmap4labels(qdc.order, qdc.missing, vis_var)
    vis = vis_utils.SingleVis(vis_var=vis_var)
    tab = tab.loc[tab.index[::-1]]
    vis.crosstab_cate_stacked_barplot(tab, legend=legend, percentage=percentage)

def output_crosstab_cate_barplot(
    df : pd.DataFrame,
    qdc : vs.QuestionDataContainer,
    qdc_strf : vs.QuestionDataContainer,
    skip_miss : bool = False,
    vis_var : Optional[vs.VisVariables] = None,
    save_fig_path : Optional[str] = None,
    save_num_path : Optional[str] = None,
    percentage : bool = True,
    include_all : bool = True,
    show : Union[bool,str] = True,
    decimal : int = 2,
    stacked : bool = True,
    transpose : bool = False,
) -> None:
    """Output cross-tabulated data as number/percentage and a figure.

    Args:
        df : DataFrame used for calculation.
        qdc : Can include missing.
        qdc_strf : For stratification. Can not include missing for this qdc.
        skip_miss : If True, missing of rows is ignored and percentage is calculated without missing.
        vis_var : For control of visualization. See vs.VisVariables for more detail.
        save_fig_path : Path for saving fig.
        save_num_path : Path for saving numbers/percentages.
        percentage : If True, a figure is created as a percentage style.
        include_all : If True, margins in pd.crosstab set True for number and percentage.
        show : Takes True, False, "number", "figure".
        decimal : Round to "decimal"th place when exporting a percentage.
        transpose : transpose dataframe.
    """
    if include_all:
        crosstab_kwgs = dict(margins=True)
    else:
        crosstab_kwgs = dict(margins=False)
    tab = crosstab_data(df, qdc, qdc_strf, percentage=False, skip_miss=False, 
                        crosstab_kwgs=crosstab_kwgs)
    tab_per  = crosstab_data(df, qdc, qdc_strf, percentage=percentage, skip_miss=skip_miss,
                         crosstab_kwgs=crosstab_kwgs)
    if transpose:
        tab = tab.T
        tab_per = tab_per.T

    # Number part.
    if (show == True) or (show == "number"):
        display(tab)
        display(tab_per)
    if not isinstance(save_num_path, type(None)):
        pre_title = f"{qdc.title}" 
        utils.save_number_to_data(tab, save_num_path, title=f"{pre_title} raw number")
        if skip_miss:
            title = f"{pre_title} percentage(%) excluding missing"
        else:
            title = f"{pre_title} percentage(%) including missing"
        utils.save_number_to_data(
            tab_per, save_num_path, title=title, decimal=decimal)

    if isinstance(vis_var, type(None)):
        vis_var = vs.VisVariables()
    else:
        vis_var = copy.deepcopy(vis_var)

    # Visualization part.
    if isinstance(vis_var, type(None)):
        vis_var = vs.VisVariables()
    if (show == True) or (show == "figure"):
        vis_var.show = True
    else:
        vis_var.show = False
    tab = tab_per if percentage else tab
    qdc = qdc if not transpose else qdc_strf
    path_output = utils.PathOutput(save_fig_path)
    # Since "All" should not be included here, delete "All" index and columns.
    tab = utils.delete_All_from_index_column(tab)

    vis_var.save_fig_path = path_output.raw
    if stacked:
        crosstab_cate_stacked_barplot(tab, qdc, vis_var, 
                                   percentage=percentage, legend=True)
    else:
        crosstab_cate_barplot(tab, qdc, vis_var, 
                                   percentage=percentage, legend=True)

    vis_var.save_fig_path = path_output.no_label
    if stacked:
        crosstab_cate_stacked_barplot(tab, qdc, vis_var, 
                                   percentage=percentage, legend=False)
    else:
        crosstab_cate_barplot(tab, qdc, vis_var, 
                                   percentage=percentage, legend=False)

    # Create label only
    vis_var.save_fig_path = path_output.label_only
    vis_utils.label_only_fig(vis_var, tab, qdc.missing)

def obtain_multi_binaries_items_with_strat(
    df : pd.DataFrame,
    q_var_names : List[str],
    qdcs_dic : Dict[str, vs.QuestionDataContainer],
    qdc_strf : vs.QuestionDataContainer, 
    percentage : bool = True,
    fetch_value : Any = 1,
    crosstab_kwgs : Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """Calculate percentage of yes for multiple binary question items.
    
    Args : 
        q_var_names: multiple binary question items for crosstabulation.
        fetch_value : a value for flag yes.
    """
    dfM = df.copy()
    dfM[q_var_names] = dfM[q_var_names].replace(np.nan,0)
    ser_strf = df[qdc_strf.var_name].replace(qdc_strf.dic)
    df_sum = pd.DataFrame()
    for l in q_var_names:
        # Create label. 
        qdc = qdcs_dic[l]
        label = qdc.dic[fetch_value] # Fetch "1" value.

        # Crosstabulate data.
        if percentage:
            tab = (pd.crosstab(ser_strf, dfM[l], normalize="index")
                   .mul(100)
                   )
        else:
            tab = pd.crosstab(ser_strf, dfM[l])
        per = tab[fetch_value].rename(label) # Fetch "1" value.
        df_sum = pd.concat((df_sum, per), axis=1)
    df_sum = df_sum.loc[qdc_strf.order]
    return(df_sum)

def barplot_multi_binaries_with_strat(
    df_sum : pd.Series,
    vis_var : vs.VisVariables,
    percentage : bool = False,
    legend : bool = True
) -> None:
    """Plot multiple binary items simultaneously.
    """
    order = df_sum.columns
    if isinstance(vis_var.title, type(None)):
        vis_var.title = ", ".join(order)[:15]
    if isinstance(vis_var.ylabel, type(None)):
        vis_var.ylabel = vis_var.label_count if not percentage else vis_var.label_cont 
    if percentage:
        if not vis_var.ylim:
            vis_var.ylim = [0,100]

    vis_var = vis_utils.obtain_cmap4labels(order, np.nan, vis_var)
    vis = vis_utils.SingleVis(vis_var=vis_var)
    vis.barplot_multi_binaries_with_strat(df_sum, legend=legend)

def output_multi_binaries_with_strat(
    df : pd.DataFrame,
    q_var_names: List[str], 
    qdcs_dic : Dict[str, vs.QuestionDataContainer],
    qdc_strf : vs.QuestionDataContainer,
    vis_var : Optional[vs.VisVariables] = None,
    save_fig_path : Optional[str] = None,
    save_num_path : Optional[str] = None,
    show : bool = True,
    percentage : bool = True,
    transpose : bool = False,
    decimal : int = 2,
) -> None:
    """Output cross-tabulated data as number/percentage and a figure.

    Args:
        df :
        q_var_names :
        qdcs_dic : 
        qdc_strf :
        vis_var :
        save_fig_path :
        save_num_path :
        percentage : If True, a figure is created as a percentage style.
        show : Takes True, False, "number", "figure".
        transpose : If True, x and y axis is swapped when plotting.
        decimal : Round to "decimal"th place when exporting a percentage.
    """
    df_num = obtain_multi_binaries_items_with_strat(
           df, q_var_names, qdcs_dic, qdc_strf, percentage=False)
    df_per = obtain_multi_binaries_items_with_strat(
           df, q_var_names, qdcs_dic, qdc_strf, percentage=True)
    if transpose:
        df_num = df_num.T
        df_per = df_per.T

    # Number part.
    if (show == True) or (show == "number"):
        display(df_num)
        display(df_per)
    if not isinstance(save_num_path, type(None)):
        pre_title = "_".join(q_var_names)
        utils.save_number_to_data(df_num, save_num_path, title=f"raw number,{pre_title}")
        utils.save_number_to_data(
            df_per, save_num_path, title=f"percentage(%) ,{pre_title} ", decimal=decimal)
    if isinstance(vis_var, type(None)):
        vis_var = vs.VisVariables()


    # Visualization.
    if isinstance(vis_var, type(None)):
        vis_var = vs.VisVariables()
    else:
        vis_var = copy.deepcopy(vis_var)
    if (show == True) or (show == "figure"):
        vis_var.show = True
    else:
        vis_var.show = False

    df_ = df_per if percentage else df_num
    path_output = utils.PathOutput(save_fig_path)

    vis_var.save_fig_path = path_output.raw
    barplot_multi_binaries_with_strat(df_, vis_var, percentage=percentage, legend=True)

    vis_var.save_fig_path = path_output.no_label
    barplot_multi_binaries_with_strat(df_, vis_var, percentage=percentage, legend=False)

    # Create label only
    vis_var.save_fig_path = path_output.label_only
    vis_utils.label_only_fig(vis_var, df_)

