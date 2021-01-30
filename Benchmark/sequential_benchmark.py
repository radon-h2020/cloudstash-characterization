from argparse import ArgumentParser
from time import sleep
from utils import shell, log
from deploy_remove_cloudstash import deploy_cloudstash, remove_deployment
from run_artillery import run_artillery
from config import GlobalConfig
from benchmark import Benchmark

# get config singleton
config = GlobalConfig.get()

def run_sequential_benchmark(benchmark: Benchmark):
    pass
