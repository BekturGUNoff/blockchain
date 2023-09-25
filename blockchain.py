import hashlib
import json
from time import time
from flask import Flask, request, jsonify

# Define the Flask app
app = Flask(__name__)

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash="1")

    def new_block(self, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'previous_hash': previous_hash or self.hash(self.chain[-1]) if self.chain else None,
        }

        # Calculate the Merkle tree root for transactions in the block
        block['merkle_root'] = self.calculate_merkle_root(block['transactions'])

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    @staticmethod
    def hash(block):
        # Hash a block using SHA-256
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def new_transaction(self, sender, recipient, amount):
        # Create a new transaction and add it to the list of transactions
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        }
        self.current_transactions.append(transaction)
        return self.last_block['index'] + 1  # Return the index of the block that will include this transaction

    def calculate_merkle_root(self, transactions):
        # Create a Merkle tree and return its root hash
        if not transactions:
            return None

        if len(transactions) == 1:
            return self.hash(transactions[0])

        # Create a list of transaction hashes
        transaction_hashes = [self.hash(tx) for tx in transactions]

        # Recursively build the Merkle tree
        while len(transaction_hashes) > 1:
            new_hashes = []
            for i in range(0, len(transaction_hashes), 2):
                if i + 1 < len(transaction_hashes):
                    combined_hash = self.hash(transaction_hashes[i] + transaction_hashes[i + 1])
                else:
                    combined_hash = self.hash(transaction_hashes[i])
                new_hashes.append(combined_hash)
            transaction_hashes = new_hashes

        return transaction_hashes[0]

    def proof_of_work(self, last_hash):
        # Implement a basic Proof of Work algorithm to find a nonce that, when hashed, produces a hash with leading zeros
        proof = 0
        while self.valid_proof(last_hash, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_hash, proof):
        # Check if the hash of the last hash and current proof contains leading zeros (adjust difficulty as needed)
        guess = f'{last_hash}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"  # Adjust the number of leading zeros as per network difficulty

# Create a new blockchain instance
blockchain = Blockchain()

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    data = request.get_json()
    sender = data['sender']
    recipient = data['recipient']
    amount = data['amount']

    # Add the transaction to the blockchain
    index = blockchain.new_transaction(sender, recipient, amount)

    response = {'message': f'Transaction will be included in block {index}'}
    return jsonify(response), 200

@app.route('/mine_block', methods=['GET'])
def mine_block():
    # Get the last block's hash
    last_block = blockchain.last_block
    last_hash = blockchain.hash(last_block)

    # Find a valid proof for the new block
    proof = blockchain.proof_of_work(last_hash)

    # Create the new block
    previous_hash = last_hash
    block = blockchain.new_block(previous_hash)
    block['proof'] = proof  # Include the proof in the block

    response = {
        'message': 'New block mined!',
        'block': block
    }
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def get_chain():
    # Return the entire blockchain
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
