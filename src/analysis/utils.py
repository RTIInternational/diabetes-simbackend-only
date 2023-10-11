import pandas as pd


def tally_events(df, event):
    """
    Sum a grouped column

    :param df: Initial DataFrame
    :param event: Name of column to be unfurled
    :return: Unfurled dataframe
    """
    return df.groupby(['step'])[event].sum()


def unfurl_and_tally_events(df, event):
    """
    Unpack and tally a dataframe column

    :param df: Initial DataFrame
    :param event: Name of column to be unfurled
    :return: Unfurled dataframe
    """
    return tally_events(unfurl_events(df, event), event)


def unfurl_events(df, event):
    """
    Unpack a nested list by converting each entry to a DataFrame row.

    :param df: Initial DataFrame
    :param event: Name of column to be unfurled
    :return: Unfurled dataframe
    """
    rows = []

    def _apply(row):
        for i, b in enumerate(row[event]):
            # Data stored at index 0 is baseline, before conducting the simulation.
            # Since analysis is only concerned with data coming from the simulation,
            # we skip this baseline value.
            if i == 0:
                continue
            if event == 'qaly':
                rows.append([i, b])
            else:
                rows.append([i, int(b)])

    df.apply(_apply, axis=1)

    return pd.DataFrame(rows, columns=['step', event])
