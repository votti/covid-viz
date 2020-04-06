# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.3.4
#   kernelspec:
#     display_name: Python [conda env:covid]
#     language: python
#     name: conda-env-covid-py
# ---

# %% [markdown]
# # Data overview
#
# by Vito Zanotelli <vito.zanotelli@gmail.com>
#
# ## Aim:
# This should provides some quick visualization and data exploration over all variables in the openZH/covid19 data repository.
#
#
# Note that I am NOT an epidemiologist and these visualizations these numbers and plots have plenty of caveats.
#
# The analysis is kept as tidy as possible. Any feedback welcome!
#
# Parts adapted from the 'visualise' notebook by Tim Head <betatim@gmail.com> licensed under CC-BY-4 (https://github.com/openZH/covid_19/blob/master/visualise.ipynb).

# %%
# visualization
import colorcet # colormaps
import plotnine as gg # a great ggplot clone

# %matplotlib inline

# %%
# General
import pandas as pd
import numpy as np
import glob

# %%
import helpers.library as lib


# %%
class C:
    """
    Helper class to keep input configuration.
    """
    glob_cases = "data/covid/covid_19/fallzahlen_kanton_total_csv/COVID19_Fallzahlen_Kanton_*total.csv"
    
    
class V:
    """
    Helper class to keep metadata related variables.
    """
    # User columns
    COL_VARIABLES = 'variables'
    COL_VALUE = 'value'
    
    # Data columns: from the data description from https://github.com/openZH/covid_19
    COL_DATE = 'date'
    COL_CANTON = 'abbreviation_canton_and_fl'
    
    COL_CUM_CONFIRMED = 'ncumul_conf'
    COL_CUM_DECEASED = 'ncumul_deceased' # number of deaths
    COL_CUM_TESTED = 'ncumul_tested'
    
    COL_CUR_HOSP = 'ncumul_hosp'
    COL_CUR_ICU = 'ncumul_ICU'
    COL_CUR_VENT = 'ncumul_vent'
    
    COL_CUM_RELEASED = 'ncumul_released'
    COL_CUM_CURED = 'TotalCured'
    
    
    vars_labels = {COL_CUM_CONFIRMED: 'Total confirmed cases',
                  COL_CUR_HOSP: 'Current hospitalized cases',
                  COL_CUM_DECEASED: 'Total deceased cases',
                  COL_CUR_ICU: 'Current intensive care cases',
                  COL_CUR_VENT: 'Current ventilator cases',
                  COL_CUM_RELEASED: 'Total released from hospital',
                  COL_CUM_CURED: 'Total cured cases',
                  COL_CUM_TESTED: 'Total tested cases'
        
    }
    vars_all = vars_labels.keys()
    
    # My main variables of interest
    vars_main = [COL_CUM_CONFIRMED,
                     COL_CUM_DECEASED,
                     COL_CUR_HOSP]


# %% [markdown]
# Load data

# %%
tdats = map(pd.read_csv, glob.glob(C.glob_cases))
dat_total = pd.concat(tdats)

# %%
dat_total.columns

# %%
dat_total.head()

# %% [markdown]
# ## Start Visualizations
#
#

# %% [markdown]
# Parsing of metadata into the right classes

# %%
dat_total[V.COL_DATE] = pd.to_datetime(dat_total[V.COL_DATE], dayfirst=True)
dat_total[V.COL_CANTON] = pd.Categorical(dat_total[V.COL_CANTON])

# %% [markdown]
# Interpolate data to get daily values

# %%
dat_daily = lib.transform_daily_per_canton(dat_total, V.vars_all, col_canton=V.COL_CANTON, col_date=V.COL_DATE)

# %% [markdown]
# Plot the most interesting values over time

# %%
cur_vars = V.vars_main

g = (dat_daily
     .melt(id_vars=[V.COL_DATE, V.COL_CANTON], value_vars=cur_vars,
           var_name=V.COL_VARIABLES,
          value_name=V.COL_VALUE)
     .assign(**{V.COL_VARIABLES:
                lambda x: pd.Categorical(x[V.COL_VARIABLES],
                                         categories=cur_vars)
                          .rename_categories(V.vars_labels)})
    
     >>
     gg.ggplot(gg.aes(x=f'{V.COL_DATE}', y=V.COL_VALUE, fill=V.COL_CANTON))
     + gg.facet_grid(f'{V.COL_VARIABLES}~.', scales='free_y')
     + gg.geom_bar(stat='identity')
     + gg.scale_fill_manual(colorcet.glasbey, name='Cantons')
     + gg.scale_x_datetime(date_breaks='1 week')
     + gg.xlab('Date')
     + gg.ylab('Cases')
     + gg.ggtitle('Covid-19 in Switzerland')
     + gg.theme_minimal()
     + gg.theme(axis_text_x = gg.element_text(angle = 90, hjust = 1),
               figure_size=(3,10)
               )
 
 
)
g

# %% [markdown]
# Things to improve:
# - Sort cantons according to the total incidence instead of alphabetically
#

# %%
cord = (dat_daily
    .groupby(V.COL_CANTON)
    [V.COL_CUM_DECEASED].mean()
    .sort_values(ascending=False)
    .index
)
cat_cantons_deceased= pd.CategoricalDtype(cord.astype(str), ordered=True)

# %% [markdown]
# Sorted cantons

# %%
cur_vars = V.vars_main

g = (dat_daily
     .melt(id_vars=[V.COL_DATE, V.COL_CANTON], value_vars=cur_vars,
           var_name=V.COL_VARIABLES,
          value_name=V.COL_VALUE)
     .assign(**{V.COL_VARIABLES:
                lambda x: pd.Categorical(x[V.COL_VARIABLES],
                                         categories=cur_vars)
                          .rename_categories(V.vars_labels)})
         .assign(**{V.COL_CANTON: lambda x: lib.order_cat(x[V.COL_CANTON],cat_cantons_deceased,
                                                 rev=True)})
    
     >>
     gg.ggplot(gg.aes(x=f'{V.COL_DATE}', y=V.COL_VALUE, fill=V.COL_CANTON))
     + gg.facet_grid(f'{V.COL_VARIABLES}~.', scales='free_y')
     + gg.geom_bar(stat='identity')
     + gg.scale_fill_manual(colorcet.glasbey, name='Cantons',
                            guide = gg.guide_legend(reverse = True))
     + gg.scale_x_datetime(date_breaks='1 week')
     + gg.xlab('Date')
     + gg.ylab('Cases')
     + gg.ggtitle('Covid-19 in Switzerland')
     + gg.theme_minimal()
     + gg.theme(axis_text_x = gg.element_text(angle = 90, hjust = 1),
               figure_size=(3,10)
               )
 
 
)
g

# %% [markdown]
# Also plot all the variables - this might be informative but also wil be quite messy

# %%
cur_vars = V.vars_all

g = (dat_daily
     .melt(id_vars=[V.COL_DATE, V.COL_CANTON], value_vars=cur_vars,
           var_name=V.COL_VARIABLES,
          value_name=V.COL_VALUE)
     .assign(**{V.COL_VARIABLES:
                lambda x: pd.Categorical(x[V.COL_VARIABLES],
                                         categories=cur_vars)
                          .rename_categories(V.vars_labels)})
         .assign(**{V.COL_CANTON: lambda x: lib.order_cat(x[V.COL_CANTON],cat_cantons_deceased,
                                                 rev=True)})
    
     >>
     gg.ggplot(gg.aes(x=f'{V.COL_DATE}', y=V.COL_VALUE, fill=V.COL_CANTON))
     + gg.facet_wrap(f'{V.COL_VARIABLES}', scales='free_y')
     + gg.geom_bar(stat='identity')
     + gg.scale_fill_manual(colorcet.glasbey, name='Cantons',
                            guide = gg.guide_legend(reverse = True))
     + gg.scale_x_datetime(date_breaks='1 week')
     + gg.xlab('Date')
     + gg.ylab('Cases')
     + gg.ggtitle('Covid-19 in Switzerland')
     + gg.theme_minimal()
     + gg.theme(axis_text_x = gg.element_text(angle = 90, hjust = 1),
               figure_size=(10,10),
                subplots_adjust={'wspace': 0.4})
 
 
)
g

# %% [markdown]
# While this gives quite a good overview, it might be interesting to visualize these per canton, so per canton trends are better visible:

# %%
cur_vars = V.vars_main
g = (dat_daily
     .melt(id_vars=[V.COL_DATE, V.COL_CANTON], value_vars=cur_vars,
           var_name=V.COL_VARIABLES,
          value_name=V.COL_VALUE)
     .assign(**{V.COL_VARIABLES:
                lambda x: pd.Categorical(x[V.COL_VARIABLES],
                                         categories=cur_vars)
                          .rename_categories(V.vars_labels)})
         .assign(**{V.COL_CANTON: lambda x: lib.order_cat(x[V.COL_CANTON],cat_cantons_deceased,
                                                 rev=False)})
     >>
     gg.ggplot(gg.aes(x=f'{V.COL_DATE}',
                      y=V.COL_VALUE,
                      color=V.COL_VARIABLES))
     + gg.facet_wrap(f'{V.COL_CANTON}')
     + gg.geom_line(stat='identity')
     + gg.scale_color_manual(colorcet.glasbey)
     + gg.scale_x_datetime(date_breaks='1 week')
     + gg.scale_y_log10()
     + gg.xlab('Date')
     + gg.ylab('Cases')
     + gg.ggtitle('Cases per canton')
     + gg.theme_minimal()
     + gg.theme(axis_text_x = gg.element_text(angle = 90, hjust = 1),
               figure_size=(10,10))
 
)
g

# %%
# also once with linear scale
g + gg.scale_y_continuous()

# %%
# linear scale but with individual scaling

cur_vars = V.vars_main

g = (dat_daily
     .melt(id_vars=[V.COL_DATE, V.COL_CANTON], value_vars=cur_vars,
           var_name=V.COL_VARIABLES,
          value_name=V.COL_VALUE)
     .assign(**{V.COL_VARIABLES:
                lambda x: pd.Categorical(x[V.COL_VARIABLES],
                                         categories=cur_vars)
                          .rename_categories(V.vars_labels)})
         .assign(**{V.COL_CANTON: lambda x: lib.order_cat(x[V.COL_CANTON],cat_cantons_deceased,
                                                 rev=False)})
     >>
     gg.ggplot(gg.aes(x=f'{V.COL_DATE}',
                      y=V.COL_VALUE,
                      color=V.COL_VARIABLES))
     + gg.facet_wrap(f'{V.COL_CANTON}', scales='free_y')
     + gg.geom_line(stat='identity')
     + gg.scale_color_manual(colorcet.glasbey)
     + gg.scale_x_datetime(date_breaks='1 week')
     + gg.xlab('Date')
     + gg.ylab('Cases')
     + gg.ggtitle('Cases per canton')
     + gg.theme_minimal()
     + gg.theme(axis_text_x = gg.element_text(angle = 90, hjust = 1),
               figure_size=(10,10),
                subplots_adjust={'wspace': 0.4})
 
)
g

# %% [markdown]
# Plot each variable individually + overlay original data points

# %%
g = (dat_daily
    .assign(**{V.COL_CANTON: lambda x: lib.order_cat(x[V.COL_CANTON],cat_cantons_deceased,
                                                 rev=False)})
     >>
     gg.ggplot(gg.aes(x=f'{V.COL_DATE}'))
     + gg.facet_wrap(f'{V.COL_CANTON}')
     + gg.scale_fill_manual(colorcet.glasbey)
     + gg.scale_x_datetime(date_breaks='1 week')
     + gg.scale_y_log10()
     + gg.xlab('Date')
     + gg.theme_minimal()
     +gg.theme(axis_text_x = gg.element_text(angle = 90, hjust = 1))
 
)
    
dt = (dat_total.assign(**{V.COL_CANTON: lambda x: lib.order_cat(x[V.COL_CANTON],cat_cantons_deceased,
                                                 rev=False)}))
for var in V.vars_main:
    (g + gg.geom_line(gg.aes(y=var), color='grey')
     + gg.geom_point(gg.aes(y=var), data=dt, color='black')
     + gg.ylab(V.vars_labels[var])
        + gg.ggtitle(V.vars_labels[var])).draw() 

# %% [markdown]
# Also once for all parameters:

# %%
cur_vars = V.vars_all
g = (dat_daily
     .melt(id_vars=[V.COL_DATE, V.COL_CANTON], value_vars=cur_vars,
           var_name=V.COL_VARIABLES,
          value_name=V.COL_VALUE)
     .assign(**{V.COL_VARIABLES:
                lambda x: pd.Categorical(x[V.COL_VARIABLES],
                                         categories=cur_vars)
                          .rename_categories(V.vars_labels)})
         .assign(**{V.COL_CANTON: lambda x: lib.order_cat(x[V.COL_CANTON],cat_cantons_deceased,
                                                 rev=False)})
     >>
     gg.ggplot(gg.aes(x=f'{V.COL_DATE}',
                      y=V.COL_VALUE,
                      color=V.COL_VARIABLES))
     + gg.facet_wrap(f'{V.COL_CANTON}')
     + gg.geom_line(stat='identity')
     + gg.scale_color_manual(colorcet.glasbey)
     + gg.scale_x_datetime(date_breaks='1 week')
     + gg.scale_y_log10()
     + gg.xlab('Date')
     + gg.ylab('Cases')
     + gg.ggtitle('Cases per canton')
     + gg.theme_minimal()
     + gg.theme(axis_text_x = gg.element_text(angle = 90, hjust = 1),
               figure_size=(10,10))
 
)
g

# %%
# linear scale but with individual scaling

cur_vars = V.vars_all

g = (dat_daily
     .melt(id_vars=[V.COL_DATE, V.COL_CANTON], value_vars=cur_vars,
           var_name=V.COL_VARIABLES,
          value_name=V.COL_VALUE)
     .assign(**{V.COL_VARIABLES:
                lambda x: pd.Categorical(x[V.COL_VARIABLES],
                                         categories=cur_vars)
                          .rename_categories(V.vars_labels)})
         .assign(**{V.COL_CANTON: lambda x: lib.order_cat(x[V.COL_CANTON],cat_cantons_deceased,
                                                 rev=False)})
     >>
     gg.ggplot(gg.aes(x=f'{V.COL_DATE}',
                      y=V.COL_VALUE,
                      color=V.COL_VARIABLES))
     + gg.facet_wrap(f'{V.COL_CANTON}', scales='free_y')
     + gg.geom_line(stat='identity')
     + gg.scale_color_manual(colorcet.glasbey)
     + gg.scale_x_datetime(date_breaks='1 week')
     + gg.xlab('Date')
     + gg.ylab('Cases')
     + gg.ggtitle('Cases per canton')
     + gg.theme_minimal()
     + gg.theme(axis_text_x = gg.element_text(angle = 90, hjust = 1),
               figure_size=(10,10),
                subplots_adjust={'wspace': 0.4})
 
)
g

# %% [markdown]
# Where to go from here:
# - Correlating data with canton population size
# - Mapping on Swiss map
# - Spatio-temporal analysis with R-inla?

# %% [markdown]
# My conda environment

# %%
import sys
# !conda env export -p {sys.prefix}
