# paint-by-number

Converts images to paint by number SVGs that can be colored in with javascript.

Fully functioning web app is deployed [here](https://paint-by-number-21987.web.app/) where you can upload photos, see them converted to paint by numbers, and fill them in.

_Completed for Computational Photography (CS445) at UIUC_

![demo.gif](demo.gif)

## How to Run PBNgen

The easiest way to run the code that generates a paint by number from an image is by uploading your image to our [web app](https://paint-by-number-21987.web.app/). Very big (high resolution) images might take a long time or time out due to limitations on cloud resources. Therefore, if you want to run the paint by number generator locally, follow the steps below:

- go into the project directory `cd paint-by-number`
- install the python dependencies `pip install -r requirements.txt`
- run `python main.py <image_path>` - this will output the B/W SVG and the JSON palette to the same directory as the input image
  - for example: `python main.py images/red_panda.jpg`
  - the image path is relative to the directory you are running your code
  - images should be in jpg or png format

## Project Structure

- `src`
  - the Python source code for generating a paint by number from an image
  - this contains a `PbnGen` class that can be invoked as `PbnGen("images/input_image.jpg")` with some optional parameters
  - to get the final pbn you must run `self.set_final_pbn()` which will set the internal image of the class to be the paint by number image
  - then you must run `self.output_to_svg()` to get the final SVG image and JSON color palette
- `frontend`
  - the React app for filling in SVG paint by number images
- `functions`
  - the PBN generator deployed to google cloud functions
