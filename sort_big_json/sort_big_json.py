import os
from datetime import datetime, timedelta
import math
import random
import argparse
import sys
import json


def get_args():
    parser = argparse.ArgumentParser(
        "Sort a huge json file without loading in fully in RAM"
    )
    parser.add_argument("--input_file", type=str, help="Path to input file")
    parser.add_argument("--batch_size", type=int, help="Batch size that can fit in memory")
    parser.add_argument("--key", type=str, help="Key or subkey used to sort")
    parser.add_argument("--sep", type=str, help="separator for nested key", default=".")
    parser.add_argument('--is_json', action='store_true', default=False, help='Indicate if it is a json or ljson file')
    parser.add_argument("--output_file", type=str, help="Path to output sorted file")

    args = parser.parse_args()
    return args


def read_jsons_chunks(file_object, chunk_size=10000):
    """Lazy function to read a json by chunk.
    Default chunk size: 10k"""
    """
        :param file_object: path file to read from
        :param chunk_size: chunk_size to read (default to 10k)
        :return: data read
    """
    # Parse the next real chunk_size lines
    chunk = file_object.read(1000000)
    data = []
    i = 0
    nb_bracket = 0
    nb_quotes = 0
    example = ""
    count_escape_char = 0
    while True:
        # Read cahracter by character
        for k, c in enumerate(chunk):
            # Check quoting
            if c == '"':
                # Check only when '"' is a delimiter of field or value in json
                if count_escape_char % 2 == 0:
                    nb_quotes += 1
            # Check beginning of brackets
            elif c == '{' and nb_quotes % 2 == 0:
                # Check only when '{' is a delimiter of field or value in json
                if count_escape_char % 2 == 0:
                    nb_bracket += 1
            # Check ending of brackets
            elif c == '}' and nb_quotes % 2 == 0:
                # Check only when '"' is a delimiter of field or value in json
                if count_escape_char % 2 == 0:
                    nb_bracket -= 1
                # This means we finished to read one json
                if nb_bracket == 0 and nb_quotes % 2 == 0:
                    example += c
                    data.append(json.loads(example))
                    i += 1
                    # When chunk_size jsons obtained, dump those
                    if i % chunk_size == 0:
                        yield(data)
                        data = []

                    # Initialize those
                    example = ""
                    continue
            # If we are in between 2 json examples or at the beginning
            elif c in ['[', ',', '\n'] and nb_bracket == 0 and nb_quotes % 2 == 0:
                continue
            # If we are at the end of the file
            if c in [']', ''] and nb_bracket == 0 and nb_quotes % 2 == 0:
                # If EOF obtained or end of jsonarray send what's left of the data
                if example == "" or example == "]":
                    yield(data)
                    return
            if c == "\\":
                count_escape_char += 1
            else:
                count_escape_char = 0
            # Append character to the json example
            example += c

        # If at the end of the chunk, read new chunk
        if k == len(chunk) - 1:
            chunk = file_object.read(1000000)
        # Keep what's left of the chunk
        elif len(chunk) != 0:
            chunk = chunk[k:]
        # if k == 0 that means that we read the whole file
        else:
            break


def compute_nb_read(path_file, batch_size, key, sep, is_json=False):
    """
        :param path_file: path file for which we count the number of lines
        :param batch_size: batch size that the machine can handle
        :param key: key or subkey on which to sort
        :param sep: separator for nested key
        :param is_json: True if json and False if ljson
        :return: number of read necessary, number of lines the data to sort
    """
    nested_key = key.split(sep)
    data_to_sort = []
    # Read all file for the first time to know how many read we need
    if is_json: # if json
        f = open(path_file)
        for jsons_chunks in read_jsons_chunks(f, chunk_size=batch_size):
            for content in jsons_chunks:
                for k in nested_key:
                    content = content[k]
                data_to_sort.append(content)
    else: # if ljson
        with open(path_file) as f:
            for i, l in enumerate(f):
                # Get the data to sort
                content = json.loads(l)
                for k in nested_key:
                    content = content[k]
                data_to_sort.append(content)

    nb_lines = len(data_to_sort)
    nb_read = math.ceil(nb_lines / batch_size)

    return nb_read, nb_lines, data_to_sort


def compute_sorted_index(data_to_sort):
    """
        :param data_to_sort: data_to_sort
        :return: sorted index of the number of lines
    """
    # Create index sorted
    idx_sorted = sorted(range(len(data_to_sort)), key=lambda k: data_to_sort[k])

    return idx_sorted


def generate_random_string(length=500, alphabet="azertyuiopqsdfghjklmwxcvbn1234567890"):
    """
        :param length: length of string wanted
        :param alphabet: alphabet from witch characters are sampled
        :return: random string of size `length`
    """
    return ''.join(random.choice(alphabet) for x in range(length))


def generate_random_json_file(path_file='./random_file', suffix=".json", nb_lines=10000, max_line_length=100):
    """
        :param path_file: path file that will be created
        :param nb_lines: number of lines wanted
        :param max_lines_length: maximum number of characters per line
        :suffix: type of output
    """
    suff = "," if suffix == ".json" else ""
    with open(path_file, 'w') as f:
        if suffix == ".json":
            f.write("[\n")
        for i in range(0, nb_lines):
            f.write(json.dumps({"test": {"case": generate_random_string(max_line_length)}}) + suff + "\n")
        if suffix == ".json":
            f.write("]")


def generate_random_json_file_cli():
    parser = argparse.ArgumentParser('generate random file containing a string per line')
    parser.add_argument("--path_file", type=str, default='./random_file.txt', help="Path to file that will be created")
    parser.add_argument("--key", type=str, default=None, help="Key on which to sort")
    parser.add_argument("--nb_lines", type=int, default=10000, help="Number of lines wanted for the file")
    parser.add_argument("--suffix", choices=['.json', '.ljson'], help='Suffix of file created (format json vs format ljson)')
    parser.add_argument("--max_line_length", type=int, default=1000, help="Max number of characters per line")
    opt = parser.parse_args()

    generate_random_json_file(opt.path_file, opt.suffix, opt.nb_lines, opt.max_line_length)


def sort_json(input_file, output_file, idx_sorted, nb_read, batch_size, is_json=False):
    """
        :param input_file: path file that will be created
        :param output_file: number of lines wanted
        :param idx_sorted: index sorted
        :param nb_read: number of read necessary
        :param batch_size: batch size used
        :param is_json: True if json and False if ljson

    """
    with open(output_file, 'a') as f:
        for i in range(nb_read):
            startTime = datetime.now()
            elements = []
            idx = idx_sorted[i*batch_size:(i+1)*batch_size]
            # get index of batch in order
            idx_sort_tmp = sorted(range(len(idx)), key=lambda k: idx[k])
            idx_sort = [idx[x] for x in idx_sort_tmp]

            # Get reverseindex
            rev_idx = sorted(range(len(idx_sort_tmp)), key=lambda k: idx_sort_tmp[k])

            waiting_line = idx_sort[0]

            j = 0
            #TODO adapt to json
            if is_json: # if json
                in_f = open(input_file)
                l = 0
                for jsons_chunks in read_jsons_chunks(in_f, chunk_size=batch_size):
                    for k, content in enumerate(jsons_chunks):
                        if k + l == waiting_line:
                            elements.append(json.dumps(content) + "\n")
                            j += 1
                            # Try to access element to the idx sort
                            try:
                                waiting_line = idx_sort[j]
                            # If fails that means it exceeds the max_line
                            except:
                                break
                    l += batch_size
            else: # if ljson
                with open(input_file) as in_f:
                    for k, l in enumerate(in_f):
                        # If line in batch add it to list of elements
                        if k == waiting_line:
                            elements.append(l)
                            j += 1
                            # Try to access element to the idx sort
                            try:
                                waiting_line = idx_sort[j]
                            # If fails that means it exceeds the max_line
                            except:
                                break

            # Recreate original order
            elements = [elements[x] for x in rev_idx]

            # Append output file
            for elem in elements:
                f.write(elem)

            print('[INFO]', nb_read - (i+1), 'read are left. It will take', str(timedelta(seconds=(nb_read - (i+1)) * (datetime.now() - startTime).total_seconds())))


def sort_big_json(input_file, batch_size, key, sep, output_file, is_json=False):
    """
        :param input_file: path file that will be created
        :param batch_size: batch size used
        :param key: key or subkey on which to sort
        :param sep: separator for nested key
        :param output_file: number of lines wanted
        :param is_json: True if json and False if ljson

    """

    assert os.path.exists(input_file)
    assert not os.path.exists(output_file)
    assert key is not None

    # Compute number of read necessary
    startTime_ = datetime.now()
    nb_read, nb_lines, data_to_sort = compute_nb_read(input_file, batch_size, key, sep, is_json)
    one_read = datetime.now() - startTime_

    print('[INFO] File was read in', str(one_read))
    print('[INFO]', nb_read, 'read are necessary. It will take', str(timedelta(seconds=nb_read * one_read.total_seconds())))

    # Get index sorted based on
    idx_sorted = compute_sorted_index(data_to_sort)

    # Sort file
    sort_json(input_file, output_file, idx_sorted, nb_read, batch_size, is_json)
    print('[INFO] File was sorted in', str(datetime.now() - startTime_))

    return nb_lines


def sort_big_json_cli():
    """
        Main function of the program
    """

    # Get arguments passed in CLI
    opt = get_args()
    batch_size = opt.batch_size
    input_file = opt.input_file
    output_file = opt.output_file
    key = opt.key
    sep = opt.sep
    is_json = opt.is_json

    assert os.path.exists(input_file)
    assert not os.path.exists(output_file)
    assert key is not None

    # Compute number of read necessary
    startTime_ = datetime.now()
    nb_read, nb_lines, data_to_sort = compute_nb_read(input_file, batch_size, key, sep, is_json)
    one_read = datetime.now() - startTime_

    print('[INFO] File was read in', str(one_read))
    print('[INFO]', nb_read, 'read are necessary. It will take', str(timedelta(seconds=nb_read * one_read.total_seconds())))

    # Get index sorted based on
    idx_sorted = compute_sorted_index(data_to_sort)

    # Sort file
    sort_json(input_file, output_file, idx_sorted, nb_read, batch_size, is_json)
    print('[INFO] File was sorted in', str(datetime.now() - startTime_))

    return nb_lines


if __name__ == "__main__":
    try:
        sys.exit(sort_big_json_cli())
    except Exception as e:
        print("[ERR] Uncaught error waiting for scripts to finish")
        print(e)
        raise
