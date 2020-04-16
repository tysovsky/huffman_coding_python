Huffman Coding implemented in Python for binary data

Usage:

To compress:

compress.py [-h] [-w WORD_SIZE] [-c CHUNK_SIZE] [-o OUT] input

Example: python compress.py book.txt

Required:

input - input file to compress

Optional:

WORD_SIZE - the size of a single word, in bytes, default 2

CHUNK_SIZE - how many words are read at once, to prevent loading entire large files in memort, default = 4096

OUT - filename of the compressed file, by default its input_filename.compressed

Generally increasing word size will make the compressed file smaller, but word mapping much larger. Since to decompress a compressed file we need the word mapping, making the word size too large will result into the word mapping + compressed file being larger than original file. Word size above 4 is rarely practical, and for the most part 2 is the sweet spot.

Decompression coming soon