
import matplotlib.pyplot as plt
import numpy as np
from typing import Union
from pysimdeum.core.statistics import Statistics

from pysimdeum.tools.helper import create_diurnal_pattern, create_usage_data
from pysimdeum.core.house import House

def plot_water_use_distribution(inputproperty: Union[list, House], plotsubject: str='percentage'):
    """Function to plot water use distribution betwee the different appliances as a pie graph [-> Axessubplot object]
    
    Args:
        inputproperty (list[House] | list[str] | House): the house or houses (either as a list of objects or paths to files) to be plotted
        plotsubject (str, optional): unit of plot, percentage, per person per day or per person default is percentage
    Returns:
        ax1 (matplotlib axessubplot): an matplotlib axes containing the plot (use plt.show() to render)
    """
    appliance_data, total_water_usage, total_users, total_number_of_days = create_usage_data(inputproperty)
    def func(pct, allvals):
        absolute = pct/100.*np.sum(allvals)
        return "{:.1f}L\n({:.1f}%)".format(absolute, pct)
    if plotsubject != 'total' and plotsubject != 'percentage' and plotsubject != 'pp' and plotsubject != 'pppd':
        print('Plotting subject not known. options are total, percentage (default), pppd (per person per day) and pp (per person)')
    else:
        labels = appliance_data.index.values
        sizes = appliance_data[plotsubject].values
        fig1, ax1 = plt.subplots()
        if plotsubject == 'percentage':
            ax1.pie(sizes, labels=labels, startangle=90, autopct='%1.1f%%')
        else:
            ax1.pie(sizes, labels=labels, startangle=90, autopct=lambda pct: func(pct, sizes))
        fig1.suptitle(plotsubject)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        return ax1

def createQcfdplot(houses: House):
    """Function to plot a cumulative flow plot [-> Axessubplot object]
    
    Args:
        houses (House): the house object to be plotted (other options not implemented yet)
    Returns:
        ax (matplotlib axessubplot): an matplotlib axes containing the plot (use plt.show() to render)
    """
    codechangepushtest = 2
    if type(houses) == House:
        n_bins = 100
        fig, ax = plt.subplots()
        x = houses.consumption.sel(patterns=0).sum('user').sum('enduse').values
        n, bins, patches = ax.hist(x, n_bins, density=True, histtype='step',
                            cumulative=True, label='Empirical')

        return ax
    else:
        # list of housefiles not implemented yet
        return None

def plot_demand(houses: House):
    """Function to plot demand. It will give four plots containing demand per user, per enduse, total of pattern 1 and all patterns/num patterns [-> figure object]
    
    Args:
        houses (House): the house object to be plotted (other options not implemented yet)
    Returns:
        fig (matplotlib figure): an matplotlib figure containing the plot (use plt.show() to render)
    """

    if type(houses) == House:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2, sharey=True)
        for user in houses.consumption.user.values:
            ax1.plot(houses.consumption['time'].values, houses.consumption.sel(user=user, patterns=0).sum('enduse').values, label=user)
        ax3.plot(houses.consumption['time'].values, houses.consumption.sel(patterns=0).sum('user').sum('enduse').values, label='total')
        for enduse in houses.consumption.enduse.values:
            ax2.plot(houses.consumption['time'].values, houses.consumption.sel(enduse=enduse, patterns=0).sum('user').values, label=enduse)
        ax4.plot(houses.consumption['time'].values, houses.consumption.sum('user').sum('enduse').sum('patterns').values/len(houses.consumption.patterns), label='average')
        ax1.legend()
        ax1.set_xlabel('time')
        ax1.set_ylabel('demand (l/s)')
        ax2.set_xlabel('time')
        ax3.legend()
        ax3.set_xlabel('time')
        ax3.set_ylabel('demand (l/s)')
        ax4.set_xlabel('time')
        ax2.legend()
        ax4.legend()
        return fig
    else:
        #list of housefiles not implemented yet
        test=2
        return None

def view_statistics(statistics: Statistics):
    """Function to plot an overview of the household statistics percentage one, two and family households for instance [-> Axessubplot object]
    
    Args:
        statistics (Statistics): the statistics object to be plotted
    Returns:
        ax (matplotlib axessubplot): an matplotlib axes containing the plot (use plt.show() to render)
    """
    
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

    ax = __create_pie_fig(data, text, 'household statistics and home presence settings')

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
    
    return ax

def plot_diurnal_pattern(statistics: Statistics):
    """Function to plot a diurnal pattern (household presence) based on statistics [-> Axessubplot object]
    
    Args:
        statistics (Statistics): the Statistics object to be plotted
    Returns:
        ax (matplotlib axessubplot): an matplotlib axes containing the plot (use plt.show() to render)
    """
    
    diurnal_pattern = create_diurnal_pattern(statistics)
    fig, ax1 = plt.subplots()

    ax1.plot(diurnal_pattern.index, diurnal_pattern.values)
    
    return ax1

def __create_pie_fig(data, text, title):
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

    return ax

