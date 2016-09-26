# visionary.py

A cmdline tool for interacting with the Google Cloud Vision API. Useful for bulk jobs.

## Set up a GCP project

* Create a project with the [Google Cloud Console][cloud-console], and enable
  the [Vision API][vision-api].
* From the Cloud Console, create a service account,
  download its json credentials file, then set the 
  `GOOGLE_APPLICATION_CREDENTIALS` environment variable:

  ```bash
  export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-project-credentials.json
  ```

[cloud-console]: https://console.cloud.google.com
[vision-api]: https://console.cloud.google.com/apis/api/vision.googleapis.com/overview?project=_

## Set up visionary.py

* Preferred: set up an isolated Python environment. Note: On OS X El Capitain this
is required or else you will get dependency issues for the package `six`.
* Install dependencies using `pip install -r requirements.txt`

## Examples

Read the help page:

```bash
python visionary.py --help
```

Apply all detection types to a local file:

```bash
python visionary.py myimage.jpg
```

Apply all detection types to remote file accessible over HTTP:

```bash
python visionary.py http://www.example.com/myimage.jpg
```

Apply all detection types to an image on Cloud Storage:

```bash
python visionary.py gs://mybucket/myimage.jpg
```

Apply face detection only (see --help for all types) to an image on Cloud Storage:

```bash
python visionary.py -t face_detection gs://mybucket/myimage.jpg
```

Bulk load images in the local directory 'input' and write output to files suffixed with
".json" in the local directory 'output':

```bash
find input -type f | python visionary.py -o output
```

Bulk load images from Cloud Storage and write output to files suffixed with
".json" in the local directory 'output':

```bash
gsutil ls gs://mybucket/ | python visionary.py -o output
```

