# vpype-ttf
Vpype plugin for using True Type fonts for text.

For `vpype`, see: https://github.com/abey79/vpype

## ftext

A shortening of "font text", this command accepts the required arguments of a path to a TrueType, and a string of text to render, and an optional argument of the text size, and adds the rendered text lines to the document in the pipeline.

## Installation
* Install repository:
* `pip install vpype-ttf`

## Usage
Have font file specified, eg:
* `vpype ftext /usr/share/fonts/truetype/open-sans/OpenSans-Bold.ttf "vpype-ttf" show`

<img width="1031" alt="the text 'vpype-ttf' rendered with vpype show" src="img/vpype-ttf.png">

## Options
vpype-ttf currently supports font scaling with the -s or --size option.
* `vpype ftext -s 10cm /usr/share/fonts/truetype/open-sans/OpenSans-Bold.ttf "vpype!" show`

## Contributing 
Thanks to [Tatarize](https://github.com/tatarize) for creating this plugin in the first place.
If you would like to contribute and expand vpype-ttf, bug reports, feature requests, and issues are welcome.
