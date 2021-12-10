import pathlib as pl
from common import console as c

# current release version
version = "v0.2 - 2021.12.10"

# common arguments that every program uses
def addDefaultArgs(parser):
	parser.add_argument(
		"--version",
		action = "store_true",
		help = 'print current version number+date'
	)
	parser.add_argument(
		"-r",
		"--remove",
		action = "store_true",
		help = 'Remove ".igc" files after converting them'
	)
	parser.add_argument(
		"-z",
		"--nozip",
		action = "store_true",
		help = 'Do not compress output files as ".zip.acmi", instead output ".txt.acmi", useful for debugging'
	)
	parser.add_argument(
		"-d",
		"--debug",
		action = "store_true",
		help = "Do not zip crashdumps, instead output error messages normally, useful for debugging"
	)
	parser.add_argument(
		"-o",
		"--output",
		type = str,
		default = "",
		help = "Output path for acmi file(s)"
	)

	return parser

def parseArgPath(path, pathName="Argument"): # parses paths received from cmd arguments, checks if they are valid and properly formats them
	p = pl.Path(path).resolve()
	if p.is_file():
		return p.parent.as_posix()+"/"
	elif p.is_dir():
		return p.as_posix()+"/"
	else:
		# if path is not valid, set it to script's location and notify user
		c.warn(pathName+" path is not valid, defaulting to current program directory")
		return pl.Path(__name__).resolve().parent.as_posix()+"/"
