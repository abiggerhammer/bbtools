from Bio import SeqIO
from lxml import etree

import logging, logging.handlers, os, os.path
from optparse import OptionParser

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub
from models import BasicPart, CompositePart, Feature

logging.basicConfig(level=logging.INFO)
logfile = logging.FileHandler('warnings.log', 'w')
logfile.setLevel(logging.WARNING)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
logfile.setFormatter(formatter)
logging.getLogger('').addHandler(logfile)
partlogger = logging.getLogger('part')
seqlogger = logging.getLogger('sequence')
xmllogger = logging.getLogger('lxml.etree')

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
	partlogger.warning("Part %s has an invalid status, skipping" % fasta.name)
	return None
    if 'D' == status:
	partlogger.warning("Part %s was deleted, skipping" % fasta.name)
	return None
    type = pieces[3]
    # fetch DAS info, decide if basic or composite
    try:
	tree = etree.parse('%s?segment=%s' % (options.das, fasta.name))
    except:
	xmllogger.warning('Invalid features XML for %s' % fasta.name)
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
    optp.add_option("-f", "--features", dest="featuredir", help="Directory of XML files with feature info")
    optp.add_option("-s", "--datastore", dest="datastore", help="Path to the file to store datastore file stub data in", default=os.path.join(os.getcwd(), "datastore"))
    optp.add_option("-b", "--history", dest="history", help="Path to the file to store datastore history in", default=os.path.join(os.getcwd(), "history"))
    optp.add_option("-c", "--clear", action="store_true", dest="clear_datastore", help="Clear the datastore before starting (off by default)", default=False)
    (options, args) = optp.parse_args()

    if not options.fastafile or not os.path.exists(options.fastafile):	
	sys.exit('Error: FASTA file to process not specified or not found')
    if (not options.das and not options.featuredir) or (options.das and options.featuredir):
	sys.exit('Error: you must provide either a URL to a DAS server or a directory to search for feature files, but not both')

    os.environ['APPLICATION_ID'] = 'biobrickparts'

    if options.clear_datastore:
	for path in (options.datastore, options.history):
	    if os.path.lexists(path):
		logging.info('Attempting to remove file at %s', path)
		try:
		    os.remove(path)
		except OSError, e:
		    logging.warning('Removing file failed: %s', e)

    apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
    datastore = datastore_file_stub.DatastoreFileStub('biobrickparts', options.datastore, options.history, require_indexes=False, trusted=False)
    apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', datastore)    

    fastas = SeqIO.parse(open(options.fastafile), 'fasta')
    for fasta in fastas:
	if 0 == len(fasta.seq):
	    seqlogger.warning("Part %s has a sequence of length 0, skipping" % fasta.name)
	    continue
	part = makePart(fasta)
	if not part:
	    continue
        logging.info("Wrote %s" % part.name)
