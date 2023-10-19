# IoT Rollups DApp - Verification module

## Project Overview
This application is an extension to the project https://github.com/arthuravianna/iot_rollups_dapp. The project uses Cartesi Rollups to build a DApp (Decentralized Application) with verifiable logic. The purpose of this module is to check the quality of GPS data recived from busus and report attempts to decieve the application thrugh false data.


## Project Requirements
- npm
- nodeJS
- python3
- docker (version >= 20.10.12)

## Running the Dapp
To run the DApp is necessary to execute the front-end and the back-end, the later has two modes, Production Mode and Host Mode.

In Production Mode the back-end will run inside the Cartesi Machine, in Host Mode it will run on the local machine, this mode is usefull when developing an application.

After executing the Front-End and **one** of the Back-End modes the user will be able to interact with de DApp [using the curl command](#interacting-using-curl).

## Front-End
The DApp front-end consists of a Web server developed in NodeJS, it's objective is to insteract with Cartesis's contracts in the Blockchain (Layer-1), and for that it uses the Web3.js module.

The server runs on port `3000` and has 4 routes:
- `/` : Dashboard containing info about the fines to be paid. To retrive this information the Web Server makes queries to the graphql server running on port `4000`. Each page of the dashboard has data of an different epoch;
- `/submit` : Doesn't have a page, it's the route used to send inputs(real-time GPS data or a schedules) to the Web server, the Web server will then forward this data to the Contract in the Blockchain and the Contract will forward it to the back-end. **This route uses a default hardhat account and is ideal for tests.**
- `/inspect` : Used to access the inspect state of the Cartesi Machine. In this app this feature is used to get information stored in the Database (SQLite) inside the Cartesi Machine, like the know bus lines or the route of a bus line.
- `/query` : Used to query emitted fines information in form of Histogram or Time Series.

### Installing & Running
``` Bash
cd front_end
npm install
bash run_front_end.sh
```




## Back-End
The DApp back-end consists of the verifiable logic that will run inside Cartesi Rollups; this will store and update the application state given user input, and will produce outputs as vouchers (transactions that can be carried out on Layer1) and notices (informational). **The current version only uses notices**.

### Building
To build the application, run the following command:

``` Bash
docker buildx bake -f docker-bake.hcl -f docker-bake.override.hcl --load
```

### Production Mode
To execute the back-end in production mode it's necessary to generate a cartesi machine that contains the back-end logic and then run the production enviroment (containers).


#### Running the environment
In order to start the containers in production mode, simply run:
``` Bash
docker compose up
```

#### Stopping the environment
To stop the containers, first end the process with `Ctrl + C`.
Then, remove the containers and associated volumes by executing:
``` Bash
docker compose down -v
```





### Host Mode
To execute the back-end in host mode it's necessary to run the DApp back-end logic locally and then run the host enviroment (containers).

#### Running the environment
The first step is to start the containers in host mode:
``` Bash
docker compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose-host.yml up
```

#### Running the back-end locally
The second step is to run the back-end in your machine. In order to start the server, run the following commands in a dedicated terminal:
``` Bash
cd back_end
python3 -m venv .env
. .env/bin/activate
pip install -r requirements.txt
ROLLUP_HTTP_SERVER_URL="http://127.0.0.1:5004" python3 iot_prove_dapp.py
```

The server will run on port `5003` and send the corresponding notices to port `5004`. After that, you can interact with the application normally.

#### Stopping the environment
To stop the containers, first end the process with `Ctrl + C`.
Then, remove the containers and associated volumes by executing:
``` Bash
docker compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose-host.yml down -v
```


## Advancing Time
The command bellow advance 1 epoch
``` Bash
curl --data '{"id":1337,"jsonrpc":"2.0","method":"evm_increaseTime","params":[864010]}' http://localhost:8545
```


## interacting-using-curl
This form of interaction is used for tests because it uses a "default" hardhat account to cover expenses of the contracts methods execution.


### Send Vehicle Data
Execute one of the curl commands bellow.

Example 1) Execute the curl commands bellow to send data of artificial proved position of a vehicle.

``` Bash
curl -H "Content-Type: application/json" -d '{"bus_id": "2B", "trip_id":"XX;1","lat": 2, "lon": 2,"ts": 1, "ng":["2C", "3B", "XX"]}' http://localhost:3000/submit
curl -H "Content-Type: application/json" -d '{"bus_id": "2C", "trip_id":"XX;1","lat": 4, "lon": 2,"ts": 1, "ng":["2B", "3C", "XX"]}' http://localhost:3000/submit
curl -H "Content-Type: application/json" -d '{"bus_id": "3B", "trip_id":"XX;1","lat": 2, "lon": 4,"ts": 1, "ng":["3C", "2B", "XX"]}' http://localhost:3000/submit
curl -H "Content-Type: application/json" -d '{"bus_id": "3C", "trip_id":"XX;1","lat": 4, "lon": 4,"ts": 1, "ng":["3B", "2C", "XX"]}' http://localhost:3000/submit
curl -H "Content-Type: application/json" -d '{"bus_id": "XX", "trip_id":"XX;1","lat": 3, "lon": 3,"ts": 1, "ng":["2B", "2C", "3B", "3C"]}' http://localhost:3000/submit
```

Example 2) Execute the curl command bellow to load real traffic data from data.rio API.

``` Bash
cd demo
bash load.sh data_rio_2023-07-03070000.txt
```
