# Sort big json
> Simply sort a big .json or .ljson that does not fit in memory


This tool helps you sort a big json (or ljson) file that does not fit in memory.
Given the *batch_size* that your machine can put in memory it will sort (based on the *key*) the whole file by
reading as many times as necessary.

## Installation

OS X, Linux & Windows:
No specific requirements except python3 (3.5 and later).

```sh
pip install git+https://github.com/YaYaB/sort-big-json
```


## Usage example

```sh
usage: Sort a huge json file without loading in fully in RAM
       [-h] [--input_file INPUT_FILE] [--batch_size BATCH_SIZE] [--key KEY]
       [--output_file OUTPUT_FILE]

optional arguments:
  -h, --help            show this help message and exit
  --input_file INPUT_FILE
                        Path to input file
  --batch_size BATCH_SIZE
                        Batch size that can fit in memory
  --key KEY             Key or subkey used to sor
  --output_file OUTPUT_FILE
                        Path to output sorted file

```

Please refer to [here](https://github.com/YaYaB/sort-big-json/examples) for examples.

## Benchmark
The machine used has the following specs:

```sh
cpu: i7-6700HQ CPU @ 2.60GHz × 8
ram: 16Gb
Os: Ubuntu 18.04
SSD: 512Gb Toshiba M.2 2280 THNSN5512GPUK 
```

The benchmark is the following:
TODO

## Meta

YaYaB

Distributed under the Apache license v2.0. See ``LICENSE`` for more information.

[https://github.com/YaYaB/sort-big-json](https://github.com/YaYaB/sort-big-json)
