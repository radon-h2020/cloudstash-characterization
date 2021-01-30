class GlobalConfig:
    # config object singleton
    _instance = None

    @staticmethod
    def get():
        if GlobalConfig._instance is None:
            return GlobalConfig()
        else:
            return GlobalConfig._instance()

    def __init__():
        # Where is the cloudstash code bindmounted to the container
        CLOUDSTASH_CODE_PATH = "/home/alpine/serverless"

        # where are the artillery scripts
        ARTILLERY_CODE_PATH = "/home/alpine/cloudstash-characterization/Artillery"

        # where is the artillery binary
        ARTILLERY_BIN_PATH = "/home/alpine/.npm-global/bin/artillery"

        # where to output artillery reports
        #  ARTILLERY_OUTPUT_PATH = "/home/alpine/cloudstash-characterization/Artillery/output/report.json"
        ARTILLERY_OUTPUT_PATH = "/tmp"

        # enable/disable debug prints
        DEBUG = False
        # enable more prints
        VERBOSE = False
