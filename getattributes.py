from lxml import etree
import logging, os, os.path, sys, urllib2

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    tree = etree.parse(sys.argv[1])
    root = tree.getroot()
    logging.info("Got %d segments" % len(root.findall('.//SEGMENT')))
    for segment in root.iterdescendants(tag='SEGMENT'):
	if os.path.exists('%s/sequences/%s_sequence.xml' % (os.getcwd(), segment.text)):
	    logging.info("%s already retrieved, skipping" % segment.text)
	    continue
	features = urllib2.urlopen("http://partsregistry.org/das/parts/features?segment=%s" % segment.text)
	sequence = urllib2.urlopen("http://partsregistry.org/das/parts/dna?segment=%s" % segment.text)
	featuref = open('%s/features/%s_features.xml' % (os.getcwd(), segment.text), 'w')
	sequencef = open('%s/sequences/%s_sequence.xml' % (os.getcwd(), segment.text), 'w')
	for line in features:
	    featuref.write(line)
	features.close()
	featuref.close()
	logging.info("Wrote %s_features.xml" % segment.text)
	for line in sequence:
	    sequencef.write(line)
	sequence.close()
	sequencef.close()
	logging.info("Wrote %s_sequence.xml" % segment.text)

