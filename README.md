![SST](http://sst-simulator.org/img/sst-logo-small.png)

# Structural Simulation Toolkit (SST)

#### This repository contains customized [sst-core](https://github.com/SPEAR-IIT/sst-core) and [sst-elements](https://github.com/SPEAR-IIT/sst-elements) forked from [SST Github page](https://github.com/sstsimulator/sst-elements) maintained by [SPEAR group](http://www.cs.iit.edu/~zlan/) at IIT.  
Visit [sst-simulator.org](http://sst-simulator.org) to learn more about SST.

---
## Study of Workload Interference with Intelligent Routing on Dragonfly

The submodules of sst-core and sst-elements contain the toolkit enhancement for Dragonfly network interference study.

### Installation 
1. Download sst-core and sst-elements from this repository, use other SST versions may cause compatible issue.  
```bash
git clone --recurse-submodules https://github.com/SPEAR-IIT/q-adaptive_sst.git
git checkout df_interference_rl
```

2. Follow [installation guide](http://sst-simulator.org/SSTPages/SSTBuildAndInstall_11dot1dot0_SeriesDetailedBuildInstructions/) to install SST.

### Run a test

check https://github.com/SPEAR-IIT/sst-elements/tree/df_interference_rl for more detail


### Precompiled container
Please check the package under this repo for a precompiled docker image,
or pull the container directly
```bash
docker pull ghcr.io/spear-iit/sst_q-adaptive:df_interference_rl
```


---


##### [LICENSE](https://github.com/sstsimulator/sst-elements/blob/devel/LICENSE)
