from flask import Flask, render_template, request
import ipaddress
import math

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    ip_input = request.form['ip']
    mask_input = request.form['mask']
    try:
        network = ipaddress.ip_network(f"{ip_input}/{mask_input}", strict=False)
    except ValueError as e:
        return render_template('index.html', error=f"Invalid input: {e}")

    network_bits = network.prefixlen
    host_bits = 32 - network_bits
    network_address = network.network_address
    broadcast_address = network.broadcast_address
    total_hosts = network.num_addresses - 2 if network.num_addresses > 2 else 0

    return render_template(
        'result.html',
        mode="normal",
        ip=ip_input,
        mask=mask_input,
        network_bits=network_bits,
        host_bits=host_bits,
        network_address=network_address,
        broadcast_address=broadcast_address,
        total_hosts=total_hosts
    )

# Subnetting via Host
@app.route('/subnet_host', methods=['POST'])
def subnet_host():
    ip_input = request.form['ip']
    hosts = int(request.form['hosts'])
    try:
        network = ipaddress.ip_network(f"{ip_input}/24", strict=False)
    except ValueError as e:
        return render_template('index.html', error=f"Invalid IP: {e}")

    required_bits = math.ceil(math.log2(hosts + 2))
    new_prefix = 32 - required_bits
    subnets = list(network.subnets(new_prefix=new_prefix))

    return render_template(
        'result.html',
        mode="host",
        ip=ip_input,
        hosts=hosts,
        required_bits=required_bits,
        new_prefix=new_prefix,
        subnets=subnets[:5],  # Show first few for brevity
        total=len(subnets)
    )

# Subnetting via Network
@app.route('/subnet_network', methods=['POST'])
def subnet_network():
    ip_input = request.form['ip']
    networks = int(request.form['networks'])
    try:
        network = ipaddress.ip_network(f"{ip_input}/24", strict=False)
    except ValueError as e:
        return render_template('index.html', error=f"Invalid IP: {e}")

    bits_needed = math.ceil(math.log2(networks))
    new_prefix = network.prefixlen + bits_needed
    subnets = list(network.subnets(new_prefix=new_prefix))

    return render_template(
        'result.html',
        mode="network",
        ip=ip_input,
        networks=networks,
        bits_needed=bits_needed,
        new_prefix=new_prefix,
        subnets=subnets[:5],
        total=len(subnets)
    )

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
