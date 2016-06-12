# visionary.py

A cmdline tool for interacting with the Google Cloud Vision API.

## Setup a GCP project

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

## Set up visionairy.py

* Preferred: set up an isolated Python environment. Note: On OS X El Capitain this
is required or else you will get dependencey issues for the package `six`.
* Install dependencies into using `pip install -r requirements.txt`

## Examples

Read the help page:

```bash
python visionary.py --help
```

Apply all detection types to an image on Cloud Storage:

```bash
python visionary.py gs://mybucket/myimage.jpg
```

Apply face detection only (see --help for all types) to an image on Cloud Storage:

```bash
python visionary.py -t face_detection gs://mybucket/myimage.jpg
```

Bulk load images from Cloud Storage and write output to files suffixed with
".json" in the local directory:

```bash
gsutil ls gs://mybucket/ | python visionary.py -o .
```

