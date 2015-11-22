import sys

if not(len(sys.argv) == 3):
  print "Syntax error: python django-docs.py inputfile outputfile"
  exit()
urls_data = open('urls.py').read()
views_data = open(sys.argv[1])
