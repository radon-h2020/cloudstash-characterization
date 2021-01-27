from utils import shell
from deploy_remove_cloudstash import deploy_cloudstash, remove_deployment
from run_artillery import run_artillery

# === TODO these should be read from cli
# what stage to deploy
stage = "deploy-test-1"
# what artillery script to run on the deployed cloudstash
artillery_script = "create_users.yml"
# ===

# deploy cloudstash using serverless, get the api gateway url of the deployment
gateway_url, deployed = deploy_cloudstash(stage)

# run benchmark
benchmark_run = run_artillery(artillery_script, gateway_url)

# TODO parse artillery output step

# remove the cloudstash deployment
removed = remove_deployment(stage)
