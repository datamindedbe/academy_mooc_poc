Steps followed:

* Create a Github repository.
* Clone it locally
* Create AWS account
* Make a disclaimer about costs and co - Set a budget to avoid bad surprises
* Create access keys for CLI access: https://us-east-1.console.aws.amazon.com/iam/home?region=us-east-1#/security_credentials
* Install the `aws` CLI and run:
```
aws configure --profile my_aws_account
```
* Create an SSH key in .pem format:
```
ssh-keygen -m PEM
```

* Install Terraform with tfswitch
* Add Terraform files to .gitignore
* Deploy the Terraform config (input your public SSH key)
* Connect to the instance using the outputed public IP with:
```
ssh -i <path to your .pem key> ec2-user@<public_ip>
```

* Install prerequisites with the following script:
```
sudo yum update -y && \
sudo amazon-linux-extras install -y docker && \
sudo service docker start && \
sudo usermod -a -G docker ec2-user && \
sudo curl -L https://github.com/docker/compose/releases/download/v2.5.1/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose && \
sudo chmod +x /usr/local/bin/docker-compose
```

* Logout / Login to make permissions active
* Run `docker info` to make sure you can access `docker` commands without `sudo`. Run `docker-compose --version`

### Set up Airflow:

* First, create the required folders and files
```
mkdir -p ./dags ./logs ./plugins && \
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

* Download the Airflow Get Started Docker Compose:
```
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.3.1/docker-compose.yaml'
```

* Run the Airflow initialization image:
```
docker-compose up airflow-init
```

* Once done, run the whole stack:
```
docker-compose up
```