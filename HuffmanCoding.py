from functools import partial
from heapq import heappush, heappop, heapify
from collections import defaultdict
import pickle
import sys
import os

class HuffmanCoding:
    '''
    Huffman Coding compression utility
    Format of the compressed file:
        First 4 bytes - magic number 0x00FFFF00
        Next  4 bytes - word size
        Next  4 bytes - compressed end of file padding length
        Next  4 bytes - uncompressed end of file padding length
        Next  8 bytes - long representing the size of the word mapping, in bytes
        Next  X bytes, where X is the values of the previous 8 bytes - word mapping, as a pickled python dictionary
        Rest - Huffman Compressed file
    '''

    def __init__(self, word_size, words_per_chunk = 4096, verbose = False):
        self.word_size = word_size
        self.word_per_chunk = words_per_chunk
        self.verbose = verbose

    def compress(self, in_filename: str, out_filename: str):

        frequency_count, uncompressed_padding_length = self.get_frequency_count(in_filename)
        word_mapping = self.build_word_mapping(frequency_count)

        word_mapping_size = 0
        compressed_file_size = 0

        #read data in chunks of words_size * words_per_chunk
        chunk_size = self.word_size * self.word_per_chunk
        
        with open(in_filename, 'rb') as in_f, open(out_filename, 'wb') as out_f:

            out_f.write(bytes.fromhex("00ffff00" )) #magic number
            out_f.write(self.word_size.to_bytes(4, 'big')) #word size
            out_f.write(bytes.fromhex("00000000")) #compressed padding length, to be set later
            out_f.write(uncompressed_padding_length.to_bytes(4, 'big')) #original file padding length

            word_mapping_binary = pickle.dumps(word_mapping)
            word_mapping_size = len(word_mapping_binary)

            out_f.write(word_mapping_size.to_bytes(8, "big"))
            out_f.write(word_mapping_binary)

            #remainder from the last chunk that didn't fit into a byte
            last_chunk_remainder = ''

            if self.verbose:
                print('Performing compression')
            
            bytes_processed = 0
            og_size = os.path.getsize(in_filename)
            last_percentage = 0

            for chunk in iter(partial(in_f.read, chunk_size), b''):

                if self.verbose:
                    bytes_processed += len(chunk)
                    percentage = int(bytes_processed/og_size * 100)

                    if percentage > last_percentage:
                        print(f'\r{percentage}% completed', end = '')
                        sys.stdout.flush()
                        last_percentage = percentage
                
                #if the last word in the chunk is incomplete, pad it with 0s (this could happen only when end of file is reached)
                if len(chunk) % self.word_size != 0:
                    padded_length = ((len(chunk) // self.word_size) + 1) * self.word_size
                    chunk = chunk.ljust(padded_length, b'\0')

                compressed_chunk_str = last_chunk_remainder

                for i in range(len(chunk)//self.word_size):
                    word = chunk[i * self.word_size : i * self.word_size + self.word_size]
                    compressed_chunk_str += word_mapping[word]


                m = len(compressed_chunk_str) % 32

                last_chunk_remainder = compressed_chunk_str[-m:]
                compressed_chunk_str = compressed_chunk_str[:-m]

                for i in range(len(compressed_chunk_str)//32):
                    compressed_byte_array = int(compressed_chunk_str[i * 32 : i * 32 + 32], 2).to_bytes(4, 'big')
                    out_f.write(compressed_byte_array)
                    compressed_file_size += 4
            
            #if there are bits remaining that do not fit evently in 32, we need to pad the remainder with 0
            if len(last_chunk_remainder) > 0:
                padding_length = 32 - len(last_chunk_remainder)
                last_chunk_remainder += '0' * padding_length

                for i in range(len(last_chunk_remainder)//32):
                    compressed_byte_array = int(last_chunk_remainder[i * 32 : i * 32 + 32], 2).to_bytes(4, 'big')
                    out_f.write(compressed_byte_array)
                    compressed_file_size += 4

                out_f.seek(8)
                out_f.write(padding_length.to_bytes(4, 'big'))

        if(self.verbose):
            print('')

        return word_mapping_size, compressed_file_size

    def decompress(self, in_filename: str, out_filename: str):
        with open(in_filename, 'rb') as in_f, open(out_filename, 'wb') as out_f:
            magic = in_f.read(4).hex()

            assert magic == '00ffff00' or magic == '00ffff01', 'File is not a valid huffman compressed file'

            word_size = int.from_bytes(in_f.read(4), 'big')
            compressed_padding = int.from_bytes(in_f.read(4), 'big')
            original_padding = int.from_bytes(in_f.read(4), 'big')
            word_mapping_length = int.from_bytes(in_f.read(8), 'big')
            word_mapping = pickle.loads(in_f.read(word_mapping_length))

    def get_frequency_count(self, filename: str):

        og_size = os.path.getsize(filename)

        if self.verbose:
            print('Generating frequency count')

        frequency_count = defaultdict(int)

        bytes_processed = 0
        last_percentage = 0

        #read data in chunks of words_size * words_per_chunk
        chunk_size = self.word_size * self.word_per_chunk
        with open(filename, 'rb') as f:
            padding_length = 0
            
            for chunk in iter(partial(f.read, chunk_size), b''):
                
                if self.verbose:
                    bytes_processed += len(chunk)
                    percentage = int(bytes_processed/og_size * 100)

                    if percentage > last_percentage:
                        print(f'\r{percentage}% completed', end = '')
                        sys.stdout.flush()
                        last_percentage = percentage
                
                #if the last word in the chunk is incomplete, pad it with 0s (this could happen only when end of file is reached)
                if len(chunk) % self.word_size != 0:
                    padded_length = ((len(chunk) // self.word_size) + 1) * self.word_size
                    padding_length = padded_length - len(chunk)
                    chunk = chunk.ljust(padded_length, b'\0')

                for i in range(len(chunk)//self.word_size):
                    word = chunk[i * self.word_size : i * self.word_size + self.word_size]
                    frequency_count[word] += 1

        if(self.verbose):
            print('')
        return frequency_count, padding_length

    #https://paddy3118.blogspot.com/2009/03/huffman-encoding-in-python.html
    def build_word_mapping(self, frequency_count):
        heap = [ [weight, [word, ""] ] for word, weight in frequency_count.items()]
        
        heapify(heap)

        while len(heap) > 1:

            lo = heappop(heap)
            hi = heappop(heap)

            for pair in lo[1:]:
                pair[1] = '0' + pair[1]
            for pair in hi[1:]:
                pair[1] = '1' + pair[1]

            heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
        
        return {x[0]: x[1] for x in heappop(heap)[1:]}

if __name__ == '__main__':
    hc = HuffmanCoding(4, verbose=True)
    wms, fs = hc.compress('test.gcode', 'test.gcode.compressed')

    #print(f'Word Mapping Size: {wms} bytes Compressed File Size {fs} bytes')

    #hc.decompress('test.txt.compressed', 'test.txt.original')