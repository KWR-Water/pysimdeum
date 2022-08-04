import pandas as pd
from datetime import datetime

from pySIMDEUM.core.helper import create_usage_data
from pySIMDEUM.core.house import HousePattern, Property, House

def export_water_use_distribution(inputproperty, name='ApplianceWaterUse.xlsx'):
    appliance_data, total_water_usage, total_users, total_number_of_days = create_usage_data(inputproperty)
    writer = pd.ExcelWriter(name, engine = 'xlsxwriter')
    metadata = pd.DataFrame(index=['info'])
    metadata['Total number of Users'] = total_users
    metadata['Total water consumption'] = total_water_usage
    metadata['Total number of days'] = total_number_of_days
    metadata['Calculation date'] = datetime.now().date()
    appliance_data.to_excel(writer, sheet_name = 'data')
    metadata.to_excel(writer, sheet_name = 'metadata')
    writer.close()

def write_simdeum_patterns_to_xlsx(houses, timestep, Q_option, patternfile_option, output_file):
    # after writeSimdeumPatternToXls (Matlab)
    # house can eithwer be a list of filenames or a list of houses
    # timestep the output timestep of the pattern
    # Q_option for now only 'm3/h' TODO is this true? are the units not L/s?????
    # for now only 1 all patterns in 1 file
    # output_file file to write to
    
    if type(houses[0]) == str:
        count = 0
        output = pd.DataFrame()
        if '.housepattern' in houses[0]: #it are housepattern files
            for housepattern in houses:
                loadedhousepattern = HousePattern(housepattern)
                __get_housepattern_output(count, output, loadedhousepattern)
                count +=1
        else: #assumed to be house files
            for house in houses:
                prop = Property()
                loadedhouse = prop.built_house(housefile=house)
                __get_house_output(count, output, loadedhouse)
                count +=1
        summedoutput = pd.DataFrame()
        summedoutput['date'] = output['date'].values[0::timestep]
        for column in output.columns:
            if column != 'date':
                summedoutput[column] = output[column].groupby(output.index // timestep).sum().values
        summedoutput.to_excel(output_file)

    else: #.houses
        for house in houses:
            __get_house_output(count, output, loadedhouse)
        summedoutput = pd.DataFrame()
        summedoutput['date'] = output['date'].values[0::timestep]
        for column in output.columns:
            if column != 'date':
                summedoutput[column] = output[column].groupby(output.index // timestep).sum().values
        summedoutput.to_excel(output_file)

def __get_house_output(count, output, loadedhouse):
    if count == 0:
        datelist = []
        valueslist = []
        for i in range(0, len(loadedhouse.consumption.patterns)):
            datelist.extend(loadedhouse.consumption['time'].values)
            valueslist.extend(loadedhouse.consumption.sel(patterns=i).sum('user').sum('enduse').values)
        output['date'] = datelist
    else:
        valueslist = []
        for i in range(0, len(loadedhouse.consumption.patterns)):
            valueslist.extend(loadedhouse.consumption.sel(patterns=i).sum('user').sum('enduse').values)
    output['pysimdeum ' + str(count)] = valueslist

def __get_housepattern_output(count, output, loadedhousepattern):
    if count == 0:
        datelist = []
        valueslist = []
        for i in range(0, len(loadedhousepattern.consumption.patterns)):
            datelist.extend(loadedhousepattern.consumption['time'].values)
            valueslist.extend(loadedhousepattern.consumption.sel(patterns=i).values)
        output['date'] = datelist
    else:
        valueslist = []
        for i in range(0, len(loadedhousepattern.consumption.patterns)):
            valueslist.extend(loadedhousepattern.consumption.sel(patterns=i).values)
    output['pysimdeum ' + str(count)] = valueslist