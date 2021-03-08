# class to hold benchmark metadata
import time


class Benchmark:
    def __init__(self, benchmark: str, stage: str, number_of_artefacts: int):
        self.benchmark = benchmark
        self.stage = stage
        self.number_of_artefacts = number_of_artefacts
        self.start_time = time.time()
        self.end_time = None
        self.running_time = None
        self.gateway_url = None
        self.payload = None

    def log_experiment_stop_time(self) -> None:
        self.end_time = time.time()
        self.running_time = time.strftime("%H:%M:%S", time.gmtime(self.end_time - self.start_time))
