# PostmanCollector
Found an API running on Swagger UI? Have they disabled the JSON collection?\
Well, we can still get one.

This tool was made for Penetration Testing, but can of course be useful for anyone working with APIs and needs a collection to use with Postman.\
The tool extracts data from Swagger UI itself, creating a collection that contains:

- Domain/baseUrl
- Endpoints
- Schema
- Documentation

## Usage
The script is made to be as simple as possible:

```sh
Generate Postman Collection from Swagger/OpenAPI documentation
By 0xnoid: github.com/0xnoid

options:
  -h, --help            show this help message and exit
  -u URL, --url URL     Base URL to API documentation
  -o OUTPUT, --output OUTPUT
                        Output file name
  -s JSPATH, --swagger JSPATH
                        Custom path to swagger JS file (default: swagger-
                        ui-init.js)
  -v, --verbose         Enable verbose output

Usage: postman.py [-h] -u URL [-o OUTPUT] [-s JSPATH] [-v]

```

Example:
```sh
python postman.py -u https://api.example.com/api -o SomeCollection.json
```

If the Swagger UI `init.js` does not have the default path:
```sh
python postman.py -u https://api.example.com -s swagger.js -o SomeCollection
```

## Installation:
#### Quick install:
```sh
curl -s https://raw.githubusercontent.com/0xnoid/PostmanCollector/main/install.sh | bash
```

#### Manually:
```sh
git clone https://github.com/0xnoid/PostmanCollector
cd RepoRepo
python -m venv venv/
source venv/bin/activate
pip install -r requirements.txt
python PostmanCollector.py -h
```