
debug = 0

# DF 1056 nodes 
netConfig = {
    "topology": "dragonfly",
    "shape": "4:8:1:33",
    'num_groups': 33,
    'routers_per_group': 8, 
    'hosts_per_router': 4,
    'intergroup_links': 1,
}

rtingParams_q = {
    "max_hops": 1,
    
    "qtable_row_type": "destG_srcN",
    "src_group_q": False,
    "src_mid_group_q": True,

    "qtable_bcast": "nobcast",

    "save_qtable": False,
    # "save_qtable_time": ,
    "load_qtable": False,
    # "pathToQtableFile": ,
    "perid_func": False ,
}

rtingParams_adp = {
    "adaptive_threshold": 2.0
}

networkParams = {
    "packetSize" : "512B",
    "flitSize" : "128B",
    "link_bw" : "25GB/s",
    "xbar_bw" : "100GB/s",
    "link_lat_host" : "10ns",
    "link_lat_local" : "30ns",
    "link_lat_global" : "300ns",

    "input_latency" : "10ns",
    "output_latency" : "10ns",

    "input_buf_size" : "15360B",
    "output_buf_size" : "15360B",

    "xbar_arb" : "merlin.xbar_arb_lru",
}

nicParams = {
	"detailedCompute.name" : "thornhill.SingleThread",
    "module" : "merlin.reorderlinkcontrol", 
    "packetSize" : networkParams['packetSize'],
    "link_bw" : networkParams['link_bw'],
    "input_buf_size" : networkParams['input_buf_size'],
    "output_buf_size" : networkParams['output_buf_size'],
    "rxMatchDelay_ns" : 10, 
    "txDelay_ns" : 5, 
    "nic2host_lat" : "5ns", 
    "useSimpleMemoryModel" : 0,

    "simpleMemoryModel.verboseLevel" : 100,
	"simpleMemoryModel.verboseMask" : 1,

	"simpleMemoryModel.memNumSlots" : 32,
	"simpleMemoryModel.memReadLat_ns" : 15, 
	"simpleMemoryModel.memWriteLat_ns" : 4, 

	"simpleMemoryModel.hostCacheUnitSize" : 32, 
	"simpleMemoryModel.hostCacheNumMSHR" : 32, 
	"simpleMemoryModel.hostCacheLineSize" : 64, 

	"simpleMemoryModel.widgetSlots" : 32, 

	"simpleMemoryModel.nicNumLoadSlots" : 16, 
	"simpleMemoryModel.nicNumStoreSlots" : 16, 

	"simpleMemoryModel.nicHostLoadSlots" : 1, 
	"simpleMemoryModel.nicHostStoreSlots" : 1, 

	"simpleMemoryModel.busBandwidth_Gbs" : 7.8,
	"simpleMemoryModel.busNumLinks" : 8,
	"simpleMemoryModel.detailedModel.name" : "firefly.detailedInterface",
	"maxRecvMachineQsize" : 100,
	"maxSendMachineQsize" : 100,
}

emberParams = {
    "os.module"    : "firefly.hades",
    "os.name"      : "hermesParams",
    "api.0.module" : "firefly.hadesMP",
    "api.1.module" : "firefly.hadesSHMEM",
    "api.2.module" : "firefly.hadesMisc",
    'firefly.hadesSHMEM.verboseLevel' : 0,
    'firefly.hadesSHMEM.verboseMask'  : -1,
    'firefly.hadesSHMEM.enterLat_ns'  : 7,
    'firefly.hadesSHMEM.returnLat_ns' : 7,
    'verbose' : 0, 
    'verboseMask': 1,
    'firefly.hadesMP.verboseLevel' : 100,
    'firefly.hadesMP.verboseMask'  : 1,
}

hermesParams = {
	"hermesParams.detailedCompute.name" : "thornhill.SingleThread",
	"hermesParams.memoryHeapLink.name" : "thornhill.MemoryHeapLink",
    "hermesParams.nicModule" : "firefly.VirtNic",

    "hermesParams.functionSM.defaultEnterLatency" : 30000,
    "hermesParams.functionSM.defaultReturnLatency" : 30000,
    "hermesParams.ctrlMsg.shortMsgLength" : 12000,
    "hermesParams.ctrlMsg.matchDelay_ns" : 15, 

    "hermesParams.ctrlMsg.txSetupMod" : "firefly.LatencyMod",
    "hermesParams.ctrlMsg.txSetupModParams.range.0" : "0-:13ns",

    "hermesParams.ctrlMsg.rxSetupMod" : "firefly.LatencyMod",
    "hermesParams.ctrlMsg.rxSetupModParams.range.0" : "0-:10ns", 

    "hermesParams.ctrlMsg.txMemcpyMod" : "firefly.LatencyMod",
    "hermesParams.ctrlMsg.txMemcpyModParams.op" : "Mult",
    "hermesParams.ctrlMsg.txMemcpyModParams.range.0" : "0-:344ps",

    "hermesParams.ctrlMsg.rxMemcpyMod" : "firefly.LatencyMod",
    "hermesParams.ctrlMsg.txMemcpyModParams.op" : "Mult",
    "hermesParams.ctrlMsg.rxMemcpyModParams.range.0" : "0-:344ps",

    "hermesParams.ctrlMsg.sendAckDelay_ns" : 0,
    "hermesParams.ctrlMsg.regRegionBaseDelay_ns" : 300, 
    "hermesParams.ctrlMsg.regRegionPerPageDelay_ns" : 10,
    "hermesParams.ctrlMsg.regRegionXoverLength" : 4096,
    "hermesParams.loadMap.0.start" : 0,
    "hermesParams.loadMap.0.len" : 2,
}
