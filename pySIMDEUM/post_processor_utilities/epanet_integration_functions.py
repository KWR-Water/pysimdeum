from pySIMDEUM.post_processor_utilities.epanet_classes import *

def write_simdeum_patterns_to_epanet(houses, inpfile, timestep, basic_patname):
    """write_simdeum_patterns_to_epanet will write paterns form houses to a provided epanet inp file
    Input:
    houses: a list of one or more houses
    inpfile: the epanet file the patterns need to be written to
    timestep: timestep in s. this might cause resampling, for now this has to be the same as the timestep in the inp file. This is not checked!
    basic_patname: the name the patterns will get in the epanet file. in case of mre patterns numbers will be assigned
    This routine uses the epanetttools library: https://pypi.org/project/EPANETTOOLS/
    """

    epanet_object = Epanet_file_object()
    epanet_object.CreateFromInpFile(inpfile)

    numberofnodes = len(epanet_object.Junctions)
    numberofpatterns = len(epanet_object.Patterns)
    # get nodenames
    node_names = []
    for node in epanet_object.Junctions:
        node_names.append(node.Id)
    #check if enough houses
    if len(houses) < numberofpatterns:
        print('Not enough houses. Epanet file requires %s patterns' %(str(numberofpatterns)))
    
    #for now you have to know what the timestep of the inp file is
    minutes = timestep/60
    epanet_object.Times.Hydraulic_timestep = EpanetTime(0,minutes)
    epanet_object.Times.Pattern_timestep = EpanetTime(0,minutes)
    epanet_object.Times.Report_timestep = EpanetTime(0,minutes)
    epanet_object.Times.Quality_timestep = EpanetTime(0,60)
    epanet_object.Times.Duration = EpanetTime(24,0)

    #get units
    units = epanet_object.Options.Units
    if units == 'CFS': #cubic feet per second 
        flow_conv = 0.035314666213
    elif units == 'GPM': #gallons per minute 
         flow_conv = 0.26417205236 * 60
    elif units == 'MGD': #million gallons per day 
        flow_conv = 0.26417205236 * 60*60*24/1e6
    elif units == 'IMGD': #Imperial mgd 
        flow_conv = 0.2199692483 * 60*60*24/1e6
    elif units == 'AFD': #acre-feet per day 
        flow_conv = 8.1071319218e-7 * 60*60*24
    elif units == 'LPS': #liters per second 
        flow_conv = 1
    elif units == 'LPM': #liters per minute 
        flow_conv = 60
    elif units == 'MLD': #million liters per day 
        flow_conv = 60*60*24/1e6
    elif units == 'CMH ': #cubic meters per hour 
        flow_conv = 60*60/1e3 
    elif units == 'CMD': #cubic meters per day 
        flow_conv = 60*60*24/1e3
    test = 2
    
    