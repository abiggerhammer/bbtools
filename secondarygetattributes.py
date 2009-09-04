from lxml import etree
import logging, os, os.path, sys, urllib2

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    if os.path.exists("%s/features" % os.getcwd()):
	problems = []
	for xmlfile in os.listdir("%s/features" % os.getcwd()): 
	    if 'xml' in os.path.splitext(xmlfile)[1]:
	        logging.debug("Working on %s" % xmlfile)
		try:
		    tree = etree.parse("%s/features/%s" % (os.getcwd(), xmlfile))
		except:
		    logging.warn("lxml can't parse %s, skipping" % xmlfile)
		    problems.append(xmlfile)
		    continue
	    	root = tree.getroot()
	    	for brick in root.iterdescendants(tag='TYPE'):
		    if 'BioBrick' == brick.text:
		    	brickname = brick.getparent().get('label')
			if brickname.startswith('BBa') or brickname.startswith('pS'):
			    if not os.path.exists("%s/features/%s_features.xml" % (os.getcwd(), brickname)) or not os.path.exists("%s/sequences/%s_sequence.xml" % (os.getcwd(), brickname)):
			    	features = urllib2.urlopen('http://partsregistry.org/das/parts/features?segment=%s' % brickname)
			    	sequence = urllib2.urlopen('http://partsregistry.org/das/parts/dna?segment=%s' % brickname)
			    	featuref = open("%s/features/%s_features.xml" % (os.getcwd(), brickname), 'w')
			    	sequencef = open("%s/sequences/%s_sequence.xml" % (os.getcwd(), brickname), 'w')
			    	for line in features:
			    	    featuref.write(line)
			    	features.close()
			    	featuref.close()
			    	logging.info("Wrote features for %s" % brickname)
			    	for line in sequence:
			    	    sequencef.write(line)
			    	sequence.close()
			    	sequencef.close()
			    	logging.info("Wrote sequence for %s" % brickname)
		    	    else:
			    	logging.debug("Already got %s, skipping" % brickname)
	logging.warn("We had problems with the following:")
	[logging.warn("    %s" % problem) for problem in problems]

