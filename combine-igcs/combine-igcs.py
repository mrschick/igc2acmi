import sys, argparse, pathlib as pl, traceback as tb, datetime as dt
sys.path.append(str(pl.Path(__file__).resolve().parents[1]))
from common import functions as fnc, crashdumping as dump, args as a, console as c

def listIGCsByDate(path, igcs): # builds a dict of igc files, the key is the date of flight, the value is a list containing all igc filepaths recorded on that date
	ret = {}
	for igc in igcs:
		date = fnc.getFlightDate(path+igc+".igc")
		if date in ret:
			ret[date].append(path+igc+".igc")
		else:
			ret[date] = [path+igc+".igc"]
	return ret

def getLowestRefTime(igcs): # from a list of igc filepaths, find the one with the lowest first fix time and return that time as a time object
	lowest = dt.time(23, 59, 59)

	for igcpath in igcs:
		with open(igcpath) as igc:
			for line in igc:
				if line.startswith("B"):
					fixTime = dt.time(
						int(line[1:3]),
						int(line[3:5]),
						int(line[5:7])
					)
					break
			if fixTime < lowest:
				lowest = fixTime

	return lowest

def getLastFix(acs): # returns the highest occuring "lastfix" value among all aircraft dicts
	lastfix = 0
	for id in acs:
		if acs[id]["lastfix"] > lastfix:
			lastfix = acs[id]["lastfix"]

	return lastfix

def getFixes(filename, refTime): # returns a list of fix dictionaries: key is the time offset from reference time in seconds, values are lat/lon/alt
	ret = {}
	with open(filename) as igc:
		for line in igc:
			if line.startswith("B"):
				fix = fnc.parseFixLocation(line)
				fixTime = fnc.parseFixTime(line)
				ret[fnc.timeDiff(refTime, fixTime)] = {
					"lat": fix[0],
					"lon": fix[1],
					"alt": fix[2]
				}
	return ret

def buildAircraft(igcs, refTime): # builds the main data dict of aircraft, with one element for each IGC file read.
	i = 0
	ac = {}

	for igcPath in igcs:
		i += 1
		fixes = getFixes(igcPath, refTime)
		fixKeys = list(fixes.keys())
		ac[1000+i] = {
			"header": fnc.getFlightHeader(igcPath),
			"firstfix": fixKeys[0],
			"beflastfix": fixKeys[-2],
			"lastfix": fixKeys[-1],
			"fixes": fixes
		}

	# bubble sort aircraft dict, so that the first aircraft recorded is the first aircraft ID
	ids = list(ac.keys())
	done = False
	while not done:
		done = True
		for i in range(0, len(ids)-1):
			if ac[ids[i]]["firstfix"] > ac[ids[i+1]]["firstfix"]:
				tmp = ac[ids[i]]
				ac[ids[i]] = ac[ids[i+1]]
				ac[ids[i+1]] = tmp
				done = False

	return ac


def main():
	parser = argparse.ArgumentParser(
		"combine-igcs.exe",
		description = "Use it to combine multiple .igc files recorded on the same day into a single .acmi, containing all aircraft"
	)
	# import common arguments
	parser = a.addDefaultArgs(parser)
	# set program-specific arguments
	parser.add_argument(
		"-i",
		"--input",
		type = str,
		default = "",
		help = "Input path for igc files"
	)
	parser.add_argument(
		"-n",
		"--name",
		type = str,
		default = "",
		help = "Desired filename for ACMI file, will only be applied to the first file to be handled"
	)
	# parse all arguments
	args = parser.parse_args()

	try:
		# define input path
		inPath = a.parseArgPath(args.input, "Input")
		# define output path
		outPath = a.parseArgPath(args.output, "Output")

		# list available .igc files by their date and parse an acmi for each day
		igcs = listIGCsByDate(inPath, fnc.listIGCs(inPath))
		if None in igcs: # if .igc files with no valid date header line have been found, list them as corrupted and remove them from the dictionary
			c.warn("The following files have no valid date header line and will not be converted:")
			for file in igcs[None]:
				print("\""+file+"\"")
			igcs.pop(None)

		for date in igcs:
			try:
				# initialize data structure of flights on x date
				refTime = dt.datetime.combine(
					dt.datetime.strptime(str(date), "%y%m%d"),
					getLowestRefTime(igcs[date])
				)
				c.info("Handling flights of date: "+refTime.strftime("%d %b %Y"))
				acs = buildAircraft(igcs[date], refTime.time())

				# default to ACMI name "YYYY-MM-DD_Callsign1_Callsign2_..." if filename argument is not set or already taken
				if args.name != "" and not sorted(pl.Path(args.output).glob(args.name+".*")):
					acmiName = args.name
				else:
					acmiName = refTime.strftime("%Y-%m-%d")
					for id in acs:
						if acs[id]["header"]["callsign"] not in acmiName:
							acmiName += "_"+acs[id]["header"]["callsign"]

				# init ACMI file for date x
				acmi = open(outPath+acmiName+".tmpacmi", "w")
				acmi.write(fnc.acmiFileInit(refTime))

				# init Aircraft objects on ACMI
				for id in acs:
					acmi.write(fnc.acmiObjInit(acs[id]["header"], id))

				# write Aircraft fix positions to ACMI, grouped by time offset to refTime
				i = 0
				while i <= getLastFix(acs):
					rec = ""
					for id in acs:
						if i in acs[id]["fixes"]:
							# if current time offset is first fix of aircraft, pass ACMI "flight start" event
							if i == acs[id]["firstfix"]:
								rec += "0,Event=Message|"+str(id)+"|flight started\n"

							# pass aircraft's current position fix
							fix = acs[id]["fixes"][i]
							rec += str(id)+",T="+fix["lon"]+"|"+fix["lat"]+"|"+fix["alt"]+"\n"

							# if current time offset is before-last / last fix of aircraft, pass "flight end" event and ACMI object deletion
							if i == acs[id]["beflastfix"]:
								rec += "0,Event=Message|"+str(id)+"|flight ended\n"
							if i == acs[id]["lastfix"]:
								rec += "-"+str(id)+"\n"

					if rec != "":
						acmi.write("#"+str(i)+"\n"+rec)
					i += 1

				acmi.close()

				# handle other optional arguments
				if args.remove:
					for igc in igcs[date]:
						pl.Path(igc).unlink()
						c.info("Removed "+pl.Path(igc).name)
				if args.nozip:
					ext = ".txt.acmi"
					pl.Path(outPath+acmiName+".tmpacmi").replace(outPath+acmiName+ext)
				else:
					ext = ".zip.acmi"
					fnc.zipAcmi(outPath+acmiName)

				c.info("Combined the following files into \""+outPath+acmiName+ext+"\":")
				for igc in igcs[date]:
					print("\""+igc+"\"")

			except:
				if "acmi" in locals(): # clean up initialized ".tmpacmi" file in case of a crash
					if not acmi.closed: # if tmpacmi is still open, close it
						acmi.close()
					pl.Path(outPath+acmiName+".tmpacmi").unlink()
				if args.debug: # if debug flag is set, print normal error message
					c.err("Unable to combine flights of date "+refTime.strftime("%d %b %Y")+", error:\n"+tb.format_exc())
				else: # default crashdump writing
					c.err("Unable to convert flights of date "+refTime.strftime("%d %b %Y")+", a crashlog for it has been saved in \""+dump.fileDump(acmiName, "combine-igcs")+"\"")

	except:
		if args.debug: # if debug flag is set, print normal error message
			c.err(tb.format_exc())
		else: # default crashdump writing
			c.err("An error occured in this program's execution, a crash report has been saved to \""+dump.progDump(args, "combine-igcs")+"\"")

main()