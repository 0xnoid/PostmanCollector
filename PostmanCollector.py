import json
import sys
import re
import argparse
import requests
from urllib.parse import urlparse, urljoin
from typing import Dict, Optional

class SwaggerParser:
    def __init__(self, url: str, swagger_path: Optional[str] = None):
        self.url = url.rstrip('/')
        self.base_url = urlparse(self.url)
        self.swagger_path = swagger_path or 'swagger-ui-init.js'
        self.api_spec = None

    def _get_base_url(self) -> str:
        return f"{self.base_url.scheme}://{self.base_url.netloc}"

    def _extract_json_from_js(self, js_content: str) -> Dict:
        """Extract and convert JS object to JSON."""
        try:
            options_match = re.search(r'let\s+options\s*=\s*({[\s\S]*?);\s*(?:let|url|window)', js_content)
            if not options_match:
                raise Exception("Could not find options object")

            js_object = options_match.group(1)
            
            js_object = re.sub(r'(?m)^\s*//.*$', '', js_object)
            js_object = re.sub(r'/\*[\s\S]*?\*/', '', js_object)
            js_object = re.sub(r'undefined', 'null', js_object)
            js_object = re.sub(r'new Date\([^)]*\)', '"2024-01-01"', js_object)
            js_object = re.sub(r',(\s*[}\]])', r'\1', js_object)
            js_object = re.sub(r'(?<!["\\])\\n', ' ', js_object)
            
            js_object = re.sub(r'"description"\s*:\s*"[\s\n]*"', '"description": ""', js_object)
            
            try:
                parsed = json.loads(js_object)
                if isinstance(parsed, dict) and 'swaggerDoc' in parsed:
                    return parsed['swaggerDoc']
                return parsed
            except json.JSONDecodeError as e:
                context_start = max(0, e.pos - 50)
                context_end = min(len(js_object), e.pos + 50)
                print(f"JSON error at position {e.pos}: {str(e)}")
                print(f"Context: {js_object[context_start:context_end]}")
                raise

        except Exception as e:
            print(f"Error processing JS: {str(e)}")
            raise

    def _convert_to_postman(self) -> Dict:
        def resolve_schema_ref(ref: str) -> Dict:
            schema_name = ref.split('/')[-1]
            if 'components' in self.api_spec and 'schemas' in self.api_spec['components']:
                return self.api_spec['components']['schemas'].get(schema_name, {})
            return {}

        def process_request_body(request_body: Dict) -> Dict:
            if not request_body.get('content', {}).get('application/json', {}).get('schema'):
                return None
            
            schema = request_body['content']['application/json']['schema']
            if '$ref' in schema:
                schema = resolve_schema_ref(schema['$ref'])
                
            if schema.get('type') == 'object' and 'properties' in schema:
                example = {}
                for prop, details in schema['properties'].items():
                    if 'example' in details:
                        example[prop] = details['example']
                    elif 'type' in details:
                        if details['type'] == 'string':
                            example[prop] = ""
                        elif details['type'] == 'number':
                            example[prop] = 0
                        elif details['type'] == 'boolean':
                            example[prop] = False
                        elif details['type'] == 'array':
                            example[prop] = []
                        elif details['type'] == 'object':
                            example[prop] = {}
                
                return {
                    'mode': 'raw',
                    'raw': json.dumps(example, indent=2),
                    'options': {
                        'raw': {
                            'language': 'json'
                        }
                    }
                }
            return None

        collection = {
            "info": {
                "name": self.api_spec.get('info', {}).get('title', 'API Collection'),
                "_postman_id": "auto-generated",
                "description": self.api_spec.get('info', {}).get('description', ''),
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": [],
            "variable": [{
                "key": "baseUrl",
                "value": self._get_base_url(),
                "type": "string"
            }]
        }

        paths = self.api_spec.get('paths', {})
        tag_items = {}

        for path, methods in paths.items():
            for method, details in methods.items():
                if method == 'parameters':
                    continue

                tags = details.get('tags', ['default'])

                for tag in tags:
                    if tag not in tag_items:
                        tag_items[tag] = {
                            "name": tag,
                            "item": []
                        }
                        collection["item"].append(tag_items[tag])

                    request = {
                        "name": details.get('summary', f"{method.upper()} {path}"),
                        "description": details.get('description', ''),
                        "request": {
                            "method": method.upper(),
                            "header": [],
                            "url": {
                                "raw": "{{baseUrl}}" + path,
                                "host": ["{{baseUrl}}"],
                                "path": [p for p in path.split('/') if p]
                            }
                        },
                        "response": []
                    }

                    query_params = []
                    path_params = []
                    header_params = []

                    all_params = methods.get('parameters', []) + details.get('parameters', [])
                    
                    for param in all_params:
                        if param.get('in') == 'query':
                            query_params.append({
                                "key": param['name'],
                                "value": "",
                                "description": param.get('description', '')
                            })
                        elif param.get('in') == 'header':
                            header_params.append({
                                "key": param['name'],
                                "value": "",
                                "description": param.get('description', '')
                            })

                    if query_params:
                        request["request"]["url"]["query"] = query_params
                    if header_params:
                        request["request"]["header"].extend(header_params)

                    if 'requestBody' in details:
                        body = process_request_body(details['requestBody'])
                        if body:
                            request["request"]["body"] = body

                    tag_items[tag]["item"].append(request)

        return collection

    def parse(self) -> Dict:
        """Parse Swagger/OpenAPI specification."""
        js_url = f"{self.url}/{self.swagger_path}"
        print(f"Fetching JS from: {js_url}")

        response = requests.get(js_url)
        if not response.ok:
            raise Exception(f"Failed to fetch {self.swagger_path}: {response.status_code}")

        self.api_spec = self._extract_json_from_js(response.text)
        return self._convert_to_postman()


class PostmanCollectionGenerator:
    def __init__(self, input_source: str, output_file: Optional[str] = None, swagger_path: Optional[str] = None):
        self.input_source = input_source
        self.output_file = output_file
        self.swagger_path = swagger_path
        self.collection = None

    def process_swagger(self) -> None:
        parser = SwaggerParser(self.input_source, self.swagger_path)
        self.collection = parser.parse()

        if not self.output_file:
            domain = urlparse(self.input_source).netloc.split('.')[0]
            self.output_file = f"{domain}_collection.json"

    def save_collection(self) -> None:
        with open(self.output_file, 'w') as f:
            json.dump(self.collection, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''By 0xnoid: github.com/0xnoid
Generate Postman Collection from Swagger/OpenAPI documentation'''
    )
    parser.add_argument('-u', '--url', required=True,
                    help='Base URL to API documentation')
    parser.add_argument('-o', '--output',
                    help='Output file name')
    parser.add_argument('-s', '--swagger',
                    metavar='JSPATH',
                    help='Custom path to swagger JS file (default: swagger-ui-init.js)')
    parser.add_argument('-v', '--verbose', action='store_true',
                    help='Enable verbose output')

    args = parser.parse_args()

    try:
        generator = PostmanCollectionGenerator(args.url, args.output, args.swagger)
        generator.process_swagger()
        generator.save_collection()
        print(f"Collection saved to {generator.output_file}")
    except Exception as e:
        print(f"Error: {str(e)}")
        if args.verbose:
            import traceback
            print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()