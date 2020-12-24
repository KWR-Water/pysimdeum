from  epanettools.epanettools import EPANetSimulation, Node, Link, Network, Nodes, Links, Patterns, Pattern, Controls, Control

def write_simdeum_patterns_to_epanet(houses, inpfile, timestep, basic_patname):
    """write_simdeum_patterns_to_epanet will write paterns form houses to a provided epanet inp file
    Input:
    houses: a list of one or more houses
    inpfile: the epanet file the patterns need to be written to
    timestep: timestep in s. this might cause resampling
    basic_patname: the name the patterns will get in the epanet file. in case of mre patterns numbers will be assigned
    This routine uses the epanetttools library: https://pypi.org/project/EPANETTOOLS/
    """
    es = EPANetSimulation(inpfile)
    numberofnodes = len(es.network.nodes)
    numberofpatterns = len(es.network.patterns)
    test = 2
    
    