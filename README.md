PyMangaReader
=============

Simple reader for mangas/comics.  
Reads and displays images (manga/comic pages) from directories, zips and rars (only if the [UnRAR] utility is provided).
Supported image formats are jpg, png and gif.

## Features
- Configurable base directories to read mangas from
- Remembers last opened manga/volume/chapter/page between application launches to continue reading where you left off
- Adjustable settings path for storing manga specific settings (last viewed image) for easy synchronisation between devices
- Fullscreen mode
- Rotate image by 90° in either direction
- Various resize filter from fastest (Nearest Neighbor) to best quality (Bicubic)
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
Most Keyboard Hotkeys are freely assignable through the settings dialog, defaults are:

Key | Action
----|-------
Left  | Flip to previous page
Right | Flip to next page
R     | Rotate 90° CW
E     | Rotate 90° CCW
F     | Toggle Fullscreen
H     | Toggle Menu
ESC   | Quit application (or leave fullscreen)

<br />
<p>Resize Filter:</p>

Key | Name | Quality/Speed
----|------|--------------
1 | Nearest Neighbor | Low quality but fastest mode
2 | Bilinear         | Good quality with average speed (linear interpolation in a 2x2 environment)
3 | Bicubic          | Best quality but slow (cubic spline interpolation in a 4x4 environment)
4 | Antialias        | High quality when downsizing but also slow

Mouse | Action
------|-------
Doubleclick (any Button) | Toggle Fullscreen
Wheel                    | Flip to next/previous page

Mouse Shortcuts and Resize Filter Hotkeys aren't freely assignable yet.

## Packages
Precompiled packages for Windows and Linux are available [here][Releases].  
Check the **INSTALL.platform.md** file for installation instructions.  

## License
This software uses following 3rd-party libs:

- [Pillow] ([PIL-License][PILlicense])
- [PyQt5] (GPL v3)
- [rarfile] (ISC)

This software is licensed under the [MIT license].  
© 2013 Jens Schmer

[MIT license]: http://opensource.org/licenses/MIT
[Releases]: https://github.com/jschmer/PyMangaReader/releases
[PILlicense]: http://www.pythonware.com/products/pil/license.htm

[PyQt5]: http://www.riverbankcomputing.co.uk/software/pyqt/download5
[rarfile]: https://pypi.python.org/pypi/rarfile/
[UnRAR]: http://www.rarlab.com/rar_add.htm
[Pillow]: https://pypi.python.org/pypi/Pillow/2.0.0