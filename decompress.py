from HuffmanCoding import HuffmanCoding
import time
import argparse
import os


parser = argparse.ArgumentParser(description="Compress input file using Huffman Coding")

parser.add_argument('input', type=str, help="file to compress")

parser.add_argument('-c', '--chunk-size', dest='chunk_size', type=int, default=4096, 
					help="words per chunk (default: \'%(default)s\')")

parser.add_argument('-o', '--out', dest='out', type=str, default=None,
					help="output file name (default: \'%(default)s\')")

args = parser.parse_args()

if args.out == None:
    args.out = args.input.split('.')[0]+'.original.'+args.input.split('.')[-2]

start = time.time()

hc = HuffmanCoding(1, args.chunk_size, verbose = True)
hc.decompress(args.input, args.out)

end = time.time()

print(f'Decompressed as {args.out}')
print(f'Time elapsed: {end-start:.3f} seconds')
