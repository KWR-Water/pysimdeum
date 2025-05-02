import pandas as pd
from datetime import datetime
from typing import Union

from pysimdeum.tools.helper import create_usage_data
from pysimdeum.core.house import HousePattern, Property, House

def export_water_use_distribution(inputproperty: Union[list, House], name: str='ApplianceWaterUse.xlsx'):
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

def write_simdeum_patterns_to_ddg(houses: list, timestep: int, Q_option: str, patternfile_option: int, output_file: str):
    # house can be either be a list of filenames or a list of houses
    # timestep the output timestep of the pattern. minimum is 1 minute
    # Q_option for now only 'm3/h' TODO is this true? are the units not L/s?????
    # for now only 1 all patterns in 1 file
    # output_file file to write to

    output = __get_output_dataframe(houses, timestep) 
    test = 2
    

def write_simdeum_patterns_to_xlsx(houses: list, timestep: int, Q_option: str, patternfile_option: int, output_file: str):
    """Exports total water usage patterns for a list of houses to an Excel file.

    This function aggregates water usage data to the given timestep and writes to an excel file.
    Based on the total flow for each house.

    Args:
        houses (list): A list of House objects.
        timestep (int): Time resolution (in seconds) for aggregating the water usage patterns.
        Q_option (str): Specifies the flow unit. Currently, only 'm3/h' is supported.
        patternfile_option (int): Determines how many patterns are written. Currently, only the value 1
                                    is supported, which means all patterns are written to a single file.        
        output_file (str): Name of the output Excel file where the patterns will be saved.
    """    
    output = __get_output_dataframe(houses, timestep, flowtype='totalflow')
    output.to_excel(output_file)

def write_simdeum_hot_patterns_to_xlsx(houses: list, timestep: int, Q_option: str, patternfile_option: int, output_file: str):
    # after writeSimdeumPatternToXls (Matlab)
    # house can eithwer be a list of filenames or a list of houses
    # timestep the output timestep of the pattern
    # Q_option for now only 'm3/h' TODO is this true? are the units not L/s?????
    # for now only 1 all patterns in 1 file
    # output_file file to write to
    
    output = __get_output_dataframe(houses, timestep, flowtype='hotflow')
    output.to_excel(output_file)

def __get_output_dataframe(houses, timestep, flowtype):
    if type(houses[0]) == str:
        count = 0
        output = pd.DataFrame()
        if '.housepattern' in houses[0]: #it are housepattern files
            for housepattern in houses:
                loadedhousepattern = HousePattern(housepattern)
                __get_housepattern_output(count, output, loadedhousepattern, flowtype)
                count +=1
        else: #assumed to be house files
            for house in houses:
                prop = Property()
                loadedhouse = prop.built_house(housefile=house)
                __get_house_output(count, output, loadedhouse, flowtype)
                count +=1
        summedoutput = pd.DataFrame()
        summedoutput['date'] = output['date'].values[0::timestep]
        for column in output.columns:
            if column != 'date':
                summedoutput[column] = output[column].groupby(output.index // timestep).sum().values
        return summedoutput

    else: #.houses
        count = 0
        output = pd.DataFrame()
        for house in houses:
            __get_house_output(count, output, house, flowtype)
            count += 1
        summedoutput = pd.DataFrame()
        summedoutput['date'] = output['date'].values[0::timestep]
        for column in output.columns:
            if column != 'date':
                summedoutput[column] = output[column].groupby(output.index // timestep).sum().values
        return summedoutput

def __get_house_output(count, output, loadedhouse, flowtype):
    if count == 0:
        datelist = []
        valueslist = []
        for i in range(0, len(loadedhouse.consumption.patterns)):
            datelist.extend(loadedhouse.consumption['time'].values)
            valueslist.extend(loadedhouse.consumption.sel(patterns=i).sel(flowtypes=flowtype).sum('user').sum('enduse').values)
        output['date'] = datelist
    else:
        valueslist = []
        for i in range(0, len(loadedhouse.consumption.patterns)):
            valueslist.extend(loadedhouse.consumption.sel(patterns=i).sel(flowtypes=flowtype).sum('user').sum('enduse').values)
    output['pysimdeum ' + str(count)] = valueslist

def __get_housepattern_output(count, output, loadedhousepattern, flowtype):
    if count == 0:
        datelist = []
        valueslist = []
        for i in range(0, len(loadedhousepattern.consumption.patterns)):
            datelist.extend(loadedhousepattern.consumption['time'].values)
            valueslist.extend(loadedhousepattern.consumption.sel(patterns=i).sel(flowtypes=flowtype).values)
        output['date'] = datelist
    else:
        valueslist = []
        for i in range(0, len(loadedhousepattern.consumption.patterns)):
            valueslist.extend(loadedhousepattern.consumption.sel(patterns=i).sel(flowtypes=flowtype).values)
    output['pysimdeum ' + str(count)] = valueslist


def generate_infoworks_csv(subcatchment_profiles, output_dir):
    """
    Generates a CSV file for each subcatchment wastewater profile specifically formatted for InfoWorks ICM.

    Args:
        subcatchment_profiles (dict): Dictionary containing subcatchment wastewater profiles.
        output_dir (str): Directory where the CSV files will be saved.
    """
    for subcatchment_id, profile in subcatchment_profiles.items():
        # Extract the daily flow, hourly average and ww_profile
        daily_flow = profile['daily_flow']
        hourly_average = profile['hourly_average']
        ww_profile = profile['ww_profile']

        # Create a DataFrame for CALIBRATION_WEEKDAY
        calibration_weekday = []
        for hour in range(24):
            # Filter rows for the current hour
            hour_data = ww_profile[ww_profile['time'].dt.hour == hour]

            # Calculate the flow as a factor multiplier of the hourly average
            if not hour_data.empty:
                # Use the hourly average for the corresponding date
                date = hour_data['time'].dt.date.iloc[0]
                flow_factor = hour_data['flow'].sum() / hourly_average[date]
                daily_flow_value = daily_flow[date]
            else:
                flow_factor = 0
                daily_flow_value = 0

            calibration_weekday.append({
                'TIME': f"{hour:02d}:00",
                'FLOW': round(flow_factor, 2),
                'POLLUTANT': 1
            })

        calibration_weekday_df = pd.DataFrame(calibration_weekday)

        # Use the same data for CALIBRATION_WEEKEND
        calibration_weekend_df = calibration_weekday_df.copy()

        # Create a DataFrame for CALIBRATION_MONTHLY
        calibration_monthly = [
            {'MONTH': month, 'FLOW': 1, 'POLLUTANT': 1}
            for month in [
                "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
                "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"
            ]
        ]
        calibration_monthly_df = pd.DataFrame(calibration_monthly)

        # Create a DataFrame for DESIGN_PROFILES
        design_profiles = [
            {'TIME': f"{hour:02d}:00", 'FLOW': 1, 'POLLUTANT': 1}
            for hour in range(24)
        ]
        design_profiles_df = pd.DataFrame(design_profiles)

        # Write the CSV file
        csv_content = [
            "!Version=1,type=WWG,encoding=UTF8",
            "TITLE,POLLUTANT_COUNT",
            "User defined WWG item,16",
            "Units_Concentration,Units_Salt_Concentration,Units_Temperature,Units_Average_Flow",
            "mg/l,kg/m3,degC,l/day",
            "PROFILE_NUMBER,PROFILE_DESCRIPTION,FLOW",
            f"1,1 Standard Profile {round(daily_flow_value)}l/day,{round(daily_flow_value)}",
            "SEDIMENT,AVERAGE_CONCENTRATION",
            "SF1,0",
            "SF2,0",
            "POLLUTANT,DISSOLVED,SF1,SF2",
            "BOD,0,0,0",
            "COD,0,0,0",
            "TKN,0,0,0",
            "NH4,0,0,0",
            "TPH,0,0,0",
            "PL1,0,0,0",
            "PL2,0,0,0",
            "PL3,0,0,0",
            "PL4,0,0,0",
            "DO_,0,0,0",
            "NO2,0,0,0",
            "NO3,0,0,0",
            "PH_,0,0,0",
            "SAL,0,0,0",
            "TW_,0,0,0",
            "COL,0,0,0",
            "CALIBRATION_WEEKDAY",
            "TIME,FLOW,POLLUTANT"
        ]
        csv_content += calibration_weekday_df.to_csv(index=False, header=False).splitlines()

        csv_content += [
            "CALIBRATION_WEEKEND",
            "TIME,FLOW,POLLUTANT"
        ]
        csv_content += calibration_weekend_df.to_csv(index=False, header=False).splitlines()

        csv_content += [
            "CALIBRATION_MONTHLY",
            "MONTH,FLOW,POLLUTANT"
        ]
        csv_content += calibration_monthly_df.to_csv(index=False, header=False).splitlines()

        csv_content += [
            "DESIGN_PROFILES",
            "TIME,FLOW,POLLUTANT"
        ]
        csv_content += design_profiles_df.to_csv(index=False, header=False).splitlines()

        # Save the CSV file
        output_file = f"{output_dir}/{subcatchment_id}_calibration.csv"
        with open(output_file, 'w') as f:
            f.write("\n".join(csv_content))