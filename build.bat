@echo off

pyinstaller --specpath "build" --distpath "build\dist" -p "." --clean -F -i NONE --exclude-module _bootlocale "igc2acmi\igc2acmi.py"

pyinstaller --specpath "build" --distpath "build\dist" -p "." --clean -F -i NONE --exclude-module _bootlocale "convert-all-igcs\convert-all-igcs.py"

pyinstaller --specpath "build" --distpath "build\dist" -p "." --clean -F -i NONE --exclude-module _bootlocale "combine-igcs\combine-igcs.py"

pause