from flask import Flask, render_template, request
import ipaddress

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

    ip_binary = ''.join([f"{int(octet):08b}." for octet in ip_input.split('.')])[:-1]
    mask_binary = ''.join([f"{int(octet):08b}." for octet in str(network.netmask).split('.')])[:-1]

    network_bits = bin(int(network.netmask))[2:].zfill(32).count('1')
    host_bits = 32 - network_bits

    network_address = network.network_address
    broadcast_address = network.broadcast_address
    total_hosts = network.num_addresses - 2 if network.num_addresses > 2 else 0

    # Subnetting via network bits (borrowing bits)
    subnetting_examples = []
    for extra_bits in range(1, 4):
        new_prefix = network.prefixlen + extra_bits
        if new_prefix < 32:
            subnets = list(network.subnets(new_prefix=new_prefix))
            subnetting_examples.append((f"/{new_prefix}", len(subnets), subnets[0], subnets[1]))

    # Supernetting example (reducing prefix)
    supernet_example = None
    if network.prefixlen > 8:
        supernet_example = list(network.supernet(new_prefix=network.prefixlen - 1))

    return render_template(
        'result.html',
        ip=ip_input,
        mask=mask_input,
        ip_binary=ip_binary,
        mask_binary=mask_binary,
        network_bits=network_bits,
        host_bits=host_bits,
        network_address=network_address,
        broadcast_address=broadcast_address,
        total_hosts=total_hosts,
        subnetting_examples=subnetting_examples,
        supernet_example=supernet_example
    )

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
