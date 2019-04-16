# CS411-Website
Final project for CS411. Our group is creating a web based game!

## Requirements
docker:
```bash
sudo apt install docker.io
```
docker-compose: https://docs.docker.com/compose/install/

## Usage
After cloning the repo, open a terminal and navigate to the project folder.
First build the containers using docker-compose:
```bash
sudo docker-compose up -d --build
```

To run the container:
```bash
sudo docker-compose up
```

To connect to the database:
```bash
docker-compose exec db mysql -u root -h localhost -P 3306 -p
enter password in prompt
USE myDB;
```
