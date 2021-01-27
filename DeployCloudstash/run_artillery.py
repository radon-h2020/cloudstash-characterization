from utils import shell, log
from config import ARTILLIERY_CODE_PATH, ARTILLIERY_OUTPUT_PATH


script_file = "create_users.yml"

# log(f"Running Artilliery with script {script_file}")

def run_artilliery(file):
    artillery_cmd = f"""artillery run {file} --output {ARTILLIERY_OUTPUT_PATH}"""
    res = shell(artillery_cmd, context=ARTILLIERY_CODE_PATH)
    returncode = res.returncode
    print(returncode)

run_artilliery(script_file)