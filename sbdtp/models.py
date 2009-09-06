from google.appengine.ext import db
from properties import DNAProperty

class SBO(db.Model):
    id = db.IntegerProperty(required=True)
    type = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    shortDesc = db.StringProperty()

standards = frozenset([10, 15, 21, 23, 25, 28])
def validateAssembly(value):
    if not standards.issuperset(value):
	raise BadValueError('Invalid assembly standard specification number(s): %s' % ', '.join([str(x) for x in set(value).difference(standards)]))
    return value

class BasicPart(SBO):
    length = db.IntegerProperty(required=True)
    sequence = DNAProperty(required=True)
    status = db.StringProperty(required=True)
    assemblyStandard = db.ListProperty(int, validator=validateAssembly)
    # we also get a free back-reference, named feature_set

class CompositePart(BasicPart):
    componentParts = db.StringListProperty()	# component part names

class Feature(db.Model):
    id = db.IntegerProperty(required=True)
    label = db.StringProperty()
    type = db.StringProperty(required=True)
    start = db.IntegerProperty(required=True)
    end = db.IntegerProperty(required=True)
    part = db.ReferenceProperty(BasicPart)

