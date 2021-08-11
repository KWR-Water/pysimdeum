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
    
    
    