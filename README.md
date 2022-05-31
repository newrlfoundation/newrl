# newrl

## Newrl blockchain's python client

## Prerequisites 
1. A computer accessible outside with port open for incoming.
    1. To start a node on AWS, launch an EC2 instance from instructions [here](https://docs.aws.amazon.com/efs/latest/ug/gs-step-one-create-ec2-resources.html). Make sure to make port 8090 open to public when configuring the security group. 
    2. To start a node on Digital ocean droplet, instructions [here](https://docs.digitalocean.com/products/droplets/quickstart/)
3. Git installed. Steps [here](https://git-scm.com/downloads)
4. Python3.7+ installed. This is preinstalled on most common linux distributions. On ubuntu the steps will be `sudo apt update && sudo apt install python3.10-venv`
6. Pip and python3 venv installed. Installation steps available [here](https://pip.pypa.io/en/stable/installation/)

## Installation

```bash
git clone https://github.com/asqisys/newrl.git
scripts/install.sh
```

## Start the node
```bash
screen -S newrl
scripts/start.sh
```
Screen session is used to let the node run in background when terminal is closed. 
