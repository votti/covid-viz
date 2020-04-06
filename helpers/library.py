import pandas as pd


def transform_daily_per_canton(df, value_cols, col_date, col_canton,
                               interpolation='linear'):
    """
    Linearily interpolates variables to get daily data.
    Input:
        df: a data frame
        value cols: columns containing the values of interest
        col_date: column name containing the dates
        col_canton: columns containing the canton/other grouping
        interpolation: how to interpolate. See help pd.DataFrame.interpolate(method=
                       set to 'None' for simple padding of values
    Returns:
        Interpolated data with daily values
    """
    df = (df
              .set_index([col_date, col_canton])
              .loc[:, value_cols]
              )
    df = (df
          .unstack(level=col_canton)
          # .pivot_table(index=col_date,
          #             values=value_cols,
          #             columns=[col_canton],observed=False)

          # Create a row for every day by reindexing
          .pipe(lambda d:
                d.reindex(
                    pd.DatetimeIndex(pd.date_range(d.index.min(), d.index.max(), freq='D'),
                                     name=col_date))))
    # return df
    if interpolation is not None:
        # If interpolation is used, interpolate betwen
        # available values.
        df = df.interpolate(method=interpolation,
                            limit_area='inside')

    df = (df
          # Pad missing values with previous day's number
          # If interpolation was used, this will pad the tail
          .fillna(method='pad')

          # Now there are only missing values at the start
          # of the series, so set them to zero
          .fillna(value=0)
          # Tidy up
          # Note:
          # I think the following should work and would
          # be way clearer - but it doesnt :(
          # .stack(level=col_canton)
          .stack(level=[0, 1]).unstack(-2)
          .reset_index()
          )
    return df


def order_cat(col, ct, rev=False):
    """
    Small helper to convert column to categorical
    with option to revert order
    """
    col = col.astype(ct)
    if rev:
        col.cat.set_categories(new_categories=ct.categories[::-1],
                               ordered=True, inplace=True)
    return col