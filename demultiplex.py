import argparse
import gzip
import os
from demultEndgine import demultiplexer

parser = argparse.ArgumentParser()
parser.add_argument("fname",type=str)
parser.add_argument("indexesfile",type=str)
parser.add_argument("out_dir",type=str)

args = parser.parse_args()

if not os.path.exists(args.out_dir):
    os.makedirs(args.out_dir)

base_index_dict = {}
with open(args.indexesfile) as fin:
    for line in fin:
        k,v = fin.readline().strip().split()
        base_index_dict[k] = v

if not args.fname.endswith("_1.fq.gz"):
    raise

r2 = args.fname[:-7]+"2.fq.gz"
r1 = args.fname

r1 = gzip.open(r1)
r2 = gzip.open(r2)

out_descriptors = []

DM = demultiplexer(base_index_dict=base_index_dict)

for r in [0,1]:
    out_descriptors[r] = dict([(k,gzip.open(
        os.path.join(args.out_dir,k+"_"+str(r+1)+".fq.gz"),"w"))\
                                for k in DM.get_output_names()])

while r1:
        rname = r1.readline()
        index = rname.decode("utf-8").strip().split(":")[-1]
        sample_name = DM.demultiplex(index)
        out_descriptors[0][sample_name].write(rname)
        for i in [1,2,3]:
            out_descriptors[0][sample_name].write(r1.readline())
        for i in [0,1,2,3]:
            out_descriptors[1][sample_name].write(r2.readline())

