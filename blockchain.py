import hashlib
import json
from time import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.transactions_pool = []

        # Create the genesis block
        self.new_block(previous_hash="1", proof=100)

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]) if self.chain else None,
        }

        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        }
        self.transactions_pool.append(transaction)
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1] if self.chain else None

    def mine_block(self, miner_address):
        if not self.transactions_pool:
            return None  # No transactions to mine

        # Proof of work calculation (simplified for demonstration)
        proof = 1
        while not self.valid_proof(proof):
            proof += 1

        # Create a new block
        previous_hash = self.hash(self.last_block)
        block = self.new_block(proof, previous_hash)

        # Add transactions from the pool to the new block
        block['transactions'] = self.transactions_pool
        self.transactions_pool = []

        return block

    def valid_proof(self, proof):
        # Simplified proof-of-work validation (requires first 4 characters to be zeros)
        guess = f'{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def is_valid_transaction(self, transaction):
        # Simplified transaction validation (checking sender has enough balance)
        sender_balance = self.get_balance(transaction['sender'])
        return sender_balance >= transaction['amount']

    def get_balance(self, address):
        # Calculate the balance of an address based on the blockchain's history
        balance = 0
        for block in self.chain:
            for transaction in block['transactions']:
                if transaction['sender'] == address:
                    balance -= transaction['amount']
                if transaction['recipient'] == address:
                    balance += transaction['amount']
        return balance

# Initialize the blockchain
blockchain = Blockchain()

# Example transactions
blockchain.new_transaction("Alice", "Bob", 5)
blockchain.new_transaction("Bob", "Charlie", 3)
blockchain.new_transaction("Charlie", "Alice", 2)

# Mining a new block
miner_address = "Miner1"
new_block = blockchain.mine_block(miner_address)

if new_block:
    print("Block mined successfully.")
    print("Chain:", json.dumps(blockchain.chain, indent=4))
else:
    print("No transactions to mine.")
class BlockchainCLI:
    def __init__(self, blockchain):
        self.blockchain = blockchain

    def display_menu(self):
        print("Blockchain CLI Menu:")
        print("1. Create Transaction")
        print("2. Mine a Block")
        print("3. Check Balance")
        print("4. Display Chain")
        print("5. Quit")

    def create_transaction(self):
        sender = input("Enter sender: ")
        recipient = input("Enter recipient: ")
        amount = float(input("Enter amount: "))
        if self.blockchain.new_transaction(sender, recipient, amount):
            print("Transaction added to the pool.")
        else:
            print("Invalid transaction. Insufficient balance.")

    def mine_block(self):
        miner_address = input("Enter miner's address: ")
        new_block = self.blockchain.mine_block(miner_address)
        if new_block:
            print("Block mined successfully.")
        else:
            print("No transactions to mine.")

    def check_balance(self):
        address = input("Enter address to check balance: ")
        balance = self.blockchain.get_balance(address)
        print(f"Balance of {address}: {balance} units")

    def run(self):
        while True:
            self.display_menu()
            choice = input("Enter your choice: ")
            if choice == "1":
                self.create_transaction()
            elif choice == "2":
                self.mine_block()
            elif choice == "3":
                self.check_balance()
            elif choice == "4":
                print(json.dumps(self.blockchain.chain, indent=4))
            elif choice == "5":
                break
            else:
                print("Invalid choice. Please try again.")

# Initialize the blockchain
blockchain = Blockchain()

# Initialize the CLI interface
cli = BlockchainCLI(blockchain)

# Run the CLI
cli.run()
