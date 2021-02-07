# Characterization Study of the Scalability of the https://cloudstash.io Platform

This document outlines the work carried out in order to create a characterization study of the cloudstash.io platform.
The purpose of the characterization study is to measure the: __scalability of the cloudstash.io platform as the number of stored artifacts grows.__

## System Under Test: Cloudstash

Cloudstash (available at https://cloudstash.io) is an artifact management system built entirely on AWS serverless technology.
The platform lets registered users create repositories, that can store artifacts: a zip file containing the code and generic configuration metadata of a serverless function.
Arifacts can then later be retrieved from the service.

The platform comprises a frontend webpage served using AWS Lambda (FaaS) and an AWS API Gateway (HTTP router), persistent data is stored in AWS s3 (blob storage) and AWS DynamoDB (NoSQL database).

Common for all of these technologies is that they follow a 'serverless' approach, in the sense that they are completely managed by AWS, and users pay for the service based on their usage of the services, e.g. execution time, database queries, and not for the provisioning of the resources, e.g. per minute a virtual server is rented.

The platform is developed and deployed using the serverless framework (https://www.serverless.com/) and written in Python 3.7.

## Defining Scalability

Scalability is a hard to define quality, but typically scalability is defined as the ability for a system to **scale** to meet different levels of demand.
Thus scalability in itself is a rather binary property - and more interesting is the **quality** of the scalability, i.e. "How well does the system scale?".

Therefore we need to identify some metrics that can be used to quantify the quality of the scalability. Typically scalability is measured in terms of horizontal (adding more instances of a resources) and vertical scalability (adding more resources to a given instance).
Since we are dealing with serverless computing, the scalability of the system is for the most part abstracted away from the users as part of the serverless service.
This makes it difficult to investigate the scalability of serverless-based technologies, but we can interact with the system, and we can scale this interaction, and if the system scales well, then the quality of these interactions should not change.

Since we are interested in measuring the scalability of the system as the number of stored artifacts increases, we choose two qualities of the system to quantify: the performance, and the availability of the system.
The performance will be quantified through the metric of response time for requests made to the platform, and the availability will quantified through the metrics of the HTTP response codes received when making requests to the platform, e.g. that all of our requests are handled correctly.

The assumption is that if the system scales well, then the response time should not change as we store more and more artifacts, as well as that all requests are handled correctly, no matter how many artifacts are stored in the platform.


<!-- Thus by applying a series of tests -->

<!-- e.g. the response time should be the same, no matter how many requests per second we make, all of our requests should be -->

<!-- Therefore in order to obtain some insights into the quality of the scalability -->

<!-- In terms of cloud computing, and especially serverless computing we are mostly interested in the horizontal scalability of systems, as the cloud providers make promises of horizontal scalability for the services that -->
<!-- in terms horizontal and vertical scalability. -->
<!-- Since we are interested in the scalability of platform that relies on serverless technology, -->

<!-- elasticity -->
<!-- precision -->

<!-- repeatability and reproducibility -->
<!-- isolation -->

<!-- serverless platforms evolve rapidly -->

<!-- ### Performance -->

<!-- ### Availability -->



## Benchmarking Serverless Cloud Infrastructure

Accurately benchmarking serverless technologies is hard.
The nature of the serverless paradigm means that the granular control and insight typically needed to make good benchmarks are purposefully abstracted, and hidden away from the user, in order to provide the 'serverless' experience.

Thus in order to actually acquire any insights into the system we have to adopt a black box approach to benchmarking the system.

Serverless technologies are typically provided 'as-a-service', which means that users pay for the granular usage an offered service, and thus the quality of this service is completely at the mercy of the service provider.
This means that quality of these services can change rapidly and without any warning, granted this usually a feature as providers are generally interested in offering a better service, but it means that benchmarking these systems is further complicated, as what version of a system is under test is for the most part not known.

This complicates benchmarking serverless technologies as a benchmark will be a picture of the system at a given point in time, but the next day, the provider might quietly update the service, changing the quality of the service, and thus rendering the benchmark useless apart from for historical purposes.

To alleviate these difficulties, great care should be taken when designing benchmarks for serverless technologies: benchmarks should be repeatable, reproducible, isolated and automated.

- Benchmarks should be repeatable such that they can be carried out over time, as the underlying services change, and such that these changes can be observed.
- Benchmarks should be reproducible, in the sense that they should be able to be carried out be researchers, independently of each other, and, within margin of error, these researchers should achieve the same results.
- Benchmarks should be carried out in isolation, such that the benchmark is not influenced by any optimizations of related systems, or by historical data from previous use of the technology, e.g. we do not want to run the benchmark on an existing production deployment, but instead choose to deploy a new, distinct instance of the platform, with the sole purpose of running the benchmark.
- Benchmarks should be automated, such that we can ensure that as benchmarks are run repeatedly, and by different researchers, that they are run the exact same way every time, and thus that results from different benchmarks can be compared.

<!-- ### Black Box Approach -->

<!-- ### Automation -->

<!-- ### Cloud Providers -->

<!-- ### AWS Services -->

<!-- #### Lambda -->
<!-- #### API Gateway -->
<!-- #### DynamoDB -->
<!-- #### s3 -->

## Designing Benchmarks for Scalability
Earlier in the text we put forward the assumption that due to the serverless nature of the system, the performance should be the same, irrgard


<!-- The assumption is that if the system scales well, then the response time should not change as we store more and more artifacts, as well as that all requests are handled correctly, no matter how many artifacts are stored in the platform. -->

### Benchmark 1: Sequential Artifact Uploads

### Benchmark 2: Load Test


# Benchmarking Setup

## Infrastructure

## Automation

## Benchmarking Flow

## Outputs

# Results

## Benchmark 1: Sequential Artifact Uploads

## Benchmark 2: Load Tests
