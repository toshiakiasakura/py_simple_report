from typing import Union, Optional, List, Dict, Tuple, Any
from collections import OrderedDict
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib

import variables as vs
import utils

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
    dic = utils.item_str2dict(str_items, missing)
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

    vis = utils.SingleVis(vis_var=vis_var)
    vis.one_cate_bar_plot(tab)

def wrapper_one_cate_bar_plot(
    df : pd.DataFrame,
    df_var : pd.DataFrame,
    vt : vs.VariableTable,
    q_num : str, 
    percentage : bool = False, 
    skip_miss : bool = False,
    vis_var : Optional[vs.VariableTable] = None,
) -> None:
    """Wrapper function of one cate bar plot.
    """
    qdc = create_one_question_data_container(df_var, q_num, vt)
    tab = one_cate_bar_data(df, qdc, percentage=False)
    tab_per = one_cate_bar_data(df, qdc, percentage=True)
    tab_skip = one_cate_bar_data(df, qdc, percentage=True, skip_miss=True)
    if isinstance(vis_var, type(None)):
        vis_var = vs.VisVariables()
    if isinstance(vis_var.rotation, type(None)):
        vis_var.rotation = 90 
    display(tab.to_frame())
    display(tab_per.to_frame())
    display(tab_skip.to_frame())
    if percentage:
        tab = tab_skip if skip_miss else tab_per
    one_cate_bar_plot(tab, qdc, vis_var, percentage=percentage)

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
    if skip_miss:
        ser = ser[~(ser==qdc.missing)] 
    if percentage:
        tab = (pd.crosstab(df[qdc_strf.var_name], ser, normalize="index", **crosstab_kwgs)
               .mul(100)
               )
    else:
        tab = pd.crosstab(df[qdc_strf.var_name], ser, **crosstab_kwgs)
    
    # reorder data.
    q_order = list(qdc.order)
    q_strf_order = list(qdc_strf.order)
    if skip_miss and (not isinstance(qdc.missing, type(None))):
        q_order.remove(qdc.missing)
    tab = utils.imputate_reorder_table(tab, q_order, q_strf_order, fill_value=0,
                                       allow_except=False)
    return tab

def crosstab_cate_stacked_plot(
    tab : pd.Series,
    qdc : vs.QuestionDataContainer,
    vis_var : vs.VisVariables,
    percentage : bool = False,
    legend : bool = True
) -> None:
    """Plot crosstabulational data.
    """
    if not vis_var.title:
        vis_var.title = qdc.title[:15]
    if not vis_var.xlabel:
        vis_var.xlabel = vis_var.label_count if not percentage else vis_var.label_cont 
    if percentage:
        if not vis_var.xlim:
            vis_var.xlim = [0,100]

    vis_var = utils.obtain_cmap4labels(qdc.order, qdc.missing, vis_var)
    vis = utils.SingleVis(vis_var=vis_var)
    tab = tab.loc[tab.index[::-1]]
    vis.crosstab_cate_stacked_plot(tab, legend=legend)

def wrapper_crosstab_cate_stacked_plot(
    df : pd.DataFrame,
    qdc : vs.QuestionDataContainer,
    qdc_strf : vs.QuestionDataContainer,
    skip_miss : bool = False,
    vis_var : Optional[vs.VariableTable] = None,
    save_fig_path : Optional[str] = None,
    save_num_path : Optional[str] = None,
    show : bool = True,
) -> None:
    """Wrapper function of crosstab categorical plot. 
    """
    percentage = True
    tab = crosstab_data(df, qdc, qdc_strf, percentage=False, skip_miss=False)
    tab_per  = crosstab_data(df, qdc, qdc_strf, percentage=percentage, skip_miss=False)
    tab_skip = crosstab_data(df, qdc, qdc_strf, percentage=percentage, skip_miss=True)

    # Numerical part.
    if show:
        display(tab)
        display(tab_per)
        display(tab_skip)
    if not isinstance(save_num_path, type(None)):
        title = f"{qdc.var_name}, {qdc.title}" 
        utils.save_number_to_data(tab, save_num_path, title=f"{title} raw number")
        utils.save_number_to_data(
            tab_per, save_num_path, title=f"{title} percentage(%) including missing", decimal=2)
        utils.save_number_to_data(
            tab_skip, save_num_path, title=f"{title} percentage(%) excluding missing", decimal=2)

    # Visualization part.
    if isinstance(vis_var, type(None)):
        vis_var = vs.VisVariables()
    vis_var.show = show
    if not isinstance(save_fig_path, type(None)):
        vis_var.save_fig_path = save_fig_path
    tab = tab_skip if skip_miss else tab_per
    crosstab_cate_stacked_plot(tab, qdc, vis_var, 
                               percentage=percentage, legend=True)

    if not isinstance(save_fig_path, type(None)):
        name, ext = os.path.splitext(save_fig_path)
        vis_var.save_fig_path = name + "_no_label" + ext
    crosstab_cate_stacked_plot(tab, qdc, vis_var, percentage=percentage, legend=False)

    # Create label only
    if not isinstance(save_fig_path, type(None)):
        vis_var.save_fig_path = name + "_label_only" + ext
    utils.label_only_fig(vis_var, tab, qdc.missing)

def debug_one_item_checker(df_var : pd.DataFrame, q_num : str, vt: vs.VariableTable) -> None:
    """Check question data for adjusting the variable table.
    """
    s =  "## Checking part ##\n\n"
    s += f"- Q : {q_num}\n"
    s += f"- Corresponding table : \n    {utils.item_str2dict(df_var.loc[q_num, vt.item])}\n"
    s += f"- Variable table : \n{df_var.loc[q_num]}\n"
    print(s)

def obtain_multi_binaries_items_with_strat(
    df : pd.DataFrame,
    q_nums : List[str],
    qdcs_dic : Dict[str, vs.QuestionDataContainer],
    qdc_strf : vs.QuestionDataContainer, 
    percentage : bool = True,
    fetch_value : Any = 1,
    crosstab_kwgs : Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """Calculate percentage of yes for multiple binary question items.
    
    Args : 
        q_nums : multiple binary question items for crosstabulation.
        fetch_value : a value for flag yes.
    """
    dfM = df.copy()
    # TODO : discriminate "欠損" and np.nan. Writing "欠損=チェックなし" is not sophisticated ideas to handle interpretation of missing. 
    #         Create a new column representing missing meaning is a better choice. 
    dfM[q_nums] = dfM[q_nums].replace(np.nan,0)
    df_sum = pd.DataFrame()
    for l in q_nums:
        # Create label. 
        qdc = qdcs_dic[l]
        label = qdc.dic[fetch_value] # Fetch "1" value.

        # Crosstabulate data.
        if percentage:
            tab = (pd.crosstab(dfM[qdc_strf.var_name], dfM[l], normalize="index")
                   .mul(100)
                   )
        else:
            tab = pd.crosstab(dfM[qdc_strf.var_name], dfM[l])
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
    if not vis_var.title:
        vis_var.title = ", ".join(order)[:15]
    if isinstance(vis_var.ylabel, type(None)):
        vis_var.ylabel = vis_var.label_count if not percentage else vis_var.label_cont 
    if percentage:
        if not vis_var.ylim:
            vis_var.ylim = [0,100]

    vis_var = utils.obtain_cmap4labels(order, np.nan, vis_var)
    vis = utils.SingleVis(vis_var=vis_var)
    vis.barplot_multi_binaries_with_strat(df_sum, legend=legend)

def wrapper_multi_binaries_with_strat(
    df : pd.DataFrame,
    q_nums : List[str], 
    qdcs_dic : Dict[str, vs.QuestionDataContainer],
    qdc_strf : vs.QuestionDataContainer,
    vis_var : Optional[vs.VariableTable] = None,
    save_fig_path : Optional[str] = None,
    save_num_path : Optional[str] = None,
    show : bool = True,
    transpose : bool = False
) -> None:
    """Wrap multiple binary items.
    """
    df_num = obtain_multi_binaries_items_with_strat(
           df, q_nums, qdcs_dic, qdc_strf, percentage=False)
    df_per = obtain_multi_binaries_items_with_strat(
           df, q_nums, qdcs_dic, qdc_strf, percentage=True)
    if transpose:
        df_per = df_per.T

    # number/percentage.
    if show:
        display(df_num)
        display(df_per)
    if not isinstance(save_num_path, type(None)):
        title = "_".join(q_nums)
        utils.save_number_to_data(df_num, save_num_path, title=f"raw number,{title} ")
        utils.save_number_to_data(
            df_per, save_num_path, title=f"percentage(%),{title} ", decimal=2)

    # Visualization.
    if isinstance(vis_var, type(None)):
        vis_var = vs.VisVariables()
    vis_var.show = show

    if not isinstance(save_fig_path, type(None)):
        vis_var.save_fig_path = save_fig_path
    barplot_multi_binaries_with_strat(df_per, vis_var, percentage=True, legend=True)

    if not isinstance(save_fig_path, type(None)):
        name, ext = os.path.splitext(save_fig_path)
        vis_var.save_fig_path = name + "_no_label" + ext
    barplot_multi_binaries_with_strat(df_per, vis_var, percentage=True, legend=False)

    # Create label only
    if not isinstance(save_fig_path, type(None)):
        vis_var.save_fig_path = name + "_label_only" + ext
    utils.label_only_fig(vis_var, df_per)
