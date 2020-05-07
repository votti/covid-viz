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
# # ZH Monitoring overview
# by Vito Zanotelli, <vito.zanotelli@gmail.com>, Zurich 2020
#
# ## Aim:
# Get an overview of the statistikZH covid19monitoring dataset (https://github.com/statistikZH/covid19monitoring)
#
#
# ### Ideas:
# - Compare trends over a week (Mo-So) - is there a change in behaviour of people over the week?
#     - Hypotheses:
#         - Shopping behaviours should change, including potential shifts of main shopping days
#         - Larger effects around start of shutdown, weeks since then should find a new behaviour
#         - Mobility: Weekend mobility should be more heavily reduced than workday mobility
#
# import calendar
# import pathlib

# %%
# visualization
import colorcet  # colormaps
import numpy as np
# %%
# General
import calendar
import pandas as pd
import plotnine as gg  # a great ggplot clone

import pathlib
# %matplotlib inline

# %%


# %%
class C:
    """
    Helper class to keep input configuration.
    """
    fol_zhmonitor = pathlib.Path('./data/monitoring/covid19monitoring/')
    fn_zhmonitor_data = fol_zhmonitor / 'covid19socialmonitoring.csv'
    fn_zhmonitor_meta = fol_zhmonitor / 'Metadata.csv'

    day_start = pd.to_datetime('2020-01-06')
    day_intervention_v1 = pd.to_datetime('2020-02-28')  # First ban of large events
    day_intervention_v2 = pd.to_datetime('2020-03-13')  # School closures
    day_intervention_v3 = pd.to_datetime('2020-03-16')  # Lock down

    days_intervention = [day_intervention_v1, day_intervention_v2, day_intervention_v3]

    cm_discrete = colorcet.glasbey


class V:
    """
    Helper class to keep metadata related variables.
    """
    # Data columns:
    COL_VARIABLES = 'variable_short'
    COL_VALUE = 'value'
    COL_DATE = 'date'
    COL_LOCATION = 'location'

    # Main data columns
    cols_data = [COL_VARIABLES, COL_VALUE, COL_DATE, COL_LOCATION]

    # User data columns
    COL_MONTH = 'month'
    COL_YEAR = 'year'
    COL_WEEK = 'week'
    COL_ISWEEKDAY = 'is_weekday'
    COL_DAYOFWEEK = 'dayofweek'
    COL_HASFULLWEEK = 'fullweek'  # is the measurement available for all days of that week
    COL_HASCLOSEFULLWEEK = 'almostfullweek'

    COL_VALUE_LOG10 = 'value_log'
    COL_VALUE_NORM = 'value_norm'
    # Meta columns:
    COL_TOPIC = 'topic'
    COL_VAR_DESC = 'variable_long'
    COL_LOCATION = 'location'
    COL_UNIT = 'unit'
    COL_SOURCE = 'source'
    COL_UPDATE = 'update'
    COL_PUBLIC = 'public'
    COL_DESC_LINK = 'description'
    COL_MODIFIED = 'last_modified'

    # Categorical columns
    cols_cat = [COL_VARIABLES, COL_VAR_DESC, COL_LOCATION,
                COL_UNIT, COL_SOURCE, COL_UPDATE, COL_DESC_LINK]

    cols_date = [COL_MODIFIED,
                 COL_DATE]

    COL_CANTON = 'abbreviation_canton_and_fl'


# %% [markdown]
# ## Load and structure data

# %%
dat_zhmonitor = pd.read_csv(C.fn_zhmonitor_data)
dat_zhmonitor_m = pd.read_csv(C.fn_zhmonitor_meta)

# %%
dat_zhmonitor.head()

# %%

# %%
dat_zhmonitor_m.head()

# %%
# Delete redundant variables in data
dat_zhmonitor = dat_zhmonitor[V.cols_data]


# %%
# Convert date
def apply_to_cols(df, cols, fkt, inplace=True):
    if not inplace:
        df = df.copy()
    for c in set(cols).intersection(df.columns):
        df.loc[:, c] = fkt(df.loc[:, c])
    return df


# %%
# Convert variables to datetime and categorical
for d in [dat_zhmonitor, dat_zhmonitor_m]:
    apply_to_cols(d, V.cols_date, pd.to_datetime)
    apply_to_cols(d, V.cols_cat, pd.Categorical)

# %%
dat_zhmonitor

# %%
# Convert date into week, year and weekday

dat_zhmonitor[V.COL_DAYOFWEEK] = pd.Categorical.from_codes(dat_zhmonitor[V.COL_DATE].dt.dayofweek,
                                                           categories=list(calendar.day_abbr), ordered=True)

# %%
dat_zhmonitor[V.COL_MONTH] = pd.Categorical.from_codes(dat_zhmonitor[V.COL_DATE].dt.month,
                                                       categories=list(calendar.month_abbr))

# %%
dat_zhmonitor[V.COL_WEEK] = pd.Categorical.from_codes(dat_zhmonitor[V.COL_DATE].dt.week,
                                                      categories=[str(i) for i in range(53)])

# %%
dat_zhmonitor[V.COL_YEAR] = pd.Categorical(dat_zhmonitor[V.COL_DATE].dt.year.astype(str))

# %%
# Convert date into week, year and weekday

dat_zhmonitor[V.COL_ISWEEKDAY] = dat_zhmonitor[V.COL_DATE].dt.dayofweek < 5

# %%

# %%
dat_zhmonitor[V.COL_HASFULLWEEK] = dat_zhmonitor.groupby([V.COL_YEAR, V.COL_WEEK, V.COL_VARIABLES, V.COL_LOCATION])[
    V.COL_VALUE].transform(lambda x: np.sum(np.isfinite(x)) == 7)

# %%
dat_zhmonitor[V.COL_HASCLOSEFULLWEEK] = \
dat_zhmonitor.groupby([V.COL_YEAR, V.COL_WEEK, V.COL_VARIABLES, V.COL_LOCATION])[V.COL_VALUE].transform(
    lambda x: np.sum(np.isfinite(x)) >= 5)

# %%
dat_zhmonitor[V.COL_DAYOFWEEK].tail()

# %%
dat_zhmonitor[V.COL_ISWEEKDAY].tail()

# %% [markdown]
# ## Plot all the data to better understand what's there

# %%
dat_zhmonitor.query(f'{V.COL_VARIABLES} == "tages_distanz_median"')

# %%
p = (dat_zhmonitor
     .merge(dat_zhmonitor_m[[V.COL_VARIABLES, V.COL_VAR_DESC, V.COL_UNIT, V.COL_LOCATION]])
     .assign(**{'label': lambda x: x.apply(
    lambda r: f'{r[V.COL_VARIABLES]}\n{r[V.COL_VAR_DESC]}\n{r[V.COL_LOCATION]}\nin {r[V.COL_UNIT]}',
    axis=1)})
     >>
     gg.ggplot(gg.aes(x=V.COL_DATE, y=V.COL_VALUE, color=V.COL_DAYOFWEEK, shape=V.COL_ISWEEKDAY))
     + gg.facet_grid(f'label~.', scales='free'
                     )
     + gg.geom_line(gg.aes(group=V.COL_VARIABLES))
     + gg.geom_point(size=1.5)
     + gg.scale_color_cmap_d('Dark2')
     # + gg.scale_color_brewer(type='qual',palette=2)
     + gg.geom_vline(color='gray', linetype=':',
                     xintercept=[pd.to_datetime(f'2020-{m}-25') for m in range(1, 13)])
     + gg.geom_vline(linetype='-', color='b', xintercept=C.days_intervention,
                     alpha=0.7)
     + gg.theme_minimal()
     + gg.theme(axis_text_x=gg.element_text(angle=90, hjust=1),
                figure_size=(12, 85),
                strip_text_y=gg.element_text(angle=0, ha='left'),
                strip_margin_x=7,
                #   legend_position='left'
                )
     + gg.ggtitle('Overview of all indicators')

     )
(p
 + gg.scale_x_date(limits=[dat_zhmonitor[V.COL_DATE].min(), dat_zhmonitor[V.COL_DATE].max()],
                   breaks=pd.date_range(dat_zhmonitor[V.COL_DATE].min(),
                                        dat_zhmonitor[V.COL_DATE].max(), freq='W-MON'))
 )

# %%
# It seems that it would be better to only focus on the data since 03.01 - start after XMAS break

(p
 + gg.scale_x_date(limits=[C.day_start, dat_zhmonitor[V.COL_DATE].max()],
                   breaks=pd.date_range(dat_zhmonitor[V.COL_DATE].min(),
                                        dat_zhmonitor[V.COL_DATE].max(), freq='W-MON'))

 )

# %%

# %% [markdown]
# ### Observations
#
# Corona related:
# - Behaviour of most indicators as one would expect
#
# General:
# - Cool to see how cash withdrawal decreases allways until the next payday
# - All people move less on weekends
# - People spend most money abroad on Saturday and monday
#
#
# After looking at the data, it could indeed be interesting to look at changes in behaviour over the weekdays. This seems also a bit more robust against long timescale trends.
#
# - Use data from 3. Januar 2020 (Schulanfang)
# - Week from Monday-Sunday
# - Normalize by average levels of weekdays - weekends seem often more variable/outliers
#     -> TODO: Check if really true

# %%
# Quickly check variability of weekdays vs weekends over weeks
tdat = (dat_zhmonitor
        .merge(dat_zhmonitor_m[[V.COL_VARIABLES, V.COL_TOPIC, V.COL_LOCATION]])
        # .query(f'{V.COL_DATE} < {C.days_intervention[0]}') # doesnt work with dates yet
        .query(f'{V.COL_HASFULLWEEK} == True')
        .pipe(lambda d: d.loc[d[V.COL_DATE] < C.days_intervention[0], :])  # only before intervention
        .groupby([V.COL_DAYOFWEEK, V.COL_VARIABLES, V.COL_TOPIC, V.COL_LOCATION], observed=True)[V.COL_VALUE].describe()
        .reset_index()
        .assign(**{'cv': lambda x: x['std'] / np.abs(x['mean'])})
        .assign(**{'cv_norm': lambda d: d.groupby([V.COL_VARIABLES, V.COL_LOCATION])['cv']
                .transform(lambda x: x / x.mean())})

        )

(tdat >>
 gg.ggplot(gg.aes(x=V.COL_DAYOFWEEK, y='cv', color=V.COL_VARIABLES))
 + gg.geom_point()
 + gg.geom_line(gg.aes(group=V.COL_VARIABLES))
 # + gg.geom_smooth(gg.aes(group=V.COL_VARIABLES), method='lm')
 + gg.coord_cartesian(ylim=(0, 1))

 ).draw()

(tdat >>
 gg.ggplot(gg.aes(x=V.COL_DAYOFWEEK, y='cv_norm', color=V.COL_VARIABLES))
 + gg.geom_point()
 + gg.geom_line(gg.aes(group=V.COL_VARIABLES))

 # + gg.geom_smooth(gg.aes(group=V.COL_VARIABLES), method='lm')

 ).draw()

(tdat >>
 gg.ggplot(gg.aes(x='cv_norm'))
 + gg.facet_grid(f'{V.COL_DAYOFWEEK}~.')
 + gg.geom_histogram()
 + gg.geom_vline(xintercept=np.nanmedian(tdat['cv_norm']), color='grey')
 + gg.geom_vline(gg.aes(xintercept='cv_norm'),
                 data=(tdat
                       .groupby(V.COL_DAYOFWEEK, observed=True)['cv_norm']
                       .median().reset_index()),

                 linetype=':')
 # + gg.geom_smooth(gg.aes(group=V.COL_VARIABLES), method='lm')
 + gg.coord_cartesian(xlim=(0, 3))
 + gg.ggtitle('Variability of indicators per day of week')

 ).draw()

(tdat >>
 gg.ggplot(gg.aes(x='cv_norm'))
 + gg.facet_grid(f'{V.COL_DAYOFWEEK}~{V.COL_TOPIC}')
 + gg.geom_histogram()
 + gg.geom_vline(gg.aes(xintercept='cv_norm', color=V.COL_VARIABLES))
 + gg.scale_color_manual(C.cm_discrete)
 + gg.geom_vline(gg.aes(xintercept='cv_norm'),
                 data=(tdat
                       .groupby([V.COL_TOPIC], observed=True)['cv_norm']
                       .median().reset_index()), color='grey')
 + gg.geom_vline(gg.aes(xintercept='cv_norm'),
                 data=(tdat
                       .groupby([V.COL_DAYOFWEEK, V.COL_TOPIC], observed=True)['cv_norm']
                       .median().reset_index()),
                 linetype=':')
 + gg.coord_cartesian(xlim=(0, 3))
 + gg.ggtitle('Variability of indicators per day of week')

 ).draw()
1

# %% [markdown]
# -> Surprisingly (to me) variabiltiy fo the readouts doesnt seem strongly weekday dependent
#
# -> **I normalize over the whole week now.**

# %%
dat_zhmonitor = (dat_zhmonitor
                 .assign(**{
    V.COL_VALUE_LOG10: lambda x: np.log10(x[V.COL_VALUE])})
                 .assign(**{
    # V.COL_VALUE_NORM:
    # lambda d: (d.groupby([V.COL_YEAR, V.COL_WEEK, V.COL_VARIABLES],group_keys=False))
    #           .apply(lambda x:
    #                      x[V.COL_VALUE_LOG10]-x.loc[x[V.COL_ISWEEKDAY] == True, V.COL_VALUE_LOG10].mean())

    V.COL_VALUE_NORM:
        lambda d: (d.groupby([V.COL_YEAR, V.COL_WEEK, V.COL_VARIABLES], group_keys=False)
                   .apply(lambda x:
                          x[V.COL_VALUE] / x[V.COL_VALUE].mean())
                   )

})
                 )

# %% [markdown]
# How do the previous plot look per week?

# %%
pdat = (dat_zhmonitor
        .query(f'{V.COL_HASCLOSEFULLWEEK} == True')

        .pipe(lambda d: d.loc[d[V.COL_DATE] >= C.day_start, :])  # only before intervention
        .pipe(lambda d: d.loc[np.isfinite(d[V.COL_VALUE_NORM]), :])  # only finite
        .merge(dat_zhmonitor_m[[V.COL_VARIABLES, V.COL_VAR_DESC, V.COL_UNIT,
                                V.COL_LOCATION, V.COL_TOPIC]])
        .assign(**{'label': lambda x: x.apply(
    lambda r: f'{r[V.COL_VARIABLES]}\n{r[V.COL_VAR_DESC]}\n{r[V.COL_LOCATION]}\nin {r[V.COL_UNIT]}',
    axis=1)})
        )
p = (pdat >>
     gg.ggplot(gg.aes(x=V.COL_DATE, y=V.COL_VALUE_NORM, color=V.COL_DAYOFWEEK, shape=V.COL_ISWEEKDAY))
     + gg.facet_grid(f'label~.', scales='free'
                     )
     + gg.geom_line(gg.aes(group=[V.COL_WEEK]))
     + gg.geom_point(size=1.5)
     + gg.scale_color_cmap_d('Dark2')
     # + gg.scale_color_brewer(type='qual',palette=2)
     + gg.geom_vline(color='gray', linetype=':',
                     xintercept=[pd.to_datetime(f'2020-{m}-25') for m in range(1, 13)])
     + gg.geom_vline(linetype='-', color='b', xintercept=C.days_intervention,
                     alpha=0.7)
     + gg.theme_minimal()
     + gg.theme(axis_text_x=gg.element_text(angle=90, hjust=1),
                figure_size=(12, 85),
                strip_text_y=gg.element_text(angle=0, ha='left'),
                strip_margin_x=6,
                #   legend_position='left'
                )

     + gg.scale_x_date(limits=[pdat[V.COL_DATE].min(), pdat[V.COL_DATE].max()],
                       breaks=pd.date_range(C.day_start, pdat[V.COL_DATE].max(), freq='W-MON'))
     + gg.scale_y_log10()
     + gg.ggtitle('Overview of all indicators normalized by week average')
     )
p

# %% [markdown]
# - I have to think if using the rolling average of the last 7 days wouldn't be more meaningful.
# - Given more data it would be definitely good to take the mean over the previous and next days

# %% [markdown]
# ### Observations
# - The main day for shopping stationaries has shifted from Saturday to Friday
#
# - Online trainings have traditionally be rarely done on Saturdays.The first two weekends training seems to have been picked up relatively more and now Saturday and Sunday are about equally popular.
#
#

# %%
V.COL_VAR_STAT_EINKAUF = 'stat_einkauf'

p = (pdat
     .query(f'{V.COL_VARIABLES} in {[V.COL_VAR_STAT_EINKAUF]}')
     >>
     gg.ggplot(gg.aes(x=V.COL_DATE, y=V.COL_VALUE_NORM, color=V.COL_DAYOFWEEK, shape=V.COL_ISWEEKDAY))
     + gg.facet_grid(f'label~.', scales='free'
                     )
     + gg.geom_vline(color='gray', linetype=':',
                     xintercept=[pd.to_datetime(f'2020-{m}-25') for m in range(1, 13)])
     + gg.geom_vline(linetype='-', color='b', xintercept=C.days_intervention,
                     alpha=0.7)
     + gg.geom_line(gg.aes(group=[V.COL_WEEK]))
     + gg.geom_point(size=1.5)
     + gg.scale_color_cmap_d('Dark2')
     # + gg.scale_color_brewer(type='qual',palette=2)

     + gg.theme_minimal()
     + gg.theme(axis_text_x=gg.element_text(angle=90, hjust=1),
                figure_size=(6, 2),
                strip_text_y=gg.element_text(angle=0, ha='left'),
                strip_margin_x=6,
                #   legend_position='left'
                )

     + gg.scale_x_date(limits=[pdat[V.COL_DATE].min(), pdat[V.COL_DATE].max()],
                       breaks=pd.date_range(C.day_start, pdat[V.COL_DATE].max(), freq='W-MON'))
     + gg.scale_y_log10()
     + gg.ylab('Relative shopping expense')
     + gg.xlab('Date')
     + gg.ggtitle('Overview of stationary shopping expense\nnormalized by calendar week average')
     )
p

# %%
p = (pdat
     .query(f'{V.COL_VARIABLES} in {[V.COL_VAR_STAT_EINKAUF]}')
     >>
     gg.ggplot(gg.aes(x=V.COL_DATE, y=V.COL_VALUE, color=V.COL_DAYOFWEEK, shape=V.COL_ISWEEKDAY))
     + gg.facet_grid(f'label~.', scales='free'
                     )
     + gg.geom_vline(color='gray', linetype=':',
                     xintercept=[pd.to_datetime(f'2020-{m}-25') for m in range(1, 13)])
     + gg.geom_vline(linetype='-', color='b', xintercept=C.days_intervention,
                     alpha=0.7)
     + gg.geom_line(gg.aes(group=[V.COL_WEEK]))
     + gg.geom_point(size=1.5)
     + gg.scale_color_cmap_d('Dark2')
     + gg.geom_hline(yintercept=0)

     + gg.expand_limits(y=0)

     + gg.scale_x_date(limits=[pdat[V.COL_DATE].min(), pdat[V.COL_DATE].max()],
                       breaks=pd.date_range(C.day_start, pdat[V.COL_DATE].max(), freq='W-MON'))
     # + gg.scale_y_log10()

     + gg.theme_minimal()
     + gg.theme(axis_text_x=gg.element_text(angle=90, hjust=1),
                figure_size=(6, 2.5),
                strip_text_y=gg.element_text(angle=0, ha='left'),
                strip_margin_x=6,
                #   legend_position='left'
                )

     + gg.ylab('Stationary shopping expense\n[Mio. CHF]')
     + gg.xlab('Date')

     + gg.ggtitle('Overview of stationary shopping expense', )
     )
p

# %%
pdat[V.COL_TOPIC].unique()

# %%
V.COL_TOPIC_EDU = 'Bildung'

p = (pdat
     .query(f'{V.COL_TOPIC} in {[V.COL_TOPIC_EDU]}')
     >>
     gg.ggplot(gg.aes(x=V.COL_DATE, y=V.COL_VALUE_NORM, color=V.COL_DAYOFWEEK, shape=V.COL_ISWEEKDAY))
     + gg.facet_grid(f'label~.', scales='free'
                     )
     + gg.geom_vline(color='gray', linetype=':',
                     xintercept=[pd.to_datetime(f'2020-{m}-25') for m in range(1, 13)])
     + gg.geom_vline(linetype='-', color='b', xintercept=C.days_intervention,
                     alpha=0.7)
     + gg.geom_line(gg.aes(group=[V.COL_WEEK]))
     + gg.geom_point(size=1.5)
     + gg.scale_color_cmap_d('Dark2')
     # + gg.scale_color_brewer(type='qual',palette=2)

     + gg.theme_minimal()
     + gg.theme(axis_text_x=gg.element_text(angle=90, hjust=1),
                figure_size=(8, 4),
                strip_text_y=gg.element_text(angle=0, ha='left'),
                strip_margin_x=22,
                #   legend_position='left'
                )

     + gg.scale_x_date(limits=[pdat[V.COL_DATE].min(), pdat[V.COL_DATE].max()],
                       breaks=pd.date_range(C.day_start, pdat[V.COL_DATE].max(), freq='W-MON'))
     + gg.scale_y_log10()
     + gg.ylab('Relative online training')
     + gg.xlab('Date')
     + gg.ggtitle('Overview of online training\nnormalized by calendar week average')
     )
p

# %% [markdown]
# My conda environment

# %%
import sys

# %%
# !conda env export -p {sys.prefix}

# %%

# %%

# %%

# %%

# %%
