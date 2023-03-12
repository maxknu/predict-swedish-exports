# predict-swedish-exports Web App and Python code
 Based on https://github.com/PolinaKnutsson/Predicting-Swedish-exports



# How to create Docker container to run this app
docker build -t damtrapa/zmb-restart-app .

docker run -it -p 5000:5000 -d damtrampa/zomboid-restart-app

docker push damtrapa/zmb-restart-app