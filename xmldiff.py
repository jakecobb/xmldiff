#!/usr/bin/env python

from lxml import etree
import sys
import difflib
import optparse
try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO

def xmldiff(old, new, old_name='old', new_name='new', unified=True, **kwargs):
	"""Return a generator yielding a diff of two XML documents.

	The documents are parsed to remove structurally-unnecessary characters, then
	reconstituted into a pretty-printed string.  The generator returned is the
	diff of these cleaned up versions, so the lines correspond more tightly to
	changes in the document structure.

	Extra keyword arguments are those for difflib.unified_diff/context_diff:
	'fromdate', 'todate', 'n', and 'lineterm'
	Other keywords will be silently ignored.

	@param old: the old file, may be a file-like object or a string naming a file
	@param new: the new file, may be a file-like object or a string naming a file
	@param old_name: specify old name in diff, if old is a string then it will be used instead
	@param new_name: specify mew name in diff, if new is a string then it will be used instead
	@param unified: whether to yield a unified diff (default) or a context diff
	@return a diff generator
	"""
	# arg handling
	if isinstance(old, basestring):
		old_name = old
		old = open(old_name, 'rb')
	if isinstance(new, basestring):
		new_name = new
		new = open(new_name, 'rb')

	diff = difflib.unified_diff if unified else difflib.context_diff

	et = etree
	parser = et.XMLParser(remove_blank_text=True) # strip unnecessary whitespace
	try:
		# parse while stripping unnecessary whitespace, then pretty-print to align structure with diff
		oldxml = et.tostring(et.parse(old, parser=parser), encoding='UTF-8', pretty_print=True)
		newxml = et.tostring(et.parse(new, parser=parser), encoding='UTF-8', pretty_print=True)

		diff_args = {'fromfile': old_name, 'tofile': new_name}
		for k, v in kwargs.iteritems():
			if k in ('fromdate', 'todate', 'n', 'lineterm'):
				diff_args[k] = v

		return diff(oldxml.splitlines(), newxml.splitlines(), **diff_args)
	finally:
		try:
			if hasattr(old, 'close'): old.close()
			if hasattr(new, 'close'): new.close()
		except IOError: pass
		
	pass

def xmldiffstr(old, new, old_name='old', new_name='new', unified=True):
	"""Return a generator yielding a diff of two XML documents in string form.
	See xmldiff.xmldiff for the arguments."""
	return xmldiff(StringIO(old), StringIO(new), 
		old_name=old_name, new_name=new_name, unified=unified)

def _parser():
	p = optparse.OptionParser('Usage: %prog [OPTIONS] OLD_FILE NEW_FILE')

	p.add_option('-c', '--context', type='int', default=None, \
		dest='context', help='Number of lines of context.')

	return p

def main(args=None):
	args = args or sys.argv[1:]
	parser = _parser()
	opts, args = parser.parse_args(args)

	if len(args) < 2:
		parser.error('You must specify two files.')
	old, new = args[:2]

	diff_args = {'lineterm': ''} # no newlines in the header
	if opts.context is not None:
		if opts.context < 1:
			parser.error('Context should be a positive integer.')
		diff_args['n'] = opts.context
		
	print '\n'.join(xmldiff(old, new, **diff_args))
	
if __name__ == '__main__':
	main()
