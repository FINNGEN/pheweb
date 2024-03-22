# Quick start

  To run against a site e.g. r9 cd to the root of the project
  install the depdendencies then run the following command.

  ```
  export PYTHONPATH=$(pwd):$PYTHONPATH
  DEVELOPMENT_HOST=https://r9.finngen.fi pytest -v -s tests/integration/test_page.py
  ```

# Details

  There are three modes to run these tests; development, image, build.

## Host Test

   Used for developing selinum tests. By providing the
   environment variable `DEVELOPMENT_HOST` with the url
   of a pheweb instance (without authentication).  It
   will run the selinum test against the pheweb instance.

   This uses your local browser giving a front row seat
   to how the tests are run.


   Below is an exmaple of how to run the tests in the host
   mode

   ```
   DEVELOPMENT_HOST=https://r9.finngen.fi pytest -v -s tests/integration/test_page.py
   ```

## Image test

   Used to run selinum test against images. By providing
   the environment variable `DEVELOPMENT_IMAGE` with the
   image to run the test against.


   DEVELOPMENT_IMAGE

   Below is an exmaple of how to run the tests in the image
   mode

   ```
   DEVELOPMENT_IMAGE="eu.gcr.io/phewas-development/pheweb:wip-509069f8c5d64d6096d2e97ff2b7c3b7e57e4d57" pytest -v -s tests/integration/test_page.py
   ```

## Build test

   This is the default behavior and takes no arguments.  It
   builds the pheweb image and
   then runs the test against it.

  pytest -v -s tests/integration/test_page.py
  `
