import pandas as pd
import numpy as np
import xarray as xr
import pytest
from pysimdeum.tools.helper import _create_data

def setUp():
        # Mocking inputproperty for testing
        class MockInputProperty:
            def __init__(self, consumption, users):
                self.consumption = consumption
                self.users = users
        
        # Mocking consumption data
        time = pd.date_range(start='2024-01-01', periods=10, freq='H')
        patterns = ['pattern1', 'pattern2']
        users = ['user1', 'user2']
        data = np.random.rand(10, 2, 2, 2, 2)
        consumption = xr.DataArray(data, dims=('time', 'user', 'enduse', 'patterns', 'flowtypes'), 
                                    coords={'time': time, 'user': users, 'enduse': range(2),
                                            'patterns': patterns, 'flowtypes': ['totalflow', 'hotflow']})
        return MockInputProperty(consumption, users)
    
def test_create_data():
    # Call the function with the mocked inputproperty
    input = setUp()
    appliance_data, total_water_usage, total_users, total_number_of_days, total_patterns = _create_data(input)
    
    # Assertions for total water usage
    expected_total_water_usage = np.sum(input.consumption.sel(flowtypes='totalflow').values)
    assert pytest.approx(total_water_usage) == expected_total_water_usage

    # Assertions for total patterns
    expected_total_patterns = len(input.consumption.patterns)
    assert total_patterns == expected_total_patterns

    # Assertions for total users
    expected_total_users = len(input.users)
    assert total_users == expected_total_users

    # Assertions for appliance data
    expected_appliance_data_total = input.consumption.sel(flowtypes='totalflow').sum('user').sum('time').sum('patterns').to_dataframe('total')
    expected_appliance_data_total['percentage'] = (expected_appliance_data_total['total']/total_water_usage)*100
    expected_appliance_data_total['pp'] = expected_appliance_data_total['total']/total_users
    expected_appliance_data_total['pppd'] = (expected_appliance_data_total['pp']/total_patterns)/total_number_of_days
    
    pd.testing.assert_frame_equal(appliance_data, expected_appliance_data_total)

    # Assertions for total number of days
    expected_number_of_seconds = len(input.consumption)
    expected_total_number_of_days = expected_number_of_seconds/(60*60*24)
    assert pytest.approx(total_number_of_days) == expected_total_number_of_days