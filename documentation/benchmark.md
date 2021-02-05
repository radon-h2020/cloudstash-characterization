# Characterization Study of the Scalability of the https://cloudstash.io Platform
This document outlines the work carried out in order to create a characterization study of the cloudstash.io platform.
The purpose of the characterization study is thus to measure the: __'Scalability of the cloudstash.io platform as the number of stored artifacts grows.'__

## Cloudstash.io
Cloudstash.io is an artifact management system built entirely on AWS serverless technology.
The platform lets registered users create repositories, that can store artifacts, a zip file containing the code and generic configuration metadata of a serverless function, for later retrieval from the service.

The platform comprises a frontend webpage served using AWS Lambda (FaaS) and the AWS API Gateway, persistent data is stored in AWS s3 (blob storage) and AWS DynamoDB (NoSQL database).

Common for all of these technologies is that they follow a 'serverless' approach, in the sense that they are completely managed by AWS, and users pay for the service based on their usage of the services, e.g. execution time, database queries, and not for the provisioning of the resources, e.g. per minute a virtual server is rented.

## Defining Scalability
Scalability is a hard to define quality, but generally we would define scalability as the ability for a given software to be useful in cases where there is more less demand for it, in the sense that the software scales to the number of users that would like to use it.
Typically scalability is divided into two categories: horizontal (adding more instances of a resource) and vertical scalability (adding more resources to distinct instances).
In terms of cloud computing, and especially serverless computing we are mostly interested in the horizontal scalability of systems, as the cloud providers make promises of horizontal scalability for the services that 
in terms horizontal and vertical scalability.
Since we are interested in the scalability of platform that relies on serverless technology,



elasticity
precision

repeatability and reproducibility
isolation


serverless platforms evolve rapidly

### Performance

### Availability



## Benchmarking Serverless Cloud Infrastructure

### Black Box Approach

### Automation

### Cloud Providers

### AWS Services

#### Lambda
#### API Gateway
#### DynamoDB
#### s3

## Designing Benchmarks for Scalability

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
