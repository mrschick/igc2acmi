import traceback as tb
import datetime as dt, zipfile as zf, pprint as pp

# write a program crashdump
def progDump(args, prog, path=""):
	arcName = dt.datetime.now().strftime(prog+"_Crashdump_%Y-%m-%d_%H-%M-%S")
	body = "ERROR LOG "+dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	body += "\n\nARGS:\n"+pp.pformat(args)
	body += "\n\nERROR TRACEBACK:\n"+tb.format_exc()

	with zf.ZipFile(path+arcName+".zip", "a", zf.ZIP_DEFLATED) as zlog:
		zlog.writestr(arcName+".log", body)

	return arcName+".zip"

# write the crashdump for an exception occured while handling a specific file
def fileDump(file, prog, path=""):
	arcName = dt.datetime.now().strftime(prog+"_Crashdump_%Y-%m-%d_%H-%M-%S")
	fname = file+".igc_Exception.log"
	body = "Handled File Name:\n"+file+".igc\n\n"
	body += "Error:\n"+tb.format_exc()

	with zf.ZipFile(path+arcName+".zip", "a", zf.ZIP_DEFLATED) as zlog:
		zlog.writestr(fname, body)

	return arcName+".zip"
