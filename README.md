# Learn Blockchains by Building One

This is the source code for post on [Building a Blockchain](https://medium.com/p/117428612f46).

## Installation

1. Make sure [Python 3.6+](https://www.python.org/downloads/) is installed.
2. Install [pipenv](https://github.com/kennethreitz/pipenv).

```
$ pip install pipenv
```

3. Create a _virtual environment_ and specify the Python version to use.

```
$ pipenv --python=python3.6
```

4. Install requirements.

```
$ pipenv install
```

5. Run the server:
    * `$ pipenv run python blockchain.py`
    * `$ pipenv run python blockchain.py -p 5001`
    * `$ pipenv run python blockchain.py --port 5002`

## Docker

Another option for running this blockchain program is to use Docker.  Follow the instructions below to create a local Docker container:

1. Clone this repository
2. Build the docker container

```
$ docker build -t blockchain .
```

3. Run the container

```
$ docker run --rm -p 80:5000 blockchain
```

4. To add more instances, vary the public port number before the colon:

```
$ docker run --rm -p 81:5000 blockchain
$ docker run --rm -p 82:5000 blockchain
$ docker run --rm -p 83:5000 blockchain
```

The github repository contains a basic implementation of a blockchain and its client using Python. This blockchain has the following features:

- Possibility of adding multiple nodes to the blockchain
- Proof of Work (PoW)
- Simple conflict resolution between nodes
- Transactions with RSA encryption

The blockchain client has the following features:

- Wallets generation using Public/Private key encryption (based on RSA algorithm)
- Generation of transactions with RSA encryption

This github repository also contains 2 dashboards:

- "Blockchain Frontend" for miners
- "Blockchain Client" for users to generate wallets and send coins


# Dependencies

- Works with ```Python 3.6```
- [Anaconda's Python distribution](https://www.continuum.io/downloads) contains all the dependencies for the code to run.

# How to run the code

1. To start a blockchain node, go to ```blockchain``` folder and execute the command below:
```python blockchain.py -p 5000```
2. You can add a new node to blockchain by executing the same command and specifying a port that is not already used. For example, ```python blockchain.py -p 5001```
3. TO start the blockchain client, go to ```blockchain_client``` folder and execute the command below:
```python blockchain_client.py -p 8080```
4. You can access the blockchain frontend and blockchain client dashboards from your browser by going to localhost:5000 and localhost:8080


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.