#!/bin/env python3
import argparse
import json
import logging
import multiprocessing
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Sequence

import gzip

from pheweb.file_utils import common_filepaths

from pheweb.load.load_utils import parallelize_per_pheno
from pheweb.load.load_utils import timeit
from pheweb.serve.data_access.db import TabixAnnotationDao
from pheweb.serve.data_access.db import TabixGnomadDao
from pheweb.serve.server_jeeves import annotate_manhattan
from pheweb.serve.data_access.db import ExternalFileResultDao

from pheweb.text_utils import text_to_boolean

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

@dataclass(repr=True, eq=True, frozen=True)
class Arguments:
    """
    A data transfer object (DTO) that holds the file paths required
    for adding annotations from gnomAD and a custom annotation file to
    a Manhattan file.

    Attributes:
        manhattan_filepath (str): The file path to the Manhattan file.
        gnomad_filepath (str): The file path to the gnomAD annotations file.
        annotation_filepath (str): File path to custom annotations file.
        output_filepath (str): File path to output.
    """
    gnomad_filepath: str
    annotation_filepath: str
    manhattan_filepath: str
    output_filepath: str
    compress: bool
    anno_cpra: bool =True

    def __str__(self):
        """
        Returns a formatted string representation of the file paths.

        Returns:
            str: A string displaying the file paths for the Manhattan
                 file, gnomAD annotations file, custom annotations
                 file, and output file.
        """
        return f"""
        Manhattan file: {self.manhattan_filepath}
        Gnomad file: {self.gnomad_filepath}
        Annotation file: {self.annotation_filepath}
        Output file: {self.output_filepath}

        anno_cpra: {self.anno_cpra}
        compress: {self.compress}
        """

@timeit
def process_manhattan(arguments : Arguments) -> None:
    n_query_thread=max(multiprocessing.cpu_count()-1, 1)
    anno_cpra=arguments.anno_cpra
    compress=arguments.compress
    threadpool=ThreadPoolExecutor(max_workers=n_query_thread)
    manhattan_filepath = arguments.manhattan_filepath
    annotation_dao=TabixAnnotationDao(matrix_path=arguments.annotation_filepath)
    gnomad_dao=TabixGnomadDao(matrix_path=arguments.gnomad_filepath)
    manhattan = annotate_manhattan(threadpool=threadpool,
                                   manhattan_filepath=manhattan_filepath,
                                   annotation_dao=annotation_dao,
                                   anno_cpra=anno_cpra,
                                   gnomad_dao=gnomad_dao)
    json_data = json.dumps(manhattan)
    if compress:
        data = gzip.compress(json_data.encode('utf-8'))
    else:
        data = json_data.encode('utf-8')
    with open(arguments.output_filepath, 'wb') as output_file:
        output_file.write(data)

def common_args(parser):
    parser.add_argument('--gnomad_filepath',
                        type=str,
                        help='gnomad file',
                        required=True)
    parser.add_argument('--annotation_filepath',
                        type=str,
                        help='annotation file',
                        required=True)
    parser.add_argument('--compress',
                        type=text_to_boolean,
                        nargs='?',
                        const=True,
                        default=True,
                        help='compress defaults to true')

def parse_args(argv: Sequence[str]) -> Arguments:
    # Fixed arguments
    parser = argparse.ArgumentParser(description="annotate manhattan")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--manhattan_filepath',
                       type=str,
                       help='manhattan file')
    group.add_argument('--phenocode', type=str,
                       help='phenocode')
    common_args(parser)
    parser.add_argument('--output_filepath',
                        type=str,
                        help='output file')
    parser.add_argument('--anno_cpra',
                        type=text_to_boolean,
                        nargs='?',
                        const=True,
                        default=True,
                        help='annotation cpra defaults to true')

    args = parser.parse_args(argv)
    phenotype = args.phenocode
    if phenotype is None:
        manhattan_filepath=args.manhattan_filepath
    else:
        manhattan_filepath=common_filepaths['pheno'](phenotype)

    arguments=Arguments(manhattan_filepath=manhattan_filepath,
                        gnomad_filepath=args.gnomad_filepath,
                        annotation_filepath=args.annotation_filepath,
                        output_filepath=args.output_filepath,
                        anno_cpra=args.anno_cpra,
                        compress=args.compress)
    print(arguments)
    return arguments

def create_runner(annotation_filepath: str,
                  gnomad_filepath:str,
                  compress:bool):
    def runner(pheno) -> None:
        nonlocal annotation_filepath
        nonlocal gnomad_filepath
        phenocode = pheno['phenocode']
        manhattan_filepath = common_filepaths['manhattan'](phenocode)
        output_filepath = common_filepaths['compressed-manhattan'].format(manhattan_filepath)
        arguments = Arguments(manhattan_filepath=manhattan_filepath,
                              gnomad_filepath=gnomad_filepath,
                              annotation_filepath=annotation_filepath,
                              output_filepath=output_filepath,
                              compress=compress)
        process_manhattan(arguments)
    return runner

def get_output_filepaths(compress:bool):
    def filepaths(pheno):
        nonlocal compress
        filepath = common_filepaths['manhattan'](pheno['phenocode'])
        if compress:
            filepath = common_filepaths['compressed-manhattan'].format(filepath)
        return filepath
    return filepaths

@timeit
def run(argv: Sequence[str]):
    parser = argparse.ArgumentParser(description="annotate manhattan")
    common_args(parser)
    args = parser.parse_args(argv)
    annotation_filepath=args.annotation_filepath
    gnomad_filepath=args.gnomad_filepath
    compress=args.compress
    parallelize_per_pheno(
        get_input_filepaths = lambda pheno: common_filepaths['manhattan'](pheno['phenocode']),
        get_output_filepaths = get_output_filepaths(compress),
        convert = create_runner(annotation_filepath, gnomad_filepath, compress),
        cmd = 'process_manhattan',
        skip_check = not compress
    )

def cli(argv):
    arguments = parse_args(argv)
    LOGGER.info(arguments)
    process_manhattan(arguments)

if __name__ == "__main__":
    cli(sys.argv[1:])  # pragma: no cover
