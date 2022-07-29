
import sys,getopt,copy,pprint,random,os

USING_EMBER_LOAD = True

import sst
from sst.merlin import *
from loadInfo import *
from networkConfig import *
from loadFileParse import *
from paramUtils import *

debug    = 0
emberVerbose = 0
embermotifLog = ''
emberrankmapper = ''

useSimpleMemoryModel=False

statNodeList = []
jobid = 0
loadFile = ''
loadFileVars ={}
workList = []
workFlow = []
numCores = 1
numNodes = 0
nidList = ''
statsModuleName=''
statsFile='stats.csv'

platform = 'default'

paramDir='paramFiles'
netFlitSize = ''
netBW = ''
netPktSize = ''
netTopo = ''
netShape = ''
netHostsPerRtr = 1
netInspect = ''
rtrArb = ''
nicsPerNode=1

rndmPlacement = False
#rndmPlacement = True
bgPercentage = int(0)
bgMean = 1000
bgStddev = 300
bgMsgSize = 1000

detailedModelName = ""
detailedModelNodes = []
detailedModelParams = ""
simConfig = ""
platParams = ""

#yao
rting_algo= ""
stats_startat = "0us"
numVNs=1
smallCollectiveVN=-1
smallCollectiveSize=-1

qlr1 = -1
qlr2 = -1
explore = -1
qthld1 = -1
qthld2 = -1
qtable_path = ''

io_level = -1
io_thld = -1

params = {
'network': [],
'nic': [],
'ember': [],
'hermes': [],
'merlin': [],
}

motifAPI='HadesMP'

motifDefaults = {
    'cmd' : "",
    'printStats' : 0,
    'spyplotmode': 0,
}


try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["topo=", "shape=","hostsPerRtr=",
                 "simConfig=","platParams=","debug=","platform=","numNodes=",
                 "numCores=","loadFile=","loadFileVar=","cmdLine=","printStats=","randomPlacement=",
                 "emberVerbose=","netBW=","netPktSize=","netFlitSize=",
                 "rtrArb=","embermotifLog=","rankmapper=", "motifAPI=",
                 "bgPercentage=","bgMean=","bgStddev=","bgMsgSize=","netInspect=",
                 "detailedModelName=","detailedModelParams=","detailedModelNodes=",
                 "useSimpleMemoryModel","param=","paramDir=","statsModule=","statsFile=",
                #yao
                 "algoRting=", "stats_startat=", "numVNs=", "smallCollectiveVN=", "smallCollectiveSize=",
                 "qlr1=", "qlr2=", "qthld1=", "qthld2=", "explore=", "qtable_path=", "io_level=", "io_thld=",
                 ])

except getopt.GetoptError as err:
    print (str(err))
    sys.exit(2)

for o, a in opts:
    if o in ("--shape"):
        netShape = a
    elif o in ("--hostsPerRtr"):
        netHostsPerRtr = int(a)
    elif o in ("--platform"):
        platform = a
    elif o in ("--numCores"):
        numCores = a
    elif o in ("--numNodes"):
        numNodes = a
    elif o in ("--debug"):
        debug = a
    elif o in ("--loadFile"):
        loadFile = a
    elif o in ("--loadFileVar"):
        key,value = a.split("=",1)
        loadFileVars[key] = value
    elif o in ("--motifAPI"):
        motifAPI= a
    elif o in ("--cmdLine"):
        motif = dict.copy(motifDefaults)
        motif['cmd'] = a
        workFlow.append( motif )
    elif o in ("--topo"):
        netTopo = a
    elif o in ("--printStats"):
        motifDefaults['printStats'] = a
    elif o in ("--emberVerbose"):
        emberVerbose = a
    elif o in ("--embermotifLog"):
        embermotifLog = a
    elif o in ("--rankmapper"):
        emberrankmapper = a
    elif o in ("--netBW"):
        netBW = a
    elif o in ("--netFlitSize"):
        netFlitSize = a
    elif o in ("--netPktSize"):
        netPktSize = a
    elif o in ("--netInspect"):
        netInspect = a
    elif o in ("--rtrArb"):
        rtrArb = a
    elif o in ("--randomPlacement"):
        if a == "True":
            rndmPlacement = True
    elif o in ("--bgPercentage"):
        bgPercentage = int(a)
    elif o in ("--bgMean"):
        bgMean = int(a)
    elif o in ("--bgStddev"):
        bgStddev = int(a)
    elif o in ("--bgMsgSize"):
        bgMsgSize = int(a)
    elif o in ("--detailedModelName"):
        detailedModelName = a
    elif o in ("--detailedModelNodes"):
        detailedModelNodes = [int(i) for i in a.split(',')]
    elif o in ("--detailedModelParams"):
        detailedModelParams = a
    elif o in ("--simConfig"):
        simConfig = a
    elif o in ("--platParams"):
        platParams = a
    elif o in ("--param"):
        key,value = a.split(":",1)
        params[key] += [value]
    elif o in ("--useSimpleMemoryModel"):
        useSimpleMemoryModel=True
    elif o in ("--paramDir"):
        paramDir = a
    elif o in ("--statsModule"):
        statsModuleName = a
    elif o in ("--statsFile"):
        statsFile = a
    #yao
    elif o in ("--algoRting"):
        rting_algo = a
    elif o in ("--stats_startat"):
        stats_startat = a
    elif o in ("--numVNs"):
        numVNs = int(a)
    elif o in ("--smallCollectiveVN"):
        smallCollectiveVN = int(a)
    elif o in ("--smallCollectiveSize"):
        smallCollectiveSize = int(a)
    
    elif o in ("--qlr1"):
        qlr1 = float(a)
    elif o in ("--qlr2"):
        qlr2 = float(a)
    elif o in ("--qthld1"):
        qthld1 = float(a)
    elif o in ("--qthld2"):
        qthld2 = float(a)
    
    elif o in ("--qtable_path"):
        qtable_path = a

    elif o in ("--explore"):
        explore = float(a)

    elif o in ("--io_level"):
        io_level = int(a)   
    elif o in ("--io_thld"):
        io_thld = int(a)

    else:
        assert False, "unknow option {0}".format(o)

sys.path.append( os.getcwd() + '/' + paramDir )
print ('EMBER: using param directory: {0}'.format( paramDir ))


print( '\nEmberload.py: rting {}, stats_startat {} \n'.format(rting_algo, stats_startat))
print( '\nEmberload.py: numVNs {}, smallCollectiveVN {}, smallSize {} \n'.format(numVNs, smallCollectiveVN, smallCollectiveSize))


if 1 == len(sys.argv):
    simConfig = 'defaultSim'

if len(loadFile) > 0 and  len(workList) > 0:
    sys.exit("Error: can't specify both loadFile and cmdLine");


## yao no simConfig
if simConfig:
    try:
        config = __import__( simConfig, fromlist=[''] )
    except:
        sys.exit('Failed: could not import sim configuration `{0}`'.format(simConfig) )

    workFlow, numNodes, numCores, nicsPerNode = config.getWorkFlow( motifDefaults )
    platform, netTopo, netShape = config.getNetwork( )
    detailedModelName, detailedModelParams, detailedModelNodes = config.getDetailedModel()

#yao no workflow
if workFlow:
    workList.append( [jobid, workFlow] )
    jobid += 1

model = None

# yao no detailed model name
if detailedModelName:

    try:
        modelModule = __import__( detailedModelName, fromlist=[''] )
    except:
        sys.exit('Failed: could not import detailed model `{0}`'.format(detailedModelName) )

    try:
        modelParams = __import__( detailedModelParams, fromlist=[''] )
    except:
        sys.exit('Failed: could not import detailed model params `{0}`'.format(detailedModelNameParms) )

    model = modelModule.getModel(modelParams.params,detailedModelNodes)

print ("EMBER: platform: {0}".format( platform ))

# yao no platParams
if not platParams:
    platParams = platform + 'Params'
try:
    config = __import__( platParams, fromlist=[''] )
except:
    sys.exit('Failed: could not import `{0}`'.format(platParams) )


assert(rting_algo)
nicParams = config.nicParams

#yao
nicParams["numVNs"]=numVNs

networkParams = config.networkParams
#yao
networkParams['stats_startat'] = stats_startat

hermesParams = config.hermesParams

#yao
if smallCollectiveVN > 0:
    assert(smallCollectiveSize>=0)
    assert(numVNs>1)
    hermesParams["hermesParams.functionSM.smallCollectiveVN"] = smallCollectiveVN
    hermesParams["hermesParams.functionSM.smallCollectiveSize"] = smallCollectiveSize

emberParams = config.emberParams
platNetConfig = config.netConfig
platNetConfig['algorithm'] = rting_algo.split(",")

#yao
rtingParams = {}
rtingchecked=False
if set(platNetConfig['algorithm']) & set(['par', 'ugal-3vc', 'ugal-4vc']): 
    rtingParams.update(config.rtingParams_adp) 
    rtingchecked=True

if set(platNetConfig['algorithm']) & set(['q-adaptive']):
    rtingParams.update(config.rtingParams_q)
    assert(qlr1 > 0)
    assert(qlr2 > 0)
    # assert(rtingParams['lr2'] > 0)
    rtingParams['learning_rate'] = qlr1
    # rtingParams['learning_rate2'] = qlr1 * qlr2
    rtingParams['learning_rate2'] = qlr2

    assert(qthld1>=0)
    rtingParams['q_threshold1'] = qthld1

    assert(qthld2>=0)
    rtingParams['q_threshold2'] = qthld2

    assert(explore>=0)
    rtingParams['epsilon'] = explore

    rtingchecked=True


if set(platNetConfig['algorithm']) & set(['static']):
    rtingchecked=True
    
if not rtingchecked:
    assert( set(platNetConfig['algorithm']) & set( ['minimal', 'valiant']) )

    
if netBW:
    networkParams['link_bw'] = netBW

if netInspect:
    networkParams['network_inspectors'] = netInspect

if netFlitSize:
    networkParams['flitSize'] = netFlitSize

if netPktSize:
    networkParams['packetSize'] = netPktSize

if "" == netTopo:
    if platNetConfig['topology']:
        netTopo = platNetConfig['topology']
    else:
        sys.exit("What topo? [torus|fattree|dragonfly]")

usePlatNetConfig = False
if "" == netShape:
    usePlatNetConfig = True
    if platNetConfig['shape']:
        netShape = platNetConfig['shape']
    else:
        sys.exit("Error: " + netTopo + " needs shape")

if "torus" == netTopo:

    topoInfo = TorusInfo(netShape, netHostsPerRtr, nicsPerNode)
    topo = topoTorus()

elif "fattree" == netTopo:

    topoInfo = FattreeInfo(netShape)
    topo = topoFatTree()

elif "dragonfly" == netTopo or "dragonfly2" == netTopo:

    if usePlatNetConfig:
        topoInfo = DragonFlyInfo(platNetConfig)
    else:
        topoInfo = DragonFlyInfo(netShape)
    topo = topoDragonFly()

elif "dragonflyLegacy" == netTopo:

    topoInfo = DragonFlyLegacyInfo(netShape)
    topo = topoDragonFlyLegacy()

elif "hyperx" == netTopo:

    if usePlatNetConfig:
        topoInfo = HyperXInfo(platNetConfig)
    else:
        topoInfo = HyperXInfo(netShape, netHostsPerRtr)

    topo = topoHyperX()

elif "json" == netTopo:

    topo,rtr = netShape.split(':')
    topo = TopoJSON( topo, rtr )
    topoInfo = JSONInfo(topo.num_nodes)

else:
    sys.exit("how did we get here")

if rtrArb:
    print ("EMBER: network: topology={0} shape={1} arbitration={2}".format(netTopo,netShape,rtrArb))
else:
    print ("EMBER: network: topology={0} shape={1}".format(netTopo,netShape))

if int(numNodes) == 0:
    numNodes = int(topoInfo.getNumNodes())

nidList='0-' + str(int(numNodes)-1)

if int(numNodes) > int(topoInfo.getNumNodes()):
    sys.exit("need more nodes want " + str(numNodes) + ", have " + str(topoInfo.getNumNodes()))

print ("EMBER: numNodes={0} numNics={1}".format(numNodes, topoInfo.getNumNodes() ))

emptyNids = []

if jobid > 0 and rndmPlacement:

    print ("EMBER: random placement")

    hermesParams["hermesParams.mapType"] = 'random'

    random.seed( 0xf00dbeef )
    nidList=""
    nids = random.sample( list(range( int(topoInfo.getNumNodes()))), int(numNodes) )
    #nids.sort()

    allNids = []
    for num in range ( 0, int( topoInfo.getNumNodes()) ):
        allNids.append( num )

    emptyNids = list( set(allNids).difference( set(nids) ) )

    while nids:
        nidList += str(nids.pop(0))
        if nids:
            nidList +=","

    # yao workList empty
    tmp = workList[0]
    tmp = tmp[1]

    for x in tmp:
        x['cmd'] = "-nidList=" + nidList + " " + x['cmd']

    random.shuffle( emptyNids )

#yao init but not used
XXX = []

if rndmPlacement and bgPercentage > 0:
    if bgPercentage > 100:
        sys.exit( "fatal: bgPercentage " + str(bgPercentage) );
    count = 0
    bgPercentage = float(bgPercentage) / 100.0
    avail = int( topoInfo.getNumNodes() * bgPercentage )
    bgMotifs, r = divmod( avail - int(numNodes), 2 )

    print ("EMBER: netAlloced {0}%, bg motifs {1}, mean {2} ns, stddev {3} ns, msgsize {4} bytes".\
                    format(int(bgPercentage*100),bgMotifs,bgMean,bgStddev,bgMsgSize))
    while ( count < bgMotifs ) :
        workFlow = []
        nidList = "-nidList=" + str(emptyNids[ count * 2 ] ) + "," + str(emptyNids[ count * 2 + 1])
        motif = dict.copy(motifDefaults)
        motif['cmd'] = nidList + " Init"
        workFlow.append( motif )

        motif = dict.copy(motifDefaults)
        x,y = divmod( count , 60 )
        motif['cmd'] = nidList + " TrafficGen mean="+str(bgMean)+ " stddev=" + \
                    str(bgStddev) + " messageSize="+str(bgMsgSize) + " startDelay=" + str( y * 500 )
        workFlow.append( motif )

        motif = dict.copy(motifDefaults)
        motif['cmd'] = nidList + " Fini"
        workFlow.append( motif )

        workList.append( [ jobid, workFlow ] )
        jobid += 1
        count += 1

if 'verboseLevel' not in nicParams:
    nicParams['verboseLevel'] = debug
if 'verboseMask' not in nicParams:
    nicParams['verboseMask'] = -1
if useSimpleMemoryModel:
    nicParams['useSimpleMemoryModel'] = 1
hermesParams['hermesParams.verboseLevel'] = debug
hermesParams['hermesParams.nicParams.verboseLevel'] = debug
hermesParams['hermesParams.functionSM.verboseLevel'] = debug
hermesParams['hermesParams.ctrlMsg.verboseLevel'] = debug
hermesParams['hermesParams.ctrlMsg.pqs.verboseLevel'] = debug
hermesParams['hermesParams.ctrlMsg.pqs.verboseMask'] = -1

hermesParams["hermesParams.ctrlMsg.nicsPerNode"] = nicsPerNode
## yao?? why doing this and overwrite the platform params, comment out
# emberParams['verbose'] = emberVerbose 
hermesParams[ emberParams['os.name'] + '.numNodes'] = topoInfo.getNumNodes()

if embermotifLog:
    emberParams['motifLog'] = embermotifLog
if emberrankmapper:
    emberParams['rankmapper'] = emberrankmapper

#yao params is empty so far   
for a in params['network']:
    key, value = a.split("=")
    if key in networkParams:
        print ("override networkParams {0}={1} with {2}".format( key, networkParams[key], value ))
    else:
        print ("set networkParams {0}={1}".format( key, value ))
    networkParams[key] = value

for a in params['nic']:
    key, value = a.split("=")
    if key in nicParams:
        print ("override nicParams {0}={1} with {2}".format( key, nicParams[key], value ))
    else:
        print ("set nicParams {0}={1}".format( key, value ))
    nicParams[key] = value

for a in params['ember']:
    key, value = a.split("=")
    if key in emberParams:
        print ("override emberParams {0}={1} with {2}".format( key, emberParams[key], value ))
    else:
        print ("set emberParams {0}={1}".format( key, value ))
    emberParams[key] = value

for a in params['hermes']:
    key, value = a.split("=")
    if key in hermesParams:
        print ("override hermesParams {0}={1} with {2}".format( key, hermesParams[key], value ))
    else:
        print ("set hermesParams {0}={1}".format( key, value ))
    hermesParams[key] = value

for a in params['merlin']:
    key, value = a.split("=")
    if key in sst.merlin._params:
        print ("override hermesParams {0}={1} with {2}".format( key, sst.merlin._params[key], value ))
    else:
        print ("set merlin {0}={1}".format( key, value ))
    sst.merlin._params[key] = value

nicParams["packetSize"] =    networkParams['packetSize']
nicParams["link_bw"] = networkParams['link_bw']
# sst.merlin._params["link_lat"] = networkParams['link_lat']
sst.merlin._params["link_lat_host"] = networkParams['link_lat_host']
sst.merlin._params["link_lat_local"] = networkParams['link_lat_local']
sst.merlin._params["link_lat_global"] = networkParams['link_lat_global']
sst.merlin._params["link_bw"] = networkParams['link_bw']
sst.merlin._params["xbar_bw"] = networkParams['xbar_bw']
sst.merlin._params["flit_size"] = networkParams['flitSize']
sst.merlin._params["input_latency"] = networkParams['input_latency']
sst.merlin._params["output_latency"] = networkParams['output_latency']
sst.merlin._params["input_buf_size"] = networkParams['input_buf_size']
sst.merlin._params["output_buf_size"] = networkParams['output_buf_size']

#yao
sst.merlin._params.update(rtingParams)
sst.merlin._params["stats_startat"] = stats_startat
assert(io_level>=0)
sst.merlin._params["io_level"] = io_level
assert(io_thld>=0)
sst.merlin._params["io_thld"] = io_thld
if qtable_path:
    sst.merlin._params["load_qtable"] = 'true'
    sst.merlin._params["pathToQtableFile"] = qtable_path


if "network_inspectors" in list(networkParams.keys()):
    sst.merlin._params["network_inspectors"] = networkParams['network_inspectors']

if rtrArb:
    sst.merlin._params["xbar_arb"] = "merlin." + rtrArb

if "numVNs" in nicParams:
    sst.merlin._params["num_vns"] = int( nicParams["numVNs"])

print ("EMBER: network: BW={0} pktSize={1} flitSize={2}".format(
        networkParams['link_bw'], networkParams['packetSize'], networkParams['flitSize']))

if len(params['merlin']) == 0:
    sst.merlin._params.update( topoInfo.getNetworkParams() )

epParams = {}
epParams.update(emberParams)
epParams.update(hermesParams)

#pprint.pprint( networkParams, width=1)
#pprint.pprint( nicParams, width=1)
#pprint.pprint( sst.merlin._params, width=1)

baseNicParams = {
    "packetSize" : networkParams['packetSize'],
    "link_bw" : networkParams['link_bw'],
    "input_buf_size" : networkParams['input_buf_size'],
    "output_buf_size" : networkParams['output_buf_size'],
    "module" : nicParams['module']
}

loadInfo = LoadInfo(
    topoInfo.getNumNodes(), 
    topoInfo.getNicsPerNode(), 
    baseNicParams, epParams)

if len(loadFile) > 0:
    #Yao per job
    for jobid, nidlist, numCores, params, motifs in ParseLoadFile( loadFile, loadFileVars ):

        print(' jobid, nidlist, numCores, params, motifs')

        print( jobid, nidlist, numCores, params, motifs)

        workList = []
        workFlow = []

        myNicParams = copy.deepcopy(nicParams)
        myEpParams = copy.deepcopy(epParams)
        myNidList = copy.deepcopy(nidlist)

        #yao update myNic, myEpparams from values from params
        updateParams( params, sst.merlin._params, myNicParams, myEpParams )
        
        #yao, per motif in a job 
        # motifs: list of motif
        for motif in motifs:
            tmp = dict.copy( motifDefaults )
            tmp['cmd'] = motif
            workFlow.append( tmp )

        workList.append( [jobid, workFlow] )

        loadInfo.addPart( myNidList, myNicParams, myEpParams, numCores,  model )
        loadInfo.initWork( myNidList, workList, statNodeList )

elif len(workList) > 0:
    loadInfo.addPart( nidList, nicParams, epParams, numCores,  model )
    loadInfo.initWork( nidList, workList, statNodeList )
else:
    sys.exit("Error: need a loadFile or cmdLine")

if topo.getName() == "Fat Tree":
    topo.keepEndPointsWithRouter()

topo.prepParams()

topo.setEndPointFunc( loadInfo.setNode )
topo.build()

# stats
sst.setStatisticLoadLevel(9)

sst.setStatisticOutput("sst.statOutputCSV");
sst.setStatisticOutputOptions({
    "filepath" : statsFile,
    "separator" : ", "
})

# sst.enableStatisticForComponentType("firefly.nic",'mem_num_stores',{"type":"sst.AccumulatorStatistic","rate":"0ns"})
# sst.enableStatisticForComponentType("firefly.nic",'mem_num_loads',{"type":"sst.AccumulatorStatistic","rate":"0ns"})

# sst.enableStatisticForComponentType("firefly.nic",'mem_addrs',
# {"type":"sst.HistogramStatistic",
# 	"rate":"0ns",
# 	"binwidth":"4096",
# 	"numbins":"512"}
# )

#yao
sst.enableAllStatisticsForAllComponents(
    {
        # "type":"sst.AccumulatorStatistic",
        # "rate":"10 ns",
        # "startat": stats_startat,  ## rank other than 0 does not read this properly
        # "stopat":"70us"
    }
)
