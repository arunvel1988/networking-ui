from flask import Flask, render_template, request
import ipaddress
import math

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# Normal calculation
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
        subnets=subnets[:5],  # show first 5 for brevity
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

# Supernetting
@app.route('/supernet', methods=['POST'])
def supernet():
    ip1_input = request.form['ip1']
    ip2_input = request.form['ip2']

    try:
        net1 = ipaddress.ip_network(ip1_input, strict=False)
        net2 = ipaddress.ip_network(ip2_input, strict=False)
    except ValueError as e:
        return render_template('index.html', error=f"Invalid IP input: {e}")

    start_ip = min(net1.network_address, net2.network_address)
    end_ip = max(net1.broadcast_address, net2.broadcast_address)
    supernet_list = list(ipaddress.summarize_address_range(start_ip, end_ip))

    return render_template(
        'result.html',
        mode="supernet",
        ip1=ip1_input,
        ip2=ip2_input,
        supernet_list=supernet_list
    )

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
