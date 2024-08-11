```markdown
# Flask-Aerospike

[![PyPI version](https://badge.fury.io/py/flask-aerospike.svg)](https://badge.fury.io/py/flask-aerospike)
[![CI Tests](https://github.com/idoshr/flask-aerospike/actions/workflows/tests.yml/badge.svg)](https://github.com/flask/flask-aerospike/actions/workflows/tests.yml)
[![Documentation Status](https://readthedocs.org/projects/flask-aerospike/badge/?version=latest)](https://flask-aerospike.readthedocs.io/en/latest/?badge=latest)
[![Maintainability](https://api.codeclimate.com/v1/badges/6fb8ae00b1008f5f1b20/maintainability)](https://codeclimate.com/github/idoshr/flask-aerospike/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/6fb8ae00b1008f5f1b20/test_coverage)](https://codeclimate.com/github/idoshr/flask-aerospike/test_coverage)
![PyPI - Downloads](https://img.shields.io/pypi/dm/flask-aerospike)

## Overview

Flask-Aerospike is a Flask extension that provides integration with the Aerospike database. It simplifies the process of connecting to and interacting with Aerospike from your Flask applications.

## Installation

You can install Flask-Aerospike using pip:

```sh
pip install flask-aerospike
```

## Usage

Here is a simple example of how to use Flask-Aerospike in your Flask application:

```python
from flask import Flask
from flask_aerospike import Aerospike

app = Flask(__name__)
app.config['AEROSPIKE_HOSTS'] = [('127.0.0.1', 3000)]

aerospike = Aerospike(app)

@app.route('/')
def index():
    client = aerospike.client
    # Your Aerospike operations here
    return 'Hello, Aerospike!'

if __name__ == '__main__':
    app.run()
```

## Configuration

You can configure Flask-Aerospike using the following configuration variables:

- `AEROSPIKE_HOSTS`: A list of tuples containing the host and port of your Aerospike nodes.
- `AEROSPIKE_NAMESPACE`: The namespace to use in Aerospike.
- `AEROSPIKE_SET`: The set to use in Aerospike.

## Documentation

The full documentation is available at [Read the Docs](https://flask-aerospike.readthedocs.io/en/latest/).

## Contributing

Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Credits

This project is maintained by:

- Ido Shraga

See the [AUTHORS.md](AUTHORS.md) file for a full list of contributors.
```
