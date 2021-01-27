from utils import shell
from deploy_remove_cloudstash import deploy_cloudstash, remove_deployment

# what stage to deploy
stage = "deploy-test-1"

# deploy cloudstash using serverless, get the api gateway url of the deployment
#  gateway_url, deployed = deploy_cloudstash(stage)

#  set gateway url as environment variable
#  shell(f"export gateway_url={gateway_url}")

#  print("deployed", deployed)
#  print("gateway_url", gateway_url)

# === insert experiment here ===

# remove the cloudstash deployment
removed = remove_deployment(stage)
print("removed", removed)
