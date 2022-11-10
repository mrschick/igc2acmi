import sys, argparse, pathlib as pl, traceback as tb
sys.path.append(str(pl.Path(__file__).resolve().parents[1]))
from common import functions as fnc, crashdumping as dump, args as a, console as c

def main():
	parser = argparse.ArgumentParser(
		"convert-all-igcs.exe",
		description = "Use it to convert all .igc files in a directory into .acmi"
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
	# parse all arguments
	args = parser.parse_args()

	if args.version:
		print(a.version)
		return

	try:
		# define input path
		inPath = a.parseArgPath(args.input, "Input")
		# define output path
		outPath = a.parseArgPath(args.output, "Output")

		igcs = fnc.listIGCs(inPath)
		if len(igcs) == 0:
			c.warn("No .igc files found in \""+inPath+"\"")
			return

		for igcName in igcs:
			try:
				# init input and output file streams
				igc = open(inPath+igcName+".igc", "r")
				acmi = open(outPath+igcName+".tmpacmi", "w")

				# parse IGC header and initialize ACMI header
				header = fnc.getFlightHeader(inPath+igcName+".igc")
				acmi.write(fnc.acmiFileInit(header["firstfixtime"]))
				acmi.write(fnc.acmiObjInit(header))

				# parse IGC GPS data lines and write to ACMI
				for line in igc:
					if line.startswith("B"):
						fixTime = fnc.parseFixTime(line)
						lat, lon, alt = fnc.parseFixLocation(line)

						tOffset = str(fnc.timeDiff(header["firstfixtime"].time(), fixTime))
						acmi.write("#"+tOffset+"\n1000,T="+lon+"|"+lat+"|"+str((int(alt)+args.altdelta))+"\n")

				igc.close()
				acmi.close()

				# handle other optional arguments
				if args.remove:
					pl.Path(inPath+igcName+".igc").unlink()
					c.info("Removed "+igcName+".igc")
				if args.nozip:
					pl.Path(outPath+igcName+".tmpacmi").replace(outPath+igcName+".txt.acmi")
					ext = ".txt.acmi"
				else:
					fnc.zipAcmi(outPath+igcName)
					ext = ".zip.acmi"

				c.info("Converted: \""+outPath+igcName+ext+"\"")
			except:
				if "igcName" in locals(): # clean up initialized ".tmpacmi" file in case of a crash
					if not acmi.closed: # if tmpacmi is still open, close it
						acmi.close()
					pl.Path(outPath+igcName+".tmpacmi").unlink()
				if args.debug: # if debug flag is set, print normal error message
					c.err("Unable to convert \""+igcName+".igc\", error:\n"+tb.format_exc())
				else: # default crashdump writing
					c.err("Unable to convert \""+igcName+".igc\", a crashlog for it has been saved in \""+dump.fileDump(igcName, "conv-all-igcs")+"\"")

	except:
		if args.debug: # if debug flag is set, print normal error message
			c.err(tb.format_exc())
		else: # default crashdump writing
			c.err("An error occured in this program's execution, a crash report has been saved to \""+dump.progDump(args, "conv-all-igcs")+"\"")

main()