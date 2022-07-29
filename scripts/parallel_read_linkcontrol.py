import os,sys,time
import argparse, itertools
import numpy as np
import ujson as json
from multiprocessing import Pool

from df_utils import *

CLI=argparse.ArgumentParser()

CLI.add_argument(
  "jsonf", type=str,
)

CLI.add_argument(
  "win_size", type=int,
)

CLI.add_argument(
  "pd_index", type=str,
)

CLI.add_argument(
  "pkt_lat", type=str, ## return pkt latencies for boxplot?
)

CLI.add_argument(
  "--datafs",  # name on the CLI - drop the `--` for positional/required parameters
  nargs="*",  # 0 or more values expected => creates a list
  type=str,
)


CLI.add_argument(
  "--rawbw",  # name on the CLI - drop the `--` for positional/required parameters
  type=bool,
)

args = CLI.parse_args()

if __name__ == '__main__':

    num_workers=len(args.datafs) if len(args.datafs) < 50 else 50

    print('reading datafile, num workers: ', num_workers) 
    
    stime_0 = time.time()
    with Pool(num_workers) as pool:

        tmpres = pool.starmap_async(read_job_linkctrl, 
                                    zip(args.datafs, 
                                    itertools.repeat(0), 
                                    itertools.repeat(args.pkt_lat), 
                                    itertools.repeat(args.win_size), 
                                    itertools.repeat(args.pd_index), 
                                    itertools.repeat(args.rawbw), 
                                    ))

        res_list = tmpres.get()
        print(' Reading all finshed. Takes {:.4f} mins, Begin to IO out...'.format((time.time() - stime_0)/60) )

        res_dir = {
          'datafs' : args.datafs, 
          'job_bw' : ['not used'],
          'win_size': args.win_size,
          'res_list': res_list,
        }

        with open(args.jsonf, "w") as write_file:
            json.dump(res_dir, write_file,
                    # separators=(',', ':'), 
                    # sort_keys=True, 
                    indent=4)

        print(' IO done, write to {}\n\t total takes {:.4f} mins'.format( args.jsonf, (time.time() - stime_0)/60) )


        