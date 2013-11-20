PyMangaReader
=============

Simple reader for mangas.  
Reads images (manga pages) from directories, zips and rars (only if the UnRAR utility is provided).
Supported image formats are jpg, png and gif.

## Features
- Configurable base directories to read mangas from
- Adjustable settings path for storing manga specific settings for easy synchronisation
- Remembers last opened manga/volume/chapter/page between application launches to continue reading where you left off
- Fullscreen mode
- Rotate image by 90° in either direction
- Seamlessly navigate through the pages, you'll get notified if a new chapter or volume begins

Works best with following directory/archive hierarchy:
```
MangaName (directory)
|- Volume 1 (dir or archive)
|  |- chapter 1 (dir or archive)
|  |  |- Page 1 (image)
|  |  |- Page ... (image)
|  |- chapter ...
|- Volume ...
```
but can also handle shallower hierarchies.

## Hotkeys
Key | Action
----|------
Left  | Flip to previous page
Right | Flip to next page
R     | Rotate 90° CW
E     | Rotate 90° CCW
F     | Toggle Fullscreen
H     | Toggle Menu
ESC   | Quit application (or leave fullscreen)

Mouse | Action
------|------
Doubleclick  | Toggle Fullscreen
Wheel        | Flip to next/previous page

## Packages
Precompiled packages for Windows and Linux are available [here][Releases].  
Check the **INSTALL.platform.md** file for installation instructions.  

## License
This software is licensed under the [MIT license].  
© 2013 Jens Schmer

[MIT license]: http://opensource.org/licenses/MIT
[Releases]: https://github.com/jschmer/PyMangaReader/releases
