import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 

from pySIMDEUM.core.house import House, Property

def plot_diurnal_pattern(statistics):

    # plot a diurnal pattern based on statistics object
    # after plot_diurnal_pattern.m
    # 
    # Input: statistics object

    diurnal_pattern = __create_diurnal_pattern(statistics)
    

    plt.plot(diurnal_pattern.index, diurnal_pattern.values)
    plt.show()

def view_statistics(statistics):
    # make several plots to quickly get an overview of the statistics
    #
    # Input: statistics object
    # household stats pie graph
    data = []
    text = []
    for key in statistics.household.keys():
        temptext = []
        temptext.append(key + ': ' + str(statistics.household[key]['households']) + '\n')
        data.append(statistics.household[key]['households'])
        for key2 in statistics.household[key]['division_gender'].keys():
            temptext.append(key2 + ': ' + str(statistics.household[key]['division_gender'][key2]) + ' ')
        temptext.append('\n')
        for key3 in statistics.household[key]['division_age'].keys():
            temptext.append(key3 + ': ' + str(statistics.household[key]['division_age'][key3]) + ' ')
        temptext.append('\n')
        for key4 in statistics.household[key]['job'].keys():
            temptext.append(key4 + ': ' + str(statistics.household[key]['job'][key4]) + ' ')
        temptext.append('\n')
        text.append(''.join(temptext))

    create_pie_fig(data, text, 'household statistics and home presence settings')

    # home presence table
    rows = []
    cell_text= []
    for key in statistics.diurnal_pattern['child'].keys():
        for key2 in statistics.diurnal_pattern['child'][key].keys():
            rows.append(key + '-' + key2)
    columns= list(statistics.diurnal_pattern.keys())
    for key in statistics.diurnal_pattern['child'].keys():
        for key2 in statistics.diurnal_pattern['child'][key].keys():
            temp_text = []
            width = []
            for column in columns:
                temp_text.append(statistics.diurnal_pattern[column][key][key2])
                width.append(0.4)
            cell_text.append(temp_text)
    the_table = plt.table(cellText=cell_text, cellLoc='center', rowLabels=rows, colLabels=columns, colWidths=width,
                      loc='bottom')
    plt.subplots_adjust(bottom=0.45)
    plt.show()


def get_max_time_diurnal_pattern(statistics):

    # get the time of maximum usage form a statistics object
    # meant for automatic testing
    #
    # Input: statistics object
    # Output: timedelta of moment of maximum usage days, HH:MM:SS
    
    diurnal_pattern = __create_diurnal_pattern(statistics)
    return diurnal_pattern.idxmax()

def __create_diurnal_pattern(statistics):
    num_sim = 1000
    time = pd.timedelta_range(start='00:00:00', end='23:59:59', freq='1S')
    diurnal_pattern = pd.Series(index=time).fillna(0)

    for i in range(num_sim):
        prop = Property(statistics=statistics)
        house = prop.built_house()
        house.populate_house()

        for user in house.users:
            presence = user.compute_presence(weekday=True, statistics=statistics)
            presence = presence.fillna(0)
            diurnal_pattern = diurnal_pattern + presence
    return diurnal_pattern

def create_pie_fig(data, text, title):
    fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))


    wedges, texts = ax.pie(data, wedgeprops=dict(width=0.7), startangle=-80)

    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"),
            bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(text[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
                    horizontalalignment=horizontalalignment, **kw)

    ax.set_title(title)

    