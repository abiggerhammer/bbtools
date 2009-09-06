from Bio import SeqIO
from lxml import etree

import logging, os, os.path
from optparse import OptionParser

from models import BasicPart, CompositePart, Feature

logging.basicConfig(level=logging.DEBUG)

statuses = {'A': 'Available', 'B': 'Building', 'D': 'Deleted', 'L': 'Length OK', 'M': 'Missing', 'P': 'Planning', 'U': 'Unavailable'}

def makeFeature(feature):
    ret = Feature(id=int(feature.get('id')),
                  label=feature.get('label'),
                  type=feature.findtext("TYPE"),
                  start=int(feature.findtext("START")),
                  end=int(feature.findtext("END")))
    return ret

def makePart(fasta):
    tuple = fasta.description.split('"')
    description = tuple[1]
    pieces = tuple[0].split()
    status = statuses.get(pieces[1])
    if not status:
	return None
    type = pieces[3]
    # fetch DAS info, decide if basic or composite
    try:
	tree = etree.parse('%s?segment=%s' % (options.das, fasta.name))
    except:
	logging.warn('Invalid features XML for %s' % fasta.name)
	return None
    root = tree.getroot()
    components = []
    features = []
    for feature in root.iterfind(".//TYPE[@category='translation']"):
	newFeature = makeFeature(feature.getparent())
	features.append(newFeature)
	if 'BioBrick' == newFeature.type and (newFeature.label.startswith('BBa') or newFeature.label.startswith('pS')):
	    components.append(newFeature.label)
    if 'Composite' == type or len(components) > 0:
#	logging.debug("id=%s, type=%s, name=%s, shortDesc=%s, length=%d, sequence=%s, status=%s, components=%s" % (pieces[2], type, fasta.name, tuple[1], len(fasta.seq), fasta.seq, status, str(components)))
	part = CompositePart(id=int(pieces[2]),
			     type=type,
			     name=fasta.name,
			     shortDesc=tuple[1],
			     length=len(fasta.seq),
			     sequence=fasta.seq,
			     status=status,
			     componentParts=components)
    else:
	part = BasicPart(id=int(pieces[2]),
    			 type=type,
    			 name=fasta.name,
    			 shortDesc=tuple[1],
    			 length=len(fasta.seq),
    			 sequence=fasta.seq,
    			 status=status)
    part.put()
    # TODO: how do we get the assembly standards?
    for feature in features:
	feature.part = part
	feature.put()
    return part

if __name__=='__main__':
    optp = OptionParser()
    optp.add_option("-i", "--input", dest="fastafile", help="FASTA data to parse")
    optp.add_option("-d", "--das", dest="das", help="DAS URL to query for feature info, e.g. http://partsregistry.org/das/parts/features")
    optp.add_option("-f", "--features", dest="featuredir", help="directory of XML files with feature info")
    (options, args) = optp.parse_args()

    if not options.fastafile or not os.path.exists(options.fastafile):	
	sys.exit('Error: FASTA file to process not specified or not found')
    if (not options.das and not options.featuredir) or (options.das and options.featuredir):
	sys.exit('Error: you must provide either a URL to a DAS server or a directory to search for feature files, but not both')

    os.environ['APPLICATION_ID'] = 'biobrickparts'

    fastas = SeqIO.parse(open(options.fastafile), 'fasta')
    for fasta in fastas:
	part = makePart(fasta)
	if not part:
	    logging.warn("Failed to write part for %s" % fasta.name)
	    continue
        logging.info("Wrote %s" % part.name)
