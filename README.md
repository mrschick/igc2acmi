# igc2acmi
A set of tools to convert [XCSoar](https://github.com/XCSoar/XCSoar#readme)'s, [FLARM](https://flarm.com/)'s and multiple other vendors' `.igc` GPS flight logs into [Tacview](https://www.tacview.net/)'s `.acmi` format.

## The Goal
`.igc` is simple format, useful for recording the flight of a single aircraft, but has its limits.

`.klm`, which can be parsed from `.igc` using other [online utilities](http://cunimb.net/igc2kml.php), may be more visually appealing when viewed in Google Earth, but still isn't as useful for flight debriefing as I'd like to.

For these reasons, I decided to develop igc2acmi, it converts one or more `.igc` logs into [Tacview](https://www.tacview.net/)'s `.acmi` flight recording format, which is specifically designed to efficiently store multiple GPS tracks, its software also provides very useful debriefing features such as:
- customizable labels to display AMSL/AGL Altitude, Vertical Speed, Calibrated Air Speed, True Airspeed, etc.
- dynamic distance indication between 2 aircraft
- custom [terrain textures](https://www.tacview.net/documentation/terrain/en/) and [3D shapes](https://www.tacview.net/documentation/staticobjects/en/), which can be used to display aviation charts and airspace models:
![Tacview flight with custom terrain and airspace shapes](http://fabioschick.altervista.org/img/igc2acmi-Tacview-TerrainAirspace.png)
- online debriefs, where multiple people can observe a flight from a shared perspective

## The Programs
the `ProgramName.exe` `-h`/`--help` command will explain the different command-line arguments of each program.

### igc2acmi
converts a single `.igc` file into `.acmi`, useful when you want to convert a specific file using specific settings.

### convert-all-igcs
converts all `.igc` files in the program's directory (or a given input path) into an equal number of `.acmi` files. Useful when you need to convert multiple flights at once, all with the same settings.

### combine-igcs
arguably the most complex utility of the 3, it finds all `.igc` files in the program's directory (or a given input path), sorts them by date of flight and combines all flights started on the same date into a single `.acmi` file, the timeline starts with the first GPS fix of the first flight and ends with the last fix of the last one.

Aeroclubs may find the greatest utility in this feature, for example by collecting everyone's `.igc` (with pilot consent of course) every day and combining them, to store/archive flights for collective debriefs and/or longer-term analysis of pilot activity.

## Known limitations
Until now, I have only tested my project on `.igc` logs recorded by XCSoar (my own) and FLARM (a collegue's). All of the FLARM logs had an invalid date field of "000000" in their header, which the programs are not capable of handling (yet).

Maybe that has been resolved by newer FLARM versions, or was caused by incorrect setup of the FLARM module. In the meantime, make sure your `.igc` files have a valid date in their "HFDTE" line, using the "DDMMYY" format (i.e: "HFDTE221121" for 22nd November 2021).

## Sources and How to Contribute
Development of this project was significantly aided by available documentation for the [igc](https://xp-soaring.github.io/igc_file_format/igc_format_2008.html) and [acmi](https://www.tacview.net/documentation/acmi/en/) file formats, many thanks to their authors.

The [released executables](https://github.com/RUSHER0600/igc2acmi/releases) are compiled with [pyinstaller](https://www.pyinstaller.org/) using [build.bat](build.bat).

Feel free to fork this project for your own uses, any Pull Requests back to the original repository would be greatly appreciated!

## To-Do List
- [x] Add `--version` command that displays version number (and maybe release date)
- [ ] Implement parsing of `igc` [tasks](https://xp-soaring.github.io/igc_file_format/igc_format_2008.html#link_3.6) and [events](https://xp-soaring.github.io/igc_file_format/igc_format_2008.html#link_4.2) into `acmi` [events](https://www.tacview.net/documentation/acmi/en/#Events)
- [ ] Improve and augment error handling, i.e: for flights with missing/invalid date fields in their header
- [ ] Add a way for the user to determine the output file's name or name template