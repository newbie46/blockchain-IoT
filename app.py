import sys
import os
from flask import Flask, jsonify, request, render_template
from uuid import uuid4
import re

# Ensure the parent directory is in the sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from blockchain import Blockchain

app = Flask(__name__)
blockchain = Blockchain()

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
        type="reward"
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    print(f"Received values: {values}")  # Log the received values

    # Validate inputs
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        print("Missing values")
        return jsonify({'message': 'Missing values'}), 400

    sender = values.get('sender')
    recipient = values.get('recipient')
    amount = values.get('amount')

    if not isinstance(sender, str) or not isinstance(recipient, str) or not sender.strip() or not recipient.strip():
        print("Invalid sender or recipient address")
        return jsonify({'message': 'Invalid sender or recipient address'}), 400

    try:
        amount = float(amount)
    except ValueError:
        print("Invalid amount")
        return jsonify({'message': 'Invalid amount'}), 400

    if amount <= 0:
        print("Invalid amount")
        return jsonify({'message': 'Invalid amount'}), 400

    index = blockchain.new_transaction(sender, recipient, amount)

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None or not isinstance(nodes, list) or not all(is_valid_url(node) for node in nodes):
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
