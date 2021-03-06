class GlobalConfig:
    # config object singleton
    _instance = None

    @staticmethod
    def get():
        if GlobalConfig._instance is None:
            GlobalConfig()
        return GlobalConfig._instance

    def __init__(self):
        if GlobalConfig._instance is None:
            GlobalConfig._instance = self
        else:
            raise RuntimeError("Only allowed to create one GlobalConfig object.")
        # Where is the cloudstash code bindmounted to the container
        self.CLOUDSTASH_CODE_PATH = "/home/alpine/serverless"

        # where are the artillery scripts
        self.ARTILLERY_CODE_PATH = "/home/alpine/cloudstash-characterization/Artillery"

        # where is the artillery binary
        self.ARTILLERY_BIN_PATH = "/home/alpine/.npm-global/bin/artillery"

        # where the serverless artillery binary is
        self.SERVERLESS_ARTILLERY_BIN_PATH = "/home/alpine/.npm-global/bin/serverless-artillery"

        # where to output artillery reports
        self.BENCHMARK_OUTPUT_PATH = "/home/alpine/output"

        # path to generator artifact output folder and code
        self.GENERATOR_PATH = "/home/alpine/cloudstash-characterization/ArtifactGenerator"

        # enable/disable debug prints
        self.DEBUG = False

        # enable more prints
        self.VERBOSE = False

        self.REALLYVERBOSE = False

        # how many times to retry cloudstash deployment/teardown
        self.RETRIES = 10

        # the delay between cloudstash deployment/teardown attempts in seconds
        self.RETRY_DELAY = 60

        # how long to wait between steps in seconds
        self.DELAY = 60

        # how long to wait between orchestration steps, e.g. how long to wait between
        # creating the infrastructure and starting the benchmark
        self.ORCHESTRATION_DELAY = 10

        # where to store generated artifacts
        self.ARTIFACT_STORE_PATH = "/home/alpine/artifacts"

        # lower limit for artifact sizes in bytes
        self.ARTIFACT_SIZE_LOWER = 25000
        # upper limit for artifact sizes in bytes
        self.ARTIFACT_SIZE_UPPER = 250000

        # seed to use for random operations
        self.RANDOM_SEED = 1
