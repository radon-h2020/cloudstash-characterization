# ArtifactGenerator

Creates randomly generated cloudstash artifacts to be used for benchmarking.
Each artifact contains a valid cloudstash `config.ini` as well as a `payload.txt` of a desired size.

## Creating artifacts

From the command line:

```sh
python generator.py 2000000
```

Will create an artifact with size 2mb.

Available paramters are:
```sh
python generator.py <artifact size in bytes> <zip filename> <cloudstash org> <cloudstash repo> <zip files>
```

Example with all paramters

```sh
python generator.py 200000 artifact.zip benchmark benchmark-artifacts True
```
