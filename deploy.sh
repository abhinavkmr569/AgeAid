sudo docker build -t health-app . 
sudo docker run -d --name health-server -p 8080:8080 -p 8501:8501 --env-file .env --restart always health-app