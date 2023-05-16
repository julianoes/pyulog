#! /usr/bin/env python

"""
Analyse gaps in ulog
"""

from __future__ import print_function

import argparse
import os
import pandas as pd

from .core import ULog

#pylint: disable=too-many-locals, invalid-name, consider-using-enumerate

def main():
    """Command line interface"""

    parser = argparse.ArgumentParser(description='Analyse gaps in log')
    parser.add_argument('filename', metavar='file.ulg', help='ULog input file')

    parser.add_argument('-i', '--ignore', dest='ignore', action='store_true',
                        help='Ignore string parsing exceptions', default=False)

    args = parser.parse_args()

    show_gaps(args.filename, args.ignore)


def show_gaps(ulog_file_name, disable_str_exceptions=False):
    """
    Prints the found gaps per topic.

    :param ulog_file_name: The ULog filename to open and read

    :return: None
    """

    ulog = ULog(ulog_file_name, None, disable_str_exceptions)
    data = ulog.data_list

    log_data = []

    for d in data:
        for key, entries in d.data.items():
            if key != 'timestamp':
                continue

            name = d.name + '_' + str(d.multi_id)

            for entry in entries:
                if entry == 0:
                    continue
                try:
                    stamp = pd.to_datetime(entry, unit="us")
                except Exception as e:
                    print(e)
                    continue
                log_data.append({'Timestamp': stamp, 'Topic': name})


    # ChatGPT helped me with this :)
    df = pd.DataFrame(log_data)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df = df.sort_values('Timestamp')
    max_time_diff_per_topic = df.groupby('Topic')['Timestamp'].apply(lambda x: x.diff().max())
    max_time_diff_per_topic = max_time_diff_per_topic.sort_values(ascending=False)

    pd.set_option('display.max_rows', None)
    print(max_time_diff_per_topic)

if __name__ == '__main__':
    main()
