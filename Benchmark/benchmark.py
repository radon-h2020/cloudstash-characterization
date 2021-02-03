# class to hold benchmark metadata
from time import time


class Benchmark:
    def __init__(self, benchmark: str, stage: str, number_of_artefacts: int):
        self.benchmark = benchmark
        self.stage = stage
        self.number_of_artefacts = number_of_artefacts
        self.start_time = time()
        self.end_time = None
        self.gateway_url = None

    def log_experiment_stop_time(self) -> None:
        self.end_time = time()
