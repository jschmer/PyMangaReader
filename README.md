PyMangaReader
=============

Simple reader for mangas/comics.  
Reads images (manga/comic pages) from directories, zips and rars (only if the UnRAR utility is provided).
Supported image formats are jpg, png and gif.

## Features
- Configurable base directories to read mangas from
- Remembers last opened manga/volume/chapter/page between application launches to continue reading where you left off
- Adjustable settings path for storing manga specific settings (last viewed image) for easy synchronisation
- Fullscreen mode
- Rotate image by 90° in either direction
- Seamless navigation through the pages, you'll get notified if a new chapter or volume begins
- Nested archives possible (e.g. zips in zip or zips in rar, rar in other archive isn't supported!)
- Freely configurable Keyboard Shortcuts

Works best with following directory/archive hierarchy:
```
MangaName (directory or archive)
|- Volume 1 (dir or archive)
|  |- chapter 1 (dir or archive)
|  |  |- Page 1 (image)
|  |  |- Page ... (image)
|  |- chapter ...
|- Volume ...
```
but can also handle shallower hierarchies.

## Hotkeys
Keyboard Hotkeys are freely assignable through the settings dialog, defaults are:

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

Mouse Shortcuts aren't freely assignable yet.

## Packages
Precompiled packages for Windows and Linux are available [here][Releases].  
Check the **INSTALL.platform.md** file for installation instructions.  

## License
This software is licensed under the [MIT license].  
© 2013 Jens Schmer

[MIT license]: http://opensource.org/licenses/MIT
[Releases]: https://github.com/jschmer/PyMangaReader/releases
