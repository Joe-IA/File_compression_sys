from bitarray import bitarray
from audio_optimizado import *
import pickle
from filesToTxt import *
from video import *


class Node:
    def __init__(self, symbol, weight=1):
        self.symbol = symbol
        self.weight = weight
        self.left = None
        self.right = None

class HuffmanTree:
    """
    HuffmanTree class:
        In charge of building the huffman tree and generating the code table for the symbols. It uses the adaptive huffman algorithm to build the tree.

    Attributes:
        root (Node): The root of the tree.
        code_table (dict): A dictionary that contains the code for each symbol.

    Methods:
        build_tree(symbols): 
            Builds the huffman tree using the adaptive huffman algorithm.

        generate_code_table(): 
            Generates the code table for the symbols in the tree.

        _generate_code_table(node, prefix): 
            Recursive function that generates the code table.

        encode(symbols): 
            Encodes the symbols using the code table.
    
    """
    def __init__(self):
        self.root = None
        self.code_table = {}

    def build_tree(self, symbols):
        symbol_counts = {}
        for symbol in symbols:
            if symbol not in symbol_counts:
                symbol_counts[symbol] = 0
            symbol_counts[symbol] += 1

        nodes = []
        for symbol, count in symbol_counts.items():
            node = Node(symbol, count)
            nodes.append(node)

        while len(nodes) > 1:
            left = nodes.pop(0)
            right = nodes.pop(0)
            parent = Node(None, left.weight + right.weight)
            parent.left = left
            parent.right = right
            nodes.append(parent)

        self.root = nodes[0]

    def generate_code_table(self):
        self.code_table = {}
        self._generate_code_table(self.root, "")

    def _generate_code_table(self, node, prefix):
        if not node.left and not node.right:
            self.code_table[node.symbol] = prefix
            return

        if node.left:
            self._generate_code_table(node.left, prefix + "0")

        if node.right:
            self._generate_code_table(node.right, prefix + "1")

    def encode(self, symbols):
        encoded_symbols = ""
        for symbol in symbols:
            encoded_symbol = self.code_table[symbol]
            encoded_symbols += encoded_symbol

        return encoded_symbols


class Encoding:
    """
    Encoding class:
        In charge of encoding and decoding the files using the huffman algorithm.

    Attributes:
        None

    Methods:
        adaptive_huffman_encoding(text):
            Encodes the text using the huffman algorithm.

        decode(encoded_message, code_table):
            Decodes the encoded message using the code table generated by the huffman algorithm.


     """
    def adaptive_huffman_encoding(self, text):
        tree = HuffmanTree()
        tree.build_tree(text)
        tree.generate_code_table()

        encoded_text = tree.encode(text)
        return encoded_text, tree.code_table

    def decode(self, encoded_message, code_table):
        decoded_message = ""
        while encoded_message:
            for character, code in code_table.items():
                if encoded_message.startswith(code):
                    decoded_message += character
                    encoded_message = encoded_message[len(code):]
        return decoded_message

class Compresion:
    """
    Compresion class

    This class contains the methods that will be used to compress and decompress the files that the user selects. It is used to abstratc the process of compressing and decompressing files, turning complex techniques to turn a file to a simple text that can be used along the huffman algorithm. 

    Attributes:
        None

    Methods:
        No constructor is needed for this class, since all the methods are static.

        The names of the methods are self explanatory about their functionallity. 

        All the methods are static, so they can be called without the need of an instance of the class. Furthermore, they all share the same parameters, which are the directory where the file is located, the name of the file and the encoding object that will be used to compress and decompress the file.

        The compression methods will turn the existing file into a text file, in which the huffman algorithm can be applied. It turns the bytes of the file into their ascii representation, and then it applies the huffman algorithm to the text. The result of the huffman algorithm is then turned into a bitarray, which is then saved in a binary file along with the code table generated by the huffman algorithm.

        The decompression methods will read the binary file and turn the bitarray into a string of bits, which is then decoded using the code table generated by the huffman algorithm. The result of the decoding is then turned into a text file, which will be turned into the original file selected by the user.

    """
    @staticmethod
    def compress_audio(directory, name):
        print(directory, name)
        audio_processor = AudioProcessor()
        encoding_instance = Encoding() 
        output_audio_file = f"{name}.bin"
        audio_processor.process_audio_to_text(directory, f"{name}.wav", output_audio_file)


    @staticmethod
    def compress_image(directory, name, encoding):
        width, height, channels, binarios = ImagesToTxt.image_to_text(f"{directory}/{name}.bmp")
        cadena_bits = ''.join(format(byte, '08b') for byte in binarios)
        paddinf = 7 - len(cadena_bits) % 7 if len(cadena_bits) % 7 != 0 else 0
        cadena_bits = cadena_bits + "0" * paddinf
        binarios = ''.join(chr(int(cadena_bits[i:i+7], 2)) for i in range(0, len(binarios), 7))
        encoded_text, tree_code_table = encoding.adaptive_huffman_encoding(binarios)
        bits = bitarray()
        bits = bitarray([int(i) & 1 for i in encoded_text])
        with open(f"{directory}/{name}.bin", "wb") as bf:
            pickle.dump((tree_code_table, bits, width, height, channels, paddinf), bf)

    @staticmethod
    def compress_text(directory, name, encoding):
        with open(f"{directory}/{name}.txt", "r") as f:
            text = f.read()
        encoded_text, tree_code_table = encoding.adaptive_huffman_encoding(text)
        bits = bitarray()
        bits = bitarray([int(i) & 1 for i in encoded_text])
        with open(f"{directory}/{name}.bin", "wb") as bf:
            pickle.dump((tree_code_table, bits), bf)
    
    @staticmethod
    def compress_video(directory, name, encoding):
        video = VideoProcessor.read_video(f"{directory}/{name}.mp4")
        video = VideoProcessor.binary_to_text(video)
        encoded_text, tree_code_table = encoding.adaptive_huffman_encoding(video)
        bits = bitarray()
        bits = bitarray([int(i) & 1 for i in encoded_text])
        with open(f"{directory}/{name}.bin", "wb") as bf:
            pickle.dump((tree_code_table, bits), bf)

    @staticmethod
    def decompress_audio(directory, name):
        audio_processor = AudioProcessor()
        encoding_instance = Encoding()
        input_audio_file = f"{name}.bin"
        audio_processor.process_text_to_audio(directory, input_audio_file, f"{name}_decompressed.wav")



    @staticmethod
    def decompress_image(directory, name, encoding):
        with open(f"{directory}/{name}.bin", "rb") as bf:
            tree_code_table, bits, width, height, channels, padding = pickle.load(bf)
        decoded_text = bits.to01()
        if padding > 0:
            decoded_text = decoded_text[:-padding]
        decoded_text = encoding.decode(decoded_text, tree_code_table)
        decoded_bytes = decoded_text.encode("utf-8")
        ImagesToTxt. text_to_image(width, height, channels,decoded_bytes, f"{directory}/{name}.bmp")


    @staticmethod
    def decompress_text(directory, name, encoding):
        with open(f"{directory}/{name}.bin", "rb") as bf:
            tree_code_table, bits = pickle.load(bf)
        decoded_text = encoding.decode(bits.to01(), tree_code_table)
        with open(f"{directory}/{name}.txt", "w") as f:
            f.write(decoded_text)

    @staticmethod
    def decompress_video(directory, name, encoding):
        with open(f"{directory}/{name}.bin", "rb") as bf:
            tree_code_table, bits = pickle.load(bf)
        decoded_text = encoding.decode(bits.to01(), tree_code_table)
        video = VideoProcessor.text_to_binary(decoded_text)
        VideoProcessor.write_video(f"{directory}/{name}.mp4", video)