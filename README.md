# cloudstash-characterization

Please read Readme.md in each folder for documentation

## Running Benchmarks


Use the scripts `run_sequential_benchmark.sh` and `run_load_test_benchmark.sh` to orchestrate running the benchmark, this will create a docker container, that will first deploy a cloudstash instance, then run the benchmark, output the results to .csv saved in the `output` directory, and finally remove the created cloudstash instance.

```
>>> THE SCRIPTS EXPECTS TO BE CALLED FROM THE ROOT OF THE REPOSITORY <<<
```

You may add the following `option` flags after the required arguments:
- `--local` runt the script locally, will bindmount the benchmark code from the local directory to make development easier
- `--tail` will automatically follow the generated log file, note that when invoking the option, when you exit tail with Ctrl-c, you will the container process too, so do not use in production!
- `--debug` will enable some debug prints
- `--verbose` will enable more verbose prints

### Sequential Uploads Benchmark

This benchmark will sequentially upload the specified number of artifacts.

You must pass the `number of artifacts to be sequentially uploaded` as the first argument:
```
bash run_sequential_benchmarks <number of artifacts (int)> [options]
```

### Load Test Benchmark

This benchmark will run a predefined load test, consisting of listing artifacts, getting (downloading) artifacts and uploading artifacts.

You must pass the `number of artifacts to already be in the cloudstash instance` before the load test is started, these will be uploaded to the deployed cloudstash instance before the load test starts.
```
bash run_load_test_benchmark.sh <number of artifacts (int)> [options]
```
