from time import sleep
from utils import shell, log
from deploy_remove_cloudstash import deploy_cloudstash, remove_deployment
from run_artillery import run_artillery
from config import GlobalConfig
from benchmark import Benchmark
from ArtifactGenerator import generator



# get config singleton
config = GlobalConfig.get()


def run_sequential_benchmark(benchmark: Benchmark):
    artillery_script = ""

    ###
    # Deploy cloudstash
    ###

    # deploy cloudstash using serverless, get the api gateway url of the deployment
    gateway_url, deployed = deploy_cloudstash(benchmark.stage)

    # make sure everything is ready before starting benchmark
    #  log(f"Waiting {delay} seconds before starting benchmark")
    #  sleep(delay)

    ###
    # Run the benchmark
    ###

    # run benchmark
    benchmark_run = run_artillery(artillery_script, gateway_url)


    

    # TODO parse artillery output step

    ###
    # Teardown cloudstash instance
    ###

    # remove the cloudstash deployment
    removed = remove_deployment(benchmark.stage)








import click
import configparser
import requests
import os
import base64
import errno
import shutil
from configparser import Error, NoOptionError



def read_config(config_file):
    try:
        config = configparser.ConfigParser()
        config.read(config_file)
        return config
    except Error as e:
        click.secho(f"{e}",fg='red')



def upload_artifact(benchmark: Benchmark):
    api_endpoint = "test"
    zip_name = "artifact.zip"

    log(f"Creating user to obtain deploy token...")
    # Create one user
    payload = {}
    payload['username'] = "user"
    payload['password'] = "password"
    r = requests.post(
                f"{api_endpoint}/signup", #global_config.endpoint,
                json=payload,
                headers={'content-type':'application/json'}
            )
    click.echo(r.status_code)
    message_str_split = r['message'].split(" ") # extract from response
    user_token = message_str_split[len(message_str_split)-1]   # take out last word of return message, should be token
    log(f"Obtained deploy token {user_token}")

    # Create one respository
    cloudstash_repo = "benchmark"

        # post request

    # for the number of artifacts specified in benchmark do:
    for i in range(0, benchmark.number_of_artefacts):
        log(f"Processing request {i}")

        # Call generate artifact
        #python generator.py <artifact size in bytes> <zip filename> <cloudstash org> <cloudstash repo> <zip files>
        cmd = f"python generator.py 100 {zip_name} benchmark {cloudstash_repo} True"
        res = shell(cmd, context=config.GENERATOR_PATH)
        returncode = res.returncode
        
        if returncode == 0:
            # upload artifact to cloudstash

            artifact_config = read_config(global_config.configfile)
            payload = {}
            try:
                payload['artifact_name'] = artifact_config.get('FUNCTION','name')
                payload['version'] = artifact_config.get('FUNCTION','version')
                payload['description'] = artifact_config.get('FUNCTION','description')
                payload['repositoryName'] = artifact_config.get('REPOSITORY','repository')
                payload['organization'] = artifact_config.get('REPOSITORY','org')
                payload['provider'] = artifact_config.get('RUNTIME','provider')
                payload['runtime'] = artifact_config.get('RUNTIME','runtime')
                payload['handler'] = artifact_config.get('RUNTIME','handler')
                payload['applicationToken'] = user_token #global_config.token
                with open(f"{config.GENERATOR_PATH}/{zip_name}",'rb') as binfile:
                    encoded = base64.b64encode(binfile.read())
                payload['file'] = encoded#.decode()

                click.secho(f"upload function {payload['artifact_name']} to repository {payload['repositoryName']}", bold=True)
                
                r = requests.post(
                    api_endpoint, #global_config.endpoint,
                    json=payload,
                    headers={'content-type':'application/json', 'Authorization': user_token} if user_token else {'content-type':'application/json'}
                )
                click.echo(r.status_code)

            except KeyError as ke:
                click.secho(f"{ke}",fg='red') 
            except NoOptionError as noe:
                click.secho(f"{noe}",fg='red')
            except requests.exceptions.RequestException as re:
                    click.secho(f"{re}",fg='red')

            # Remove generated artifact from local fs
            cmd = f"rm generator.py"
            res = shell(cmd, context=config.GENERATOR_PATH)
            returncode = res.returncode



        else:
            # fail, try again
            log(f"Failed generating artifact for request {i}")