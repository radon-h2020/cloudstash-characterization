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

        # where to output artillery reports
        # TODO change
        #  ARTILLERY_OUTPUT_PATH = "/home/alpine/output/report.json"
        self.ARTILLERY_OUTPUT_PATH = "/tmp"

        # path to generator artifact output folder and code
        self.GENERATOR_PATH = "/home/alpine/cloudstash-characterization/ArtifactGenerator"

        # enable/disable debug prints
        self.DEBUG = False

        # enable more prints
        self.VERBOSE = False

        # how many tome to retry cloudstash deployment/teardown
        self.RETRIES = 10

        # the delay between cloudstash deployment/teardown attempts in seconds
        self.RETRY_DELAY = 60

        # how long to wait between steps in seconds
        self.DELAY = 60

        # how long to wait between orchestration steps, e.g. how long to wait between
        # creating the infrastructure and starting the benchmark
        self.ORCHESTRATION_DELAY = 60

        # where to store generated artifacts
        # TODO change
        #  self.ARTIFACT_STORE_PATH = "/home/alpine/artifacts"
        self.ARTIFACT_STORE_PATH = "../artifacts"
