# visionairy.py

#todo: support api key in addition to default credentials
#todo: make multi-threaded, hence enabling 8+ images/sec

import os
import time
import sys
import argparse
import base64
import json
import urllib2
from oauth2client.client import GoogleCredentials
from googleapiclient import discovery
from googleapiclient import errors

MAX_REQ_PER_SEC = 8
DETECTION_TYPES = ['face_detection',
                   'image_properties',
                   'label_detection',
                   'landmark_detection',
                   'logo_detection',
                   'safe_search_detection',
                   'text_detection',
                   'type_unspecified']

def rate_limit(max_per_sec):
    min_interval = 1.0 / float(max_per_sec)

    def decorate(func):
        last_time_called = [0.0]

        def rate_limited_function(*args, **kargs):
            elapsed = time.clock() - last_time_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kargs)
            last_time_called[0] = time.clock()
            return ret

        return rate_limited_function

    return decorate

def get_vision_service():
    credentials = GoogleCredentials.get_application_default()
    return discovery.build('vision', 'v1', credentials=credentials)

def get_payload(uri, types, max_results):
    payload = {}
    features = [{'type': t, 'maxResults': max_results} for t in types]

    # GCS URIs are supported out of the box
    if uri.startswith("gs://"):
        payload = {
            'requests': [{
                'image':{'source':{'gcsImageUri': uri}},
                'features': features
            }]
        }

    # Web URIs need to be downloaded and base64 encoded
    elif uri.startswith("http://") or uri.startswith("https://"):
        image_raw = urllib2.urlopen(uri).read()
        image_b64 = base64.b64encode(image_raw)

        payload = {
            'requests': [{
                'image':{'content': image_b64.decode('UTF-8')},
                'features': features
            }]
        }

    # Local files just needs be base64 encoded
    else:
        filename = os.path.join(os.path.dirname(__file__), uri)
        image_raw = open(filename, 'rb').read()
        image_b64 = base64.b64encode(image_raw)

        payload = {
            'requests': [{
                'image':{'content': image_b64.decode('UTF-8')},
                'features': features
            }]
        }

    return payload

@rate_limit(MAX_REQ_PER_SEC)
def make_request(service, payload):
    return service.images().annotate(body=payload)

def main(uris, types, max_results, output):
    service = get_vision_service()

    for uri in uris:
        uri = uri.strip()
        payload = get_payload(uri, types, max_results)
        request = make_request(service, payload)

        try:
            response = json.dumps(request.execute(), indent=2)
            if not output:
                print >> sys.stdout, response
            else:
                path = os.path.join(os.path.dirname(__file__), output)
                filename = os.path.join(path, os.path.basename(uri) + ".json")
                print >> open(filename, 'w'), str(response)

        except errors.HttpError, error:
            if error.resp.get("content-type", "").startswith("application/json"):
                print >> sys.stderr, error.content
            else:
                print >> sys.stderr, str(error)

            sys.exit(0)

def check_detection_type(argument):
    detection_types = [x.strip().lower() for x in argument.split(',')]

    for detection_type in detection_types:
        if detection_type not in DETECTION_TYPES:
            msg = "'%s' is not a valid Vision API detection type" % detection_type
            raise argparse.ArgumentTypeError(msg)

    return detection_types

def check_output(argument):
    if not os.path.isdir(os.path.join(os.path.dirname(__file__), argument)):
        msg = "Output directory '%s' does not exist''" % argument
        raise argparse.ArgumentTypeError(msg)

    return argument

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Applies image recognition to images stored on Google Cloud Storage using the Google Cloud Vision API.")
    parser.add_argument('uris', metavar='uri', nargs='*', default=sys.stdin, help="one or many URIs pointing to images in Google Cloud Storage, e.g. gs://bucket/image.jpg")
    parser.add_argument('-t', dest="detection_types", type=check_detection_type, default=DETECTION_TYPES, help="which detection type(s) to apply: %s (default: all)" % ", ".join(DETECTION_TYPES).lower())
    parser.add_argument('-m', dest="max_results", default=4, help="maximum number of results to return per detection type (default: 4)")
    parser.add_argument('-o', dest="output", type=check_output, default=False, help="write output to files in this directory, instead of stdout")
    cmd = parser.parse_args()

    main(cmd.uris, cmd.detection_types, cmd.max_results, cmd.output)

