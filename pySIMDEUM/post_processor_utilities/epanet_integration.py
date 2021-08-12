import wntr
import random
import numpy as np

def write_simdeum_patterns_to_epanet(houses, inpfile, timestep, number_of_patterns_dict, basic_patname):
    """write_simdeum_patterns_to_epanet will write paterns form houses to a provided epanet inp file
    Input:
    houses: a list of one or more houses, these do not have to be simulated yet, the routine will do this anyway
    inpfile: the epanet file the patterns need to be written to
    timestep: timestep in s. this might cause resampling, for now this has to be the same as the timestep in the inp file. This is not checked!
    basic_patname: the name the patterns will get in the epanet file. in case of mre patterns numbers will be assigned
    This routine uses wntr to read and manipulate the epanet inp file
    """
    wn = wntr.network.WaterNetworkModel(inpfile)
    numberofnodes = wn.num_junctions
    numberofpatterns = wn.num_patterns
    node_names = wn.node_name_list

    if len(houses) < numberofpatterns:
        print('Not enough houses. Epanet file requires %s patterns' %(str(numberofpatterns)))
    
    #for now you have to know what the timestep of the inp file is
    wn.options.time.duration = 24*3600
    wn.options.time.hydraulic_timestep = timestep
    wn.options.time.pattern_timestep = timestep
    wn.options.time.report_timestep = timestep
    wn.options.time.quality_timestep = timestep

    # basic units for simdeum are L/s in wntr everything is stored in SI units so m3/s
    flow_conv = 1/1e3
    houses_to_choose_from = houses[:] #trick to make a copy of the values and not just the reference
    patternnumber = 0
    for junction_name, junction in wn.junctions():
        try:
            num_pats = number_of_patterns_dict[junction_name]
        except:
            num_pats = 0
        if num_pats != 0:
            random_houses = random.choices(houses_to_choose_from, k=num_pats)
            for house in random_houses:
                houses_to_choose_from.remove(house)
            #for now we simulate the houses the amoutn of times needed.
            house.simulate()
            totpattern = house.consumption.sum('user').sum('enduse').values
            for i in range(1, num_pats): #skip first
                house.simulate()
                pattern = house.consumption.sum('user').sum('enduse').values
                totpattern = totpattern + pattern
            timereducedpattern = np.add.reduceat(totpattern, np.arange(0, len(totpattern), int(86400/timestep)))
            convertedpattern = timereducedpattern*flow_conv
            name = basic_patname + str(patternnumber)
            wn.add_pattern(name, convertedpattern)
            junction.add_demand(base=1.0/3600, pattern_name=name, category='simdeum_pattern') #we want 1 but because file is in CMH (hardcoded for now)
            #reshuffle order of demands there is probably an easier method
            temp = junction.demand_timeseries_list[len(junction.demand_timeseries_list)-1]
            del junction.demand_timeseries_list[len(junction.demand_timeseries_list)-1] 
            junction.demand_timeseries_list.insert(0,temp)
            patternnumber = patternnumber + 1

    #output the new inp file
    wn.write_inpfile('../test_simdeumpatterns.inp')

def write_simdeum_house_to_epanet(house, input_file=None):
    """write_simdeum_house_to_epanet will write an inp file of a standard house. For now there is no seperation between warm and cold
    INPUT:
    house: the house to be written to an epanet file
    input_file: inp file of a house with mandatory junctions such as ktap, brtap, shower etc. If no file is provided the routine will create a
    standard dutch house on itsself based on Moerman et al (2013)
    OUTPUT:
    an inp file containing the individual tap patterns, either the input_file modified or a newly created one
    VERSION 1: No input file is accepted yet, always a new file will be created"""

    if input_file == None:
        house_wn = create_house_network_file()
    else:
        house_wn = wntr.network.WaterNetworkModel(input_file)
    
    timestep = 1
    house_wn.options.time.duration = 24*3600
    house_wn.options.time.hydraulic_timestep = timestep
    house_wn.options.time.pattern_timestep = timestep
    house_wn.options.time.report_timestep = timestep
    house_wn.options.time.quality_timestep = timestep
    house.simulate()
    appliances = [x.statistics['classname'] for x in house.appliances]
    for name in appliances:
        pattern = house.consumption.loc[:, :, name].sum('user').values
        #timereducedpattern = np.add.reduceat(pattern, np.arange(0, len(pattern), int(86400/timestep)))
        convertedpattern = pattern
        house_wn.add_pattern(name + '_simdeum_pattern', convertedpattern)
        try:
            junction = [x[1] for x in house_wn.junctions() if x[0] == name][0]
            junction.add_demand(base=1.0/1000, pattern_name=name + '_simdeum_pattern', category='simdeum_pattern') #we want 1 but because file is in CMH (hardcoded for now)
            #reshuffle order of demands there is probably an easier method
            temp = junction.demand_timeseries_list[len(junction.demand_timeseries_list)-1]
            del junction.demand_timeseries_list[len(junction.demand_timeseries_list)-1] 
            junction.demand_timeseries_list.insert(0,temp)
        except:
            print('warning the inp file (created or input) does not contain a junction for ' + name + ' or it is named differently. This appliance and its pattern have not been added to the inp file.')
    house_wn.write_inpfile('../house_test.inp')


def get_demand_nodes_epanet(inpfile):
    """get_demand_nodes_epanet will get all the nodes which have a demand defined in the epanet file
    INPUT:
    inpfile: the epanet input file from which to get the demand nodes
    OUTPUT:
    returns a dictionary of {nodename1 : base_demand, nodename2: basedemand ...}
    because of wntr base_demand will be in m3/s"""
    wn = wntr.network.WaterNetworkModel(inpfile)
    returndict = {}
    for junctionname, junction in wn.junctions():
        if junction.base_demand > 0:
            returndict[junctionname] = junction.base_demand
    
    return returndict

def create_house_network_file():

    wn = wntr.network.WaterNetworkModel()
    #add reservoir
    wn.add_reservoir('res', base_head=30.0, coordinates=(6676.5,2517.2))
    #add.junctions (cold water)
    wn.add_junction('1', base_demand=0, elevation=-1, coordinates=(5781.71, 3107.18)) 
    wn.add_junction('watermeter', base_demand=0, elevation=-1, coordinates=(4854.74, 3700.31)) 
    wn.add_junction('2', base_demand=0, elevation=2, coordinates=(4854.74, 4250.76)) 
    wn.add_junction('6', base_demand=0, elevation=2, coordinates=(5084.1,4373.09)) 
    wn.add_junction('7', base_demand=0, elevation=2, coordinates=(5282.5,4261.06)) 
    wn.add_junction('Wc', base_demand=1/1000, elevation=0.75, coordinates=(5282.51,4103.96)) 
    wn.add_junction('5', base_demand=0, elevation=2, coordinates=(5558.62, 4630.5)) 
    wn.add_junction('8', base_demand=0, elevation=2, coordinates=(5742.59, 4530.38)) 
    wn.add_junction('BathroomTap', base_demand=1/1000, elevation=0.8, coordinates=(5745.4, 4346.93)) 
    wn.add_junction('3', base_demand=0, elevation=2.650, coordinates=(4854.74,5412.840))
    wn.add_junction('10', base_demand=0, elevation=2.65, coordinates=(6200.31,4663.61)) 
    wn.add_junction('11', base_demand=0, elevation=2.65, coordinates=(6766.06, 4923.5)) 
    wn.add_junction('12', base_demand=0, elevation=1, coordinates=(6766.06, 4159.02)) 
    wn.add_junction('13', base_demand=0, elevation=1, coordinates=(7194.19,3883.79)) 
    wn.add_junction('KitchenTap', base_demand=1/1000, elevation=0.8, coordinates=(7194.19,3639.14)) 
    wn.add_junction('15', base_demand=0, elevation=1, coordinates=(7438.84, 3730.89)) 
    wn.add_junction('Dishwasher', base_demand=1/1000, elevation=0.5, coordinates=(7438.84,3318.04)) 
    wn.add_junction('4', base_demand=0, elevation=2.9, coordinates=(4854.74,5657.49)) 
    wn.add_junction('24', base_demand=0, elevation=3.65, coordinates=(4854.74, 6207.95)) 
    wn.add_junction('Wc_2', base_demand=1/1000, elevation=3.65, coordinates=(4304.28, 5963.3)) #Does not yet work
    wn.add_junction('25', base_demand=0, elevation=4, coordinates=(4856.09, 6471.7)) 
    wn.add_junction('28', base_demand=0, elevation=4, coordinates=(5967.02, 6954.23)) 
    wn.add_junction('31', base_demand=0, elevation=4, coordinates=(6460.24, 6681.96)) 
    wn.add_junction('Shower', base_demand=1/1000, elevation=3.9, coordinates=(6460.24, 6483.18)) 
    wn.add_junction('29', base_demand=0, elevation=4, coordinates=(6964.83, 6391.44)) 
    wn.add_junction('BathroomTap_2', base_demand=1/1000, elevation=3.7, coordinates=(6964.83, 6085.63)) #does not yet work
    wn.add_junction('40', base_demand=0, elevation=5.58, coordinates=(4854.74, 8058.1)) 
    wn.add_junction('14', base_demand=0, elevation=5.78, coordinates=(4856.09, 8278.37)) 
    wn.add_junction('43', base_demand=0, elevation=6.28, coordinates=(4854.74, 8577.98)) 
    wn.add_junction('WashingMachine', base_demand=1/1000, elevation=6.28, coordinates=(4291.24, 8313.9)) 
    #add pipes (cold water)
    wn.add_pipe('1', 'watermeter', '2', length=2, diameter=25/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('25', '1', 'watermeter', length=2, diameter=25/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('4', '2', '6', length=0.235, diameter=20/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('33', '1', 'res', length=1, diameter=32/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('6', '6', '7', length=0.264, diameter=16/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('7', '7', 'Wc', length=0.25, diameter=16/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('5', '6', '5', length=1.079, diameter=16/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('8', '5', '8', length=0.262, diameter=16/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('9', '8', 'BathroomTap', length=0.2, diameter=16/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('2', '3', '2', length=0.65, diameter=25/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('10', '3', '10', length=1.3075, diameter=25/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('11', '10', '11', length=1, diameter=25/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('12', '11', '12', length=1.5175, diameter=25/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('13', '12', '13', length=0.325, diameter=25/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('15', '13', 'KitchenTap', length=0.2, diameter=16/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('14', '13', '15', length=0.31, diameter=16/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('16', '15', 'Dishwasher', length=0.5, diameter=16/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('3', '4', '3', length=0.2, diameter=25/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('23', '4', '24', length=0.75, diameter=25/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('26', 'Wc_2', '24', length=0.747, diameter=16/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('24', '24', '25', length=0.35, diameter=25/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('27', '25', '28', length=0.1358, diameter=25/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('28', '28', '31', length=0.64, diameter=25/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('30', '31', 'Shower', length=0.1, diameter=16/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('29', '31', '29', length=0.76, diameter=16/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('31', '29', 'BathroomTap_2', length=0.3, diameter=16/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('49', '40', '25', length=1.58, diameter=25/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('54', '14', '40', length=0.2, diameter=25/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('53', '43', '14', length=0.5, diameter=25/1000, roughness=0.05/1000, minor_loss=0.0)
    wn.add_pipe('50', 'WashingMachine', '43', length=0.479, diameter=16/1000, roughness=0.05/1000, minor_loss=0.0)
    
    wn.options.hydraulic.headloss ="D-W"
    wn.options.hydraulic.inpfile_units="LPS"
    return wn
    
    
    