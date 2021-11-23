import colorama as cr

cr.init()

def info(msg):
	print(cr.Fore.BLUE+"[INFO] "+cr.Style.RESET_ALL+msg)

def warn(msg):
	print(cr.Fore.YELLOW+"[WARN] "+cr.Style.RESET_ALL+msg)

def err(msg):
	print(cr.Fore.RED+"[ERROR] "+cr.Style.RESET_ALL+msg)
