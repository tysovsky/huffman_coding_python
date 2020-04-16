from HuffmanCoding import HuffmanCoding
import time
import argparse
import os


parser = argparse.ArgumentParser(description="Compress input file using Huffman Coding")

parser.add_argument('input', type=str, help="file to compress")

parser.add_argument('-w', '--word-size', dest='word_size', type=int, default=2,
					help="word size in bytes (default: %(default)s)")

parser.add_argument('-c', '--chunk-size', dest='chunk_size', type=int, default=4096, 
					help="words per chunk (default: \'%(default)s\')")

parser.add_argument('-o', '--out', dest='out', type=str, default=None,
					help="output file name (default: \'%(default)s\')")

args = parser.parse_args()

if args.out == None:
    args.out = args.input+'.compressed'

start = time.time()

hc = HuffmanCoding(args.word_size, args.chunk_size)
wms, fs = hc.compress(args.input, args.out)

end = time.time()

og_size = os.path.getsize(args.input)
compressed_size = wms+fs+4+4+4+8 # word_mapping + compressed_file + magic_number + compressed_padding + original_padding + word_mapping_length

print(f'Time elapsed: {end-start:.3f} seconds')
print(f'Word Mapping Size: {wms+4+4+4+8} bytes, Compressed File Size: {fs} bytes')
print(f'Original file size: {og_size} bytes, Total Compressed file size: {compressed_size} bytes')
print(f'Compression rate: {compressed_size/og_size * 100:.2f}%')