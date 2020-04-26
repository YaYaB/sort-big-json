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
    parser.add_argument("--key", type=str, help="Key or subkey used to sor")
    parser.add_argument("--output_file", type=str, help="Path to output sorted file")

    args = parser.parse_args()
    return args


def compute_nb_read(path_file, batch_size, key):
    """
        :param path_file: path file for which we count the number of lines
        :param batch_size: batch size that the machine can handle
        :param key: key or subkey on which to sort
        :return: number of read necessary and the data to sort
    """
    #TODO adapt to json
    data_to_sort = []
    # Read all file for the first time to know how many read we need
    with open(path_file) as f:
        for i, l in enumerate(f):
            # Get the data to sort
            data_to_sort.append(json.loads(l)[key])
            pass

    nb_lines = i +1
    nb_read = math.ceil(nb_lines / batch_size)

    return nb_read, data_to_sort


def compute_sorted_index(data_to_sort, key):
    """
        :param data_to_sort: data_to_sort 
        :param key: key on which to sort
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
            if i % 1000 == 0:
                print(i)
            f.write(json.dumps({'test': generate_random_string(max_line_length)}) + suff + "\n")
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


def sort_json(input_file, output_file, idx_sorted, nb_read, batch_size):
    """
        :param input_file: path file that will be created
        :param output_file: number of lines wanted
        :param idx_sorted: index sorted
        :param nb_read: number of read necessary
        :param batch_size: batch size used

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


def main():
    """
        Main function of the program
    """

    # Get arguments passed in CLI
    opt = get_args()
    batch_size = opt.batch_size
    input_file = opt.input_file
    output_file = opt.output_file
    key = opt.key

    assert os.path.exists(input_file)
    assert not os.path.exists(output_file)
    assert key is not None

    # Compute number of read necessary
    startTime_ = datetime.now()
    nb_read, data_to_sort = compute_nb_read(input_file, batch_size, key)
    one_read = datetime.now() - startTime_

    print('[INFO] File was read in', str(one_read))
    print('[INFO]', nb_read, 'read are necessary. It will take', str(timedelta(seconds=nb_read * one_read.total_seconds())))

    # Get index sorted based on 
    idx_sorted = compute_sorted_index(data_to_sort, key)
    
    # Sort file
    sort_json(input_file, output_file, idx_sorted, nb_read, batch_size)
    print('[INFO] File was sorted in', str(datetime.now() - startTime_))

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("[ERR] Uncaught error waiting for scripts to finish")
        print(e)
        raise
