import datetime as dt
import zipfile as zf
import pathlib as pl


# FILE NAME/PATH PARSING

def listIGCs(dir): # finds all .igc file names in selected directory, and returns them without extension
	p = pl.Path(dir).resolve()
	igcFiles = []
	for child in p.iterdir():
		if child.is_file() and child.suffix.casefold() == ".igc":
			igcFiles.append(child.stem)

	return igcFiles

def parsePathName(pathArg): # given a full file path, it returns a tuple of: parent-path, filename, file extension
	p = pl.Path(pathArg).resolve()
	if p.is_file():
		return (
			p.parent.as_posix()+"/",
			p.stem,
			p.suffix
		)
	elif p.is_dir():
		return (p.as_posix()+"/", False, False)
	else:
		return (False, False, False)


# IGC FILE PARSING

def getFlightDate(igc): # takes a .igc filepath and only returns the date in YYMMDD format as an integer, for quicker sorting later on
	with open(igc) as f:
		for line in f:
			if line.startswith("HFDTE"):
				if ":" in line:
					d = line.split(":")[1].strip("\n")
					return int(d[4:]+d[2:4]+d[:2])
				else:
					return int(line[9:11]+line[7:9]+line[5:7])

def getFlightHeader(filename): # takes a .igc filepath and returns header data as a dictionary, along with the plane's first location fix's time
	tmp = {}
	igc = open(filename, "r")

	for line in igc:
		if line.startswith("H"):
			if ":" in line:
				key, value = line.split(":")
				if value == "undefined\n":
					value = ""
				tmp[key[:5]] = value.strip("\n")
			else:
				tmp[line[:5]] = line[5:].strip("\n")
		elif line.startswith("B"):
			fixTime = dt.datetime(
				int("20"+tmp["HFDTE"][4:]), # year
				int(tmp["HFDTE"][2:4]), # month
				int(tmp["HFDTE"][:2]), # day
				int(line[1:3]), # hour
				int(line[3:5]), # minute
				int(line[5:7]), # second
				tzinfo = dt.timezone.utc
			)
			break
	igc.close()

	# reformat header data
	header = {}
	header["firstfixtime"] = fixTime

	if tmp["HFGTY"] == "":
		header["actype"] = "Glider"
	else:
		header["actype"] = tmp["HFGTY"]

	if tmp["HFGID"] == "":
		header["callsign"] = "NoCallsign"
	else:
		header["callsign"] = tmp["HFGID"]

	# if there is a second crewmate, concatenate it with the pilot name
	if "HFCM2" not in tmp or tmp["HFCM2"] == "":
		header["pilot"] = tmp["HFPLT"]
	else:
		header["pilot"] = tmp["HFPLT"]+" | "+tmp["HFCM2"]

	return header


# ACMI FILE PARSING

def acmiFileInit(refDateTime): # takes reference datetime object and returns the first 3 acmi lines
	return "FileType=text/acmi/tacview\nFileVersion=2.1\n0,ReferenceTime="+refDateTime.strftime("%Y-%m-%d")+"T"+refDateTime.strftime("%H:%M:%S")+"Z\n"

def acmiObjInit(header, id=1000): # takes a parsed .igc header and returns the respective ACMI object init line
	return str(id)+",Name="+header["actype"]+",CallSign="+header["callsign"]+",Pilot="+header["pilot"]+"\n"

def zipAcmi(fname, remove=True): # takes the ".tmpacmi" file's name and compresses it, if remove is set as True, delete the ".tmpacmi" file at the end
	zipacmi = zf.ZipFile(fname+".zip.acmi", "w", zf.ZIP_DEFLATED)
	zipacmi.write(fname+".tmpacmi", fname+".txt.acmi")
	zipacmi.close()
	if remove:
		pl.Path(fname+".tmpacmi").unlink()


# TIME PARSING

def timeDiff(t1, t2): # takes 2 time objects and returns their difference in seconds, works across midnight too
	t1 = dt.datetime.combine(dt.datetime.min, t1)
	t2 = dt.datetime.combine(dt.datetime.min, t2)

	tdelta = t2 - t1
	if tdelta.days < 0:
		tdelta = dt.timedelta(days = 0, seconds = tdelta.seconds)

	return tdelta.seconds

def parseFixTime(b): # receives an .igc "B"(fix) line and returns its "HHMMSS" timestamp as a time object, for further handling by the code
	return dt.datetime.strptime(b[1:7], "%H%M%S").time()


# COORDINATE PARSING

def dm2dd(d, m): # takes a DM coordinate and returns the respective DD coordinate, rounded to 5 positions (igc format's max precision) and converted to string
	dd = int(d) + float(m[:2]+"."+m[2:]) / 60
	return str(round(dd, 5))

def parseFixLocation(b): # receives an .igc "B"(fix) line and returns Lat, Lon, Alt parsed (and converted from DM to DD) for Tacview
	ret = []
	#lat
	if b[14] == "N":
		ret.append(dm2dd(b[7:9], b[9:14]))
	elif b[14] == "S":
		ret.append(dm2dd("-"+b[7:9], b[9:14]))
	#lon
	if b[23] == "E":
		ret.append(dm2dd(b[15:18], b[18:23]))
	elif b[23] == "W":
		ret.append(dm2dd("-"+b[15:18], b[18:23]))
	#alt
	ret.append(b[30:35].lstrip("0"))

	return ret
