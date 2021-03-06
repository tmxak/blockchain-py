import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import datetime
import requests
from flask import Flask, jsonify, request


class Blockchain:
    def __init__(self):
        self.current_votes = []
        self.chain = []
        self.nodes = set()

        # Create the genesis block
        self.new_block(previous_hash='00000', proof=100)

    def register_node(self, address):
        """
        Add a new node to the list of nodes
        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: A blockchain
        :return: True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: True if our chain was replaced, False if not
        """
        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash):
        """
        Create a new Block in the Blockchain
        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: New Block
        """
        block_hash = self.hash(f'{previous_hash}{time()}{proof}{self.current_votes}'.encode())
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'votes': self.current_votes,
            'proof': proof,
            "blockhash": block_hash,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of votes
        self.current_votes = []
        self.chain.append(block)
        return block

    def new_vote(self, userid, voteid):
        """
        Creates a new vote to go into the next mined Block
        :param userid: Address of the userid
        :param voteid: Voteid
        :param timeid: timeid
        :return: The index of the Block that will hold this vote
        """
        self.current_votes.append({
            'userid': userid,
            'voteid': voteid,
            'timeid': datetime.datetime.now(),
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block
        :param block: Block
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        sha = hashlib.sha256
        return sha(block).hexdigest()

    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        """
        # proof = 0
        # while self.valid_proof(last_proof, proof) is False:
        #     proof += 1
        #
        # return proof
        current_block = self.last_block['index'] + 1
        last_hash = self.hash(last_proof.encode())
        proof = 0
        while self.valid_proof(proof, last_hash, current_block) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(nonce, last_hash, block):
        block_string = json.dumps(block, sort_keys=True)
        guess = f'{nonce}{last_hash}{block_string}'.encode()
        # guess_hash = hashlib.sha256(guess).hexdigest()
        guess_hash = blockchain.hash(guess)
        if guess_hash[:3] != "000":
            return False


# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block_hash = blockchain.last_block['blockhash']
    # last_proof = last_block_hash['proof']
    proof = blockchain.proof_of_work(last_block_hash)

    # We must receive a reward for finding the proof.
    # The userid is "0" to signify that this node has mined a new coin.
    # blockchain.new_vote(
    #     userid="0",
    #     voteid=node_identifier
    # )

    if not blockchain.current_votes:
        return 'No transactions to mine', 200
    else:
    # Forge the new Block by adding it to the chain
        previous_hash = blockchain.last_block['blockhash']
        block = blockchain.new_block(proof, previous_hash)

        response = {
            'message': "New Block Forged",
            'index': block['index'],
            'votes': block['votes'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
            'blockhash': block['blockhash']
        }
        return jsonify(response), 200


@app.route('/votes/new', methods=['POST'])
def new_vote():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['userid', 'voteid']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Vote
    index = blockchain.new_vote(values['userid'], values['voteid'])

    response = {'message': f'Vote will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
