echo "Setting up MOOC Airflow server prerequisites..."

# Install Docker and Docker Compose
sudo yum update -y
sudo amazon-linux-extras install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user
sudo curl -L https://github.com/docker/compose/releases/download/v2.5.1/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo chmod 666 /var/run/docker.sock

echo "Bootstrap the Airflow stack folder structure at the current location"
# Create the Airflow stack prerequisites folders and upload the smoke test dag.
mkdir -p ./dags ./logs ./plugins ./crons
echo -e "AIRFLOW_UID=$(id -u)" > .env

curl -sfO 'https://raw.githubusercontent.com/datamindedbe/academy_mooc_poc/main/references/airflow/docker-compose.yaml'
sudo curl -s https://raw.githubusercontent.com/datamindedbe/academy_mooc_poc/main/references/airflow/smoke_test_dag.py -o ./dags/smoke_test_dag.py

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
S3_BUCKET_NAME="mooc-dags-$AWS_ACCOUNT_ID"
echo "Creating a CRON job to sync DAG files between the ./dags folder and the S3 bucket $S3_BUCKET_NAME..."
echo "* * * * *  aws s3 sync --delete s3://$S3_BUCKET_NAME/ /home/ec2-user/dags/" >> /home/ec2-user/crons/cron_jobs
chmod 600 /home/ec2-user/crons/cron_jobs
sleep 2
crontab /home/ec2-user/crons/cron_jobs