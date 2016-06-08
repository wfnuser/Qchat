import re

def main():
	hreflist = re.search(r'(?<=href=")[\w,?,=]*', '<a href="bbsqry?userid=lawa">lawa</a><')
	print(hreflist.group())

main()
        