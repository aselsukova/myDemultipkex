import argparse
import gzip
import os
import datetime
import pandas as pd
from demultEndgine import demultiplexer

def flush_buffers(out_buffers,out_descriptors):
    for mate in [0,1]:
        for k,v in out_buffers[mate].items():
            if len(v)>0:
                out_descriptors[mate][k].write("".join(v))
                out_buffers[mate][k] = []

parser = argparse.ArgumentParser()
parser.add_argument("input_files",type=str, nargs='+')
parser.add_argument("--indexesfile",type=str)
parser.add_argument("--out_dir",type=str)

args = parser.parse_args()

if not os.path.exists(args.out_dir):
    os.makedirs(args.out_dir)

base_index_dict = {}
with open(args.indexesfile) as fin:
    for line in fin:
        k,v = line.strip().split()
        base_index_dict[k] = v

for fname in args.input_files:
    if not fname.endswith("_1.fq.gz"):
        raise

DM = demultiplexer(base_index_dict=base_index_dict)
out_names = DM.get_output_names()
inp_files = args.input_files
matrix = pd.DataFrame(0,columns=out_names, index=inp_files)

out_descriptors = []
out_buffers = []

for r in [0,1]:
        out_descriptors.append(dict([(k,open(
            os.path.join(args.out_dir,k+"_"+str(r+1)+".fq"),"w"))\
                                    for k in DM.get_output_names()]))
        out_buffers.append(dict([(k,list())\
                                    for k in DM.get_output_names()]))

start_time = datetime.datetime.now()

for fname in args.input_files:
    print ("Processing file",fname)
    r2 = fname[:-7]+"2.fq.gz"
    r1 = fname

    r1 = gzip.GzipFile(r1)
    r2 = gzip.GzipFile(r2)

    count = 0
    report_count = 1000000
    last_index = ""
    last_sample = ""
    write_list_r1 = []
    for line in r1:
            count += 1
            rname = line
            decoded = rname.decode("utf-8")
            index = decoded[-18:-1]
            sample_name = DM.demultiplex(index)
            matrix.loc[fname,sample_name] += 1
            out_descriptors[0][sample_name].write(decoded)
            #out_buffers[0][sample_name].append(decoded)

            for i in [1,2,3]:
                out_descriptors[0][sample_name].write(r1.readline().decode("utf-8"))
                #out_buffers[0][sample_name].append(r1.readline().decode("utf-8"))
            for i in [0,1,2,3]:
                out_descriptors[1][sample_name].write(r2.readline().decode("utf-8"))
                #out_buffers[1][sample_name].append(r2.readline().decode("utf-8"))
            
            if count >= report_count and count % report_count == 0:
                    #flush_buffers(out_buffers,out_descriptors)
                    timediff = (datetime.datetime.now() - start_time).total_seconds() / 60.
                    print ("Processed: ",count," time: ",timediff," min")

#flush_buffers(out_buffers,out_descriptors)
timediff = (datetime.datetime.now() - start_time).total_seconds()
print ("Processed: ",count," time: ",timediff," sec")
matrix.to_csv(os.path.join(args.out_dir,"stats.csv"))
print ("Done!")
