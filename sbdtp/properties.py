from Bio.Alphabet.IUPAC import *
from Bio.Seq import Seq
from google.appengine.ext.db import _CoercingProperty, Text
from types import *

class DNAProperty(_CoercingProperty):
    """A DNA sequence property."""

    data_type = Seq

    def __init__(self, verbose_name=None, alphabet=unambiguous_dna, **kwds):
	"""Construct a DNA property.
	
	Args:
	  verbose_name: Verbose name is always first parameter.
	  alphabet: The Bio.Alphabet type to use as the validation alphabet. Defaults to Bio.Alphabet.IUPAC.IUPACUnambiguousDNA.
	"""
	super(DNAProperty, self).__init__(verbose_name, **kwds)
	if type(alphabet) is ClassType:
	    alphabet = alphabet()
	if not (isinstance(alphabet, IUPACUnambiguousDNA) or isinstance(alphabet, IUPACAmbiguousDNA) or isinstance(alphabet, IUPACExtendedDNA)):
	    raise KindError('alphabet must be instance of IUPACUnambiguousDNA, IUPACAmbiguousDNA or IUPACExtendedDNA')
	self.alphabet = alphabet

    def validate(self, value):
	"""Validate DNA property.
	
	Returns:
	  A valid value.

	Raises:
	  BadValueError if value is not a DNA sequence property. It can be a string or a BioPython Seq object.
	"""
	value = super(DNAProperty, self).validate(value)
        if not frozenset(self.alphabet.letters).issuperset(str(value).upper()):
	    raise BadValueError("Property %s's sequence must consist only of letters [%s] (upper or lowercase)." % (self.name, ''.join(self.alphabet.letters)))
	return self.data_type(str(value), self.alphabet)

    def get_value_for_datastore(self, model_instance):
	sequence = super(DNAProperty, self).get_value_for_datastore(model_instance)
	return Text(str(sequence))

    def make_value_from_datastore(self, value):
	if value is None:
	    return None
	return Seq(value, alphabet)
