class EpanetTime():
    def __init__(self, hours, minutes):
        self.Hours = int(hours)
        self.Minutes = int(minutes)
    
    def __str__(self):
        hours = str(self.Hours)
        minutes = str(self.Minutes)
        if len(hours) != 2:   #needed for example to turn 0:3 into 00:03
            hours = '0' + hours
        if len(minutes) != 2:
            minutes = '0' + minutes
        return hours + ':' + minutes

class Epanet_file_object():
    Title = ''
    Junctions = []
    Reservoirs = []
    Tanks = []
    Pipes = []
    Pumps = []
    Valves = []
    Tags = None
    Demands = []
    Status = []
    Patterns = []
    Curves = None
    Controls = None
    Rules = None
    Energy = None
    Emitters = None
    Quality = None
    Sources = None
    Mixing = None
    Times = None
    Report = None
    Options = None
    Coordinates = []
    Vertices = []
    Labels = None
    Backdrop = None

    def WriteInpFile(self, name):
        f = open(name + '.inp', 'w')
        #title
        f.write('[TITLE]\n')
        f.write(self.Title)
        #junctions
        f.write('[JUNCTIONS]\n')
        f.write(';ID\tElev\tDemand\tPattern\n')
        for junction in self.Junctions:
            f.write(junction.writestring())
        #reservoirs
        f.write('\n[RESERVOIRS]\n')
        f.write(';ID\tHead\tPattern\n')
        for reservoir in self.Reservoirs:
            f.write(reservoir.writestring())
        #tanks
        f.write('\n[TANKS]\n')
        f.write(';ID\tElevation\tInitLevel\tMinLevel\tMaxLevel\tDiameter\tMinVol\tVolCurve\n')
        for tank in self.Tanks:
            f.write(tank.writestring())
        #pipes
        f.write('\n[PIPES]\n')
        f.write(';ID\tNode1\tNode2\tLength\tDiameter\tRoughness\tMinorLoss\tStatus\n')
        for pipe in self.Pipes:
            f.write(pipe.writestring())
        #pumps
        f.write('\n[PUMPS]\n')
        f.write(';ID\tNode1\tNode2\tParameters\n')
        for pump in self.Pumps:
            f.write(pump.writestring())
        #valves
        f.write('\n[VALVES]\n')
        f.write(';ID\tNode1\tNode2\tDiameter\tType\tSetting\tMinorLoss\n')
        for valve in self.Valves:
            f.write(valve.writestring())
        #tags
        f.write('\n[TAGS]\n')
        f.write('' if self.Tags == None else self.Tags.writestring())
        #demands
        f.write('\n[DEMANDS]\n')
        f.write(';Junction\tDemand\tPattern\tCategory\n')
        for demand in self.Demands:
            f.write(demand.writestring())
        #status
        f.write('\n[STATUS]\n')
        f.write(';ID\tStatus/Setting\n')
        for status in self.Status:
            f.write(status.writestring())
        #patterns
        f.write('\n[PATTERNS]\n')
        f.write(';ID\tMultipliers')
        for pattern in self.Patterns:
            f.write('\n;\n')
            f.write(pattern.writestring())
        f.write('\n')
        #curves 
        f.write('\n[CURVES]\n')
        f.write('' if self.Curves == None else self.Curves.writestring())
        #controls
        f.write('\n[CONTROLS]\n')
        f.write('' if self.Controls == None else self.Controls.writestring())
        #Rules
        f.write('\n[RULES]\n')
        f.write('' if self.Rules == None else self.Rules.writestring())
        #energy
        f.write('\n[ENERGY]\n')
        f.write('' if self.Energy == None else self.Energy.writestring())
        #emitters
        f.write('\n[EMITTERS]\n')
        f.write('' if self.Emitters == None else self.Emitters.writestring())
        #quality
        f.write('\n[QUALITY]\n')
        f.write('' if self.Quality == None else self.Quality.writestring())
        #sources
        f.write('\n[SOURCES]\n')
        f.write('' if self.Sources == None else self.Sources.writestring())
        # reactions ommited TODO see if this works for now
        #mixing
        f.write('\n[MIXING]\n')
        f.write('' if self.Mixing == None else self.Mixing.writestring())
        #times
        f.write('\n[TIMES]\n')
        f.write(self.Times.writestring())
        #report
        f.write('\n[REPORT]\n')
        f.write(self.Report.writestring())
        #options
        f.write('\n[OPTIONS]\n')
        f.write(self.Options.writestring())
        #coordinates
        f.write('\n[COORDINATES]\n')
        f.write(';Node\tX-Coord\tY-Coord\n')
        for coordinate in self.Coordinates:
            f.write(coordinate.writestring())
        #coordinates
        f.write('\n[VERTICES]\n')
        f.write(';Link\tX-Coord\tY-Coord\n')
        for vertice in self.Vertices:
            f.write(vertice.writestring())
        #labels
        f.write('\n[LABELS]\n')
        f.write('' if self.Labels == None else self.Labels.writestring())
        #backdrop
        f.write('\n[BACKDROP]\n')
        f.write('' if self.Backdrop == None else self.Backdrop.writestring())
        f.write('\n\n[END]\n')
        f.close()


    def CreateFromInpFile(self, inpfile):
        title_lines = False
        junction_lines = False
        reservoir_lines = False
        tank_lines = False
        pipe_lines = False
        pump_lines = False
        valve_lines= False
        tag_lines = False
        demand_lines = False
        status_lines = False
        pattern_lines = False
        curve_lines = False
        control_lines = False
        rule_lines = False
        energy_lines = False
        emitter_lines = False
        quality_lines = False
        source_lines = False
        mixing_lines = False
        time_lines = False
        report_lines = False
        option_lines = False
        coordinate_lines = False
        vertice_lines = False
        label_lines = False
        backdrop_lines = False
        text = ''
        f = open(inpfile)
        lines = f.readlines()
        for line in lines:
            #save title
            if title_lines:
                if '[' not in line:
                    self.Title += line
                else:
                    title_lines = False
            if '[TITLE]' in line:
                title_lines = True
            #save junctions
            if junction_lines:
                if ';ID' not in line and '[' not in line and line != '\n':
                    values = line.split('\t')
                    id = values[0].strip()
                    elevation = 0.0 if values[1].strip() == '' else float(values[1].strip())
                    demand = 0.0 if values[2].strip() == '' else float(values[2].strip())
                    pattern = values[3].strip()
                    comment = values[4].strip()
                    self.Junctions.append(Junction(Id=id, Elevation=elevation, Demand=demand, Pattern=pattern, Comment=comment))
                elif '[' in line:
                    junction_lines = False
            if '[JUNCTIONS]' in line:
                junction_lines = True
            # save reservoirs
            if reservoir_lines:
                if ';ID' not in line and '[' not in line and line != '\n':
                    values = line.split('\t')
                    id = values[0].strip()
                    head = 0.0 if values[1].strip() == '' else float(values[1].strip())
                    pattern = values[2].strip()
                    comment = values[3].strip()
                    self.Reservoirs.append(Reservoir(Id=id, Head=head, Pattern=pattern, Comment=comment))
                elif '[' in line:
                    reservoir_lines = False
            if '[RESERVOIRS]' in line:
                reservoir_lines = True
            # save tanks
            if tank_lines:
                if ';ID' not in line and '[' not in line and line != '\n':
                    values = line.split('\t')
                    id = values[0].strip()
                    elevation = 0.0 if values[1].strip() == '' else float(values[1].strip())
                    initlevel = 0.0 if values[2].strip() == '' else float(values[2].strip())
                    minlevel = 0.0 if values[3].strip() == '' else float(values[3].strip())
                    maxlevel = 0.0 if values[4].strip() == '' else float(values[4].strip())
                    diameter = 0.0 if values[5].strip() == '' else float(values[5].strip())
                    minvol = 0.0 if values[6].strip() == '' else float(values[6].strip())
                    volcurve = values[7].strip()
                    self.Tanks.append(Tank(Id=id, Elevation=elevation, InitLevel=initlevel, MinLevel=minlevel, MaxLevel=maxlevel,
                                         Diameter=diameter, MinVol=minvol, VolCurve=volcurve, Comment=comment))
                elif '[' in line:
                    tank_lines = False
            if '[TANKS]' in line:
                tank_lines = True
            # save pipes
            if pipe_lines:
                if ';ID' not in line and '[' not in line and line != '\n':
                    values = line.split('\t')
                    id = values[0].strip()
                    node1 = values[1].strip()
                    node2 = values[2].strip()
                    length = 0.0 if values[3].strip() == '' else float(values[3].strip())
                    diameter = 0.0 if values[4].strip() == '' else float(values[4].strip())
                    roughness = 0.0 if values[5].strip() == '' else float(values[5].strip())
                    minorloss = 0.0 if values[6].strip() == '' else float(values[6].strip())
                    status = values[7].strip()
                    comment = values[8].strip()
                    self.Pipes.append(Pipe(Id=id, Node1=node1, Node2=node2, Length=length, Diameter=diameter, Roughness=roughness, 
                                            MinorLoss=minorloss, Status=status, Comment=comment))
                elif '[' in line:
                    pipe_lines = False
            if '[PIPES]' in line:
                pipe_lines = True
            # save pumps
            if pump_lines:
                if ';ID' not in line and '[' not in line and line != '\n':
                    values = line.split('\t')
                    id = values[0].strip()
                    node1 = values[1].strip()
                    node2 = values[2].strip()
                    parameters = values[3].strip() #assumption that parameter is a string
                    comment = values[4].strip()
                    self.Pumps.append(Pump(Id=id, Node1=node1, Node2=node2, Parameters=parameters, Comment=comment))
                elif '[' in line:
                    pump_lines = False
            if '[PUMPS]' in line:
                pump_lines = True
            # save valves
            if valve_lines:
                if ';ID' not in line and '[' not in line and line != '\n':
                    values = line.split('\t')
                    id = values[0].strip()
                    node1 = values[1].strip()
                    node2 = values[2].strip()
                    diameter = 0.0 if values[3].strip() == '' else float(values[3].strip())
                    type_valve = values[4].strip()
                    setting = 0.0 if values[5].strip() == '' else float(values[5].strip())
                    minorloss = 0.0 if values[6].strip() == '' else float(values[6].strip())
                    comment = values[7].strip()
                    self.Valves.append(Valve(Id=id, Node1=node1, Node2=node2, Diameter=diameter, Type=type_valve, Setting=setting, MinorLoss=minorloss, Comment=comment))
                elif '[' in line:
                    valve_lines = False
            if '[VALVES]' in line:
                valve_lines = True
            # save tags
            if tag_lines:
                if  '[' not in line and line != '\n':
                    text += line
                elif '[' in line:
                    self.Tag = Tag(text=text)
                    text = ''
                    tag_lines = False
            if '[TAGS]' in line:
                tag_lines = True
            # save demands
            if demand_lines:
                if ';Junction' not in line and '[' not in line and line != '\n':
                    values = line.split('\t')
                    junction = values[0].strip()
                    demand = 0.0 if values[1].strip() == '' else float(values[1].strip())
                    pattern = values[2].strip()
                    category = values[3].strip()
                    self.Demands.append(Demand(Junction=junction, Demand=demand, Pattern=pattern, Category=category))
                elif '[' in line:
                    demand_lines = False
            if '[DEMANDS]' in line:
                demand_lines = True
            # save status
            if status_lines:
                if ';ID' not in line and '[' not in line and line != '\n':
                    values = line.split('\t')
                    id = values[0].strip()
                    status = values[1].strip()
                    self.Status.append(Status(Id=id, Status=status))
                elif '[' in line:
                    status_lines = False
            if '[STATUS]' in line:
                status_lines = True
            # save patterns
            if pattern_lines:
                if line.strip() == ';': # new pattern
                    if len(pattern_values) != 0:
                        self.Patterns.append(Pattern(Id=id, Multipliers=pattern_values))
                    new_pattern = True
                    pattern_values = []
                    id = ''
                elif '[' in line:
                    self.Patterns.append(Pattern(Id=id, Multipliers=pattern_values))
                    pattern_lines = False
                elif ';ID' not in line and line != '\n':
                    values = line.split('\t')
                    id = values[0].strip()
                    for x in range(len(values)-1): # we already allocated the first one
                        pattern_values.append(float(values[x+1].strip()))
            if '[PATTERNS]' in line:
                pattern_lines = True
                pattern_values= []
            # save curves
            if curve_lines:
                if  '[' not in line and line != '\n':
                    text += line
                    self.Curves = Curves(text=text)
                elif '[' in line:
                    curve_lines = False
            if '[CURVES]' in line:
                curve_lines = True
            # save controls
            if control_lines:
                if  '[' not in line and line != '\n':
                    text += line 
                elif '[' in line:
                    self.Control = Controls(text=text)
                    text = ''
                    control_lines = False
            if '[CONTROLS]' in line:
                control_lines = True
            # save Rules
            if rule_lines:
                if  '[' not in line and line != '\n':
                    text += line
                elif '[' in line:
                    self.Rules = Rules(text=text)
                    text = ''
                    rule_lines = False
            if '[RULES]' in line:
                rule_lines = True
            # save energy
            if energy_lines:
                if  '[' not in line and line != '\n':
                    text += line
                elif '[' in line:
                    self.Energy = Energy(text=text)
                    text = ''
                    energy_lines = False
            if '[ENERGY]' in line:
                energy_lines = True
            # save emitters
            if emitter_lines:
                if  '[' not in line and line != '\n':
                    text += line
                elif '[' in line:
                    self.Emitters = Emiters(text=text)
                    text = ''
                    emitter_lines = False
            if '[EMITTERS]' in line:
                emitter_lines = True
            # save quality
            if quality_lines:
                if  '[' not in line and line != '\n':
                    text += line
                elif '[' in line:
                    self.Quality = Quality(text=text)
                    text = ''
                    quality_lines = False
            if '[QUALITY]' in line:
                quality_lines = True
            # save sources
            if source_lines:
                if  '[' not in line and line != '\n':
                    text += line
                elif '[' in line:
                    self.Sources = Source(text=text)
                    text = ''
                    source_lines = False
            if '[SOURCES]' in line:
                source_lines = True
            # skip [REACTIONS] TODO how do we differentiate between the two differernt headings?
            # save mixing
            if mixing_lines:
                if  '[' not in line and line != '\n':
                    text += line
                elif '[' in line:
                    self.Mixing = Mixing(text=text)
                    text = ''
                    mixing_lines = False
            if '[MIXING]' in line:
                mixing_lines = True
            # save times
            if time_lines:
                if  '[' not in line and line != '\n':
                    values = line.split('\t')
                    if values[0].strip() == 'Duration': #TODO assume a format of 00:00
                        hours = float(values[1].strip().split(':')[0])
                        minutes = float(values[1].strip().split(':')[1])
                        duration = EpanetTime(hours, minutes)
                    elif values[0].strip() == 'Hydraulic Timestep':
                        hours = float(values[1].strip().split(':')[0])
                        minutes = float(values[1].strip().split(':')[1])
                        hydraulic_timestep = EpanetTime(hours, minutes)
                    elif values[0].strip() == 'Quality Timestep':
                        hours = float(values[1].strip().split(':')[0])
                        minutes = float(values[1].strip().split(':')[1])
                        quality_timestep = EpanetTime(hours, minutes)
                    elif values[0].strip() == 'Pattern Timestep':
                        hours = float(values[1].strip().split(':')[0])
                        minutes = float(values[1].strip().split(':')[1])
                        pattern_timestep = EpanetTime(hours, minutes)
                    elif values[0].strip() == 'Pattern Start':
                        hours = float(values[1].strip().split(':')[0])
                        minutes = float(values[1].strip().split(':')[1])
                        pattern_start = EpanetTime(hours, minutes)
                    elif values[0].strip() == 'Report Timestep':
                        hours = float(values[1].strip().split(':')[0])
                        minutes = float(values[1].strip().split(':')[1])
                        report_timestep = EpanetTime(hours, minutes)
                    elif values[0].strip() == 'Report Start':
                        hours = float(values[1].strip().split(':')[0])
                        minutes = float(values[1].strip().split(':')[1])
                        report_start = EpanetTime(hours, minutes)
                    elif values[0].strip() == 'Start ClockTime': #TODO should be some form of time as well
                        start_clocktime = values[1].strip()
                    elif values[0].strip() == 'Statistic':
                        statistic = values[1].strip()
                elif '[' in line:
                    self.Times = Time_settings(Duration=duration, Hydraulic_timestep=hydraulic_timestep, Quality_timestep=quality_timestep
                                            , Pattern_timestep=pattern_timestep, Pattern_start=pattern_start, Report_timestep=report_timestep,
                                            Report_start=report_start, Start_clocktime=start_clocktime, Statistic=statistic)
                    time_lines = False
            if '[TIMES]' in line:
                time_lines = True
            # save report settings
            if report_lines:
                if  '[' not in line and line != '\n':
                    values = line.split('\t')
                    if values[0].strip() == 'Status':
                        status = values[1].strip()
                    elif values[0].strip() == 'Summary':
                        summary = values[1].strip()
                    elif values[0].strip() == 'Page':
                        page = float(values[1].strip())         
                elif '[' in line:
                    self.Report = Report_settings(Summary=summary, Status=status, Page=page)
                    report_lines = False
            if '[REPORT]' in line:
                report_lines = True
            # save options
            if option_lines:
                if  '[' not in line and line != '\n':
                    values = line.split('\t')
                    if values[0].strip() == 'Units':
                        units = values[1].strip()
                    elif values[0].strip() == 'Headloss':
                        headloss = values[1].strip()
                    elif values[0].strip() == 'Specific Gravity':
                        specific_gravity = float(values[1].strip())
                    elif values[0].strip() == 'Viscosity':
                        viscosity = float(values[1].strip())
                    elif values[0].strip() == 'Trials':
                        trials = float(values[1].strip())
                    elif values[0].strip() == 'Accuracy':
                        accuracy = float(values[1].strip())
                    elif values[0].strip() == 'CHECKFREQ':
                        checkfreq = float(values[1].strip())
                    elif values[0].strip() == 'MAXCHECK':
                        maxcheck = float(values[1].strip())
                    elif values[0].strip() == 'DAMPLIMIT':
                        damplimit = float(values[1].strip())
                    elif values[0].strip() == 'Unbalanced':
                        unbalanced = values[1].strip()
                    elif values[0].strip() == 'Pattern':
                        pattern = values[1].strip()
                    elif values[0].strip() == 'Demand Multiplier':
                        demand_multiplier = float(values[1].strip())
                    elif values[0].strip() == 'Emitter Exponent':
                        emitter_exponent = float(values[1].strip())
                    elif values[0].strip() == 'Quality':
                        quality = values[1].strip()
                    elif values[0].strip() == 'Diffusivity':
                        diffusivity = float(values[1].strip())
                    elif values[0].strip() == 'Tolerance':
                        tolerance = float(values[1].strip())      
                elif '[' in line:
                    self.Options = Options(Units=units, Headloss=headloss, Specific_gravity=specific_gravity, Viscosity=viscosity, Trials=trials,
                                           Accuracy=accuracy, Checkfreq=checkfreq, Maxcheck=maxcheck, Damplimit=damplimit, Unbalanced=unbalanced, Pattern=pattern,
                                           Demand_multiplier=demand_multiplier, Emitter_exponent=emitter_exponent, Quality=quality, Diffusivity=diffusivity, 
                                           Tolerance=tolerance)
                    option_lines = False
            if '[OPTIONS]' in line:
                option_lines = True
            # save coordinates
            if coordinate_lines:
                if ';Node' not in line and '[' not in line and line != '\n':
                    values = line.split('\t')
                    node = values[0].strip()
                    xcoord = 0.0 if values[1].strip() == '' else float(values[1].strip())
                    ycoord = 0.0 if values[2].strip() == '' else float(values[2].strip())
                    self.Coordinates.append(Coordinate(Node=node, X_coord=xcoord, Y_coord=ycoord))
                elif '[' in line:
                    coordinate_lines = False
            if '[COORDINATES]' in line:
                coordinate_lines = True
            # save coordinates
            if vertice_lines:
                if ';Link' not in line and '[' not in line and line != '\n':
                    values = line.split('\t')
                    link = values[0].strip()
                    xcoord = 0.0 if values[1].strip() == '' else float(values[1].strip())
                    ycoord = 0.0 if values[2].strip() == '' else float(values[2].strip())
                    self.Vertices.append(Vertice(Link=link, X_coord=xcoord, Y_coord=ycoord))
                elif '[' in line:
                    vertice_lines = False
            if '[VERTICES]' in line:
                vertice_lines = True
            # save labels
            if label_lines:
                if  '[' not in line and line != '\n':
                    text += line
                elif '[' in line:
                    self.Labels = Labels(text=text)
                    text = ''
                    label_lines = False
            if '[LABELS]' in line:
                label_lines = True
            # save backdrop
            if backdrop_lines:
                if  '[' not in line and line != '\n':
                    text += line
                elif '[' in line:
                    self.Backdrop = Backdrop(text=text)
                    text = ''
                    backdrop_lines = False
            if '[BACKDROP]' in line:
                backdrop_lines = True

    

class Junction():
    def __init__(self, Id="", Elevation=0.0, Demand=0.0, Pattern="", Comment=""):
        self.Id = Id
        self.Elevation = Elevation
        self.Demand = Demand
        self.Pattern = Pattern
        self.Comment = Comment
    
    def writestring(self):
        line = self.Id + '\t' + str(self.Elevation) + '\t' + str(self.Demand) + '\t' + self.Pattern + '\t' + self.Comment + '\n'
        return line

class Reservoir():
    def __init__(self, Id='', Head=0.0, Pattern='', Comment=''):
        self.Id =Id
        self.Head = Head
        self.Pattern = Pattern
        self.Comment = Comment
    
    def writestring(self):
        line = self.Id + '\t' + str(self.Head) + '\t' + self.Pattern + '\t' + self.Comment + '\n'
        return line

class Tank():
    def __init__(self, Id='', Elevation=0.0, InitLevel=0.0, MinLevel=0.0, MaxLevel=0.0, Diameter=0.0, MinVol=0.0, VolCurve='', Comment=''):
        self.Id = Id
        self.Elevation = Elevation
        self.InitLevel = InitLevel
        self.MinLevel = MinLevel
        self.MaxLevel = MaxLevel
        self.Diameter = Diameter
        self.MinVol = MinVol
        self.VolCurve = VolCurve
        self.Comment = Comment
    
    def writestring(self):
        line = self.Id + '\t' + str(self.Elevation) + '\t' + str(self.InitLevel) + '\t' + str(self.MinLevel) + '\t' + str(self.MaxLevel) + '\t' \
               + str(self.Diameter) + '\t' + str(self.MinVol) + '\t' + self.VolCurve + '\t' + self.Comment + '\n'
        return line


class Pipe():
    def __init__(self, Id='', Node1='', Node2='', Length=0.0, Diameter=0.0, Roughness=0.0, MinorLoss=0.0, Status='OPEN', Comment=''):
        self.Id = Id
        self.Node1 = Node1
        self.Node2 = Node2
        self.Length = Length
        self.Diameter = Diameter
        self.Roughness = Roughness
        self.MinorLoss = MinorLoss
        self.Status = Status
        self.Comment = Comment

    def writestring(self):
        line = self.Id + '\t' + self.Node1 + '\t' + self.Node2 + '\t' + str(self.Length) + '\t' + str(self.Diameter) + '\t' + str(self.Roughness) \
               + '\t' + str(self.MinorLoss) + '\t' + self.Status + '\t' + self.Comment + '\n'
        return line

class Pump():
    def __init__(self, Id='', Node1='', Node2='', Parameters='', Comment=''):
        self.Id = Id
        self.Node1 = Node1
        self.Node2 = Node2
        self.Parameters = Parameters
        self.Comment = Comment

    def writestring(self):
        line = self.Id + '\t' + self.Node1 + '\t' + self.Node2 + '\t' + self.Parameters + '\t' + self.Comment + '\n'
        return line

class Valve():
    def __init__(self, Id='', Node1='', Node2='', Diameter=0.0, Type='TCV', Setting=0.0, MinorLoss=0.0, Comment=''):
        self.Id = Id
        self.Node1 = Node1
        self.Node2 = Node2
        self.Diameter = Diameter
        self.Type = Type
        self.Setting = Setting
        self.MinorLoss = MinorLoss
        self.Comment = Comment
    
    def writestring(self):
        line = self.Id + '\t' + self.Node1 + '\t' + self.Node2 + '\t' + str(self.Diameter) + '\t' + self.Type + '\t' + str(self.Setting) + \
               '\t' + str(self.MinorLoss) + '\t' + self.Comment +'\n'
        return line

class Tag(): #TODO implement correctly, for now store literal text from file
    def __init__(self, text=''):
        self.Text = text
    
    def writestring(self):
        return self.Text + '\n'

class Demand():
    def __init__(self, Junction='', Demand=0.0, Pattern='', Category=''):
        self.Junction = Junction
        self.Demand = Demand
        self.Pattern = Pattern
        self.Category = Category
    
    def writestring(self):
        line = self.Junction + '\t' + str(self.Demand) + '\t' + self.Pattern + '\t' + self.Category + '\n'
        return line

class Status():
    def __init__(self, Id='', Status='Closed'):
        self.Id = Id
        self.Status = Status
    
    def writestring(self):
        line = self.Id + '\t' + self.Status + '\n'
        return line

class Pattern():
    def __init__(self, Id='', Multipliers=[1.0]):
        self.Id = Id
        self.Multipliers = Multipliers
    
    def writestring(self):
        count = 0
        line = ''
        for multiplier in self.Multipliers:
            if count == 0:
                line += self.Id
                line += '\t'
                line += str(multiplier)
                line += '\t'
            elif count > 0 and count < 6:
                line += str(multiplier)
                line += '\t'
            count += 1
            if count == 6:
                line += '\n'
                count = 0
        return line


class Curves(): #TODO implement correctly, for now store literal text from file
    def __init__(self, text=''):
        self.Text = text
    
    def writestring(self):
        return self.Text + '\n'

class Controls(): #TODO implement correctly, for now store literal text from file
    def __init__(self, text=''):
        self.Text = text
    
    def writestring(self):
        return self.Text + '\n'

class Rules():  #TODO implement correctly, for now store literal text from file
    def __init__(self, text=''):
        self.Text = text
    
    def writestring(self):
        return self.Text + '\n'

class Energy():  #TODO implement correctly, for now store literal text from file
    def __init__(self, text=''):
        self.Text = text
    
    def writestring(self):
        return self.Text + '\n'

class Emiters(): #TODO implement correctly, for now store literal text from file
    def __init__(self, text=''):
        self.Text = text
    
    def writestring(self):
        return self.Text + '\n'

class Quality(): #TODO implement correctly, for now store literal text from file
    def __init__(self, text=''):
        self.Text = text
    
    def writestring(self):
        return self.Text + '\n'

class Source(): #TODO implement correctly, for now store literal text from file
    def __init__(self, text=''):
        self.Text = text
    
    def writestring(self):
        return self.Text + '\n'

class Reaction(): #TODO implement correctly, for now store literal text from file
    def __init__(self, text=''):
        self.Text = text
    
    def writestring(self):
        return self.Text + '\n'

class Reaction_settings(): #TODO implement correctly, for now store literal text from file woh to differentiate this? Leave out completely
    def __init__(self, text=''):
        self.Text = text
    
    def writestring(self):
        return self.Text + '\n'

class Mixing(): #TODO implement correctly, for now store literal text from file
    def __init__(self, text=''):
        self.Text = text
    
    def writestring(self):
        return self.Text + '\n'

class Time_settings():
    def __init__(self, Duration=EpanetTime(0,0), Hydraulic_timestep=EpanetTime(0,0), Quality_timestep=EpanetTime(0,0),
                 Pattern_timestep=EpanetTime(0,0), Pattern_start=EpanetTime(0,0), Report_timestep=EpanetTime(0,0),
                 Report_start=EpanetTime(0,0), Start_clocktime='', Statistic='None'):
        self.Duration = Duration
        self.Hydraulic_timestep = Hydraulic_timestep
        self.Quality_timestep = Quality_timestep
        self.Pattern_timestep = Pattern_timestep
        self.Pattern_start = Pattern_start
        self.Report_timestep = Report_timestep
        self.Report_start = Report_start
        self.Start_clocktime = Start_clocktime
        self.Statistic = Statistic
    
    def writestring(self):
        line = 'Duration\t' + str(self.Duration) + '\n'
        line += 'Hydraulic Timestep\t' + str(self.Hydraulic_timestep) + '\n'
        line += 'Quality Timestep\t' + str(self.Quality_timestep) + '\n'
        line += 'Pattern Timestep\t' + str(self.Pattern_timestep) + '\n'
        line += 'Pattern Start\t' + str(self.Pattern_start) + '\n'
        line += 'Report Timestep\t' + str(self.Report_timestep) + '\n'
        line += 'Report Start\t' + str(self.Report_start) + '\n'
        line += 'Start ClockTime\t' + str(self.Start_clocktime) + '\n'
        line += 'Statistic\t' + self.Statistic + '\n'
        return line

class Report_settings():
    def __init__(self, Status='', Summary='', Page=0):
        self.Status = Status
        self.Summary = Summary
        self.Page = Page
    
    def writestring(self):
        line = 'Status\t' + self.Status + '\n'
        line += 'Summary\t' + self.Summary + '\n'
        line += 'Page\t' + str(self.Page) +'\n'
        return line 

class Options():
    def __init__(self, Units='LPS', Headloss='D-W', Specific_gravity=1.0, Viscosity=1.0, Trials=0, Accuracy=0.0, Checkfreq=0, Maxcheck=0, Damplimit=0.0,
                 Unbalanced='', Pattern='', Demand_multiplier=0.0, Emitter_exponent=0.0, Quality='', Diffusivity=0, Tolerance=0.0):
        self.Units = Units
        self.Headloss = Headloss
        self.Specific_gravity = Specific_gravity
        self.Viscosity = Viscosity
        self.Trials = Trials
        self.Accuracy = Accuracy
        self.Checkfreq = Checkfreq
        self.Maxcheck = Maxcheck
        self.Damplimit = Damplimit
        self.Unbalanced = Unbalanced
        self.Pattern = Pattern
        self.Demand_multiplier = Demand_multiplier
        self.Emitter_exponent = Emitter_exponent
        self.Quality = Quality
        self.Diffusivity = Diffusivity
        self.Tolerance = Tolerance
    
    def writestring(self):
        line = 'Units\t' + self.Units + '\n'
        line += 'Headloss\t' + self.Headloss + '\n'
        line += 'Specific Gravity\t' + str(self.Specific_gravity) + '\n'
        line += 'Viscosity\t' + str(self.Viscosity) + '\n'
        line += 'Trials\t' + str(self.Trials) + '\n'
        line += 'Accuracy\t' + str(self.Accuracy) + '\n'
        line += 'CHECKFREQ\t' + str(self.Checkfreq) + '\n'
        line += 'MAXCHECK\t' + str(self.Maxcheck) + '\n'
        line += 'DAMPLIMIT\t' + str(self.Damplimit) + '\n'
        line += 'Pattern\t' + self.Pattern + '\n'
        line += 'Demand Multiplier\t' + str(self.Demand_multiplier) + '\n'
        line += 'Emitter Exponent\t' + str(self.Emitter_exponent) + '\n'
        line += 'Quality\t' + self.Quality + '\n'
        line += 'Diffusivity\t' + str(self.Diffusivity) + '\n'
        line += 'Tolerance\t' + str(self.Tolerance) + '\n'
        return line

class Coordinate():
    def __init__(self, Node='', X_coord=0.0, Y_coord=0.0):
        self.Node = Node
        self.X_coord = X_coord
        self.Y_coord = Y_coord
    
    def writestring(self):
        line = self.Node + '\t' + str(self.X_coord) + '\t' + str(self.Y_coord) + '\n'
        return line

class Vertice():
    def __init__(self, Link='', X_coord=0.0, Y_coord=0.0):
        self.Link = Link
        self.X_coord = X_coord
        self.Y_coord = Y_coord
    
    def writestring(self):
        line = self.Link + '\t' + str(self.X_coord) + '\t' + str(self.Y_coord) + '\n'
        return line


class Labels(): #TODO implement correctly, for now store literal text from file
    def __init__(self, text=''):
        self.Text = text
    
    def writestring(self):
        return self.Text + '\n'

class Backdrop(): #TODO implement correctly, for now store literal text from file
    def __init__(self, text=''):
        self.Text = text
    
    def writestring(self):
        return self.Text + '\n'


