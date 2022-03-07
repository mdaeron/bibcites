'''
CLI to insert number of citations into BibTeX entries, using OpenCitations
'''

__author__	= 'Mathieu Daëron'
__contact__   = 'mathieu@daeron.fr'
__copyright__ = 'Copyright (c) 2022 Mathieu Daëron'
__license__   = 'Modified BSD License - https://opensource.org/licenses/BSD-3-Clause'
__date__	  = '2022-03-06'
__version__   = '1.1.1'

import opencitingpy
import bibtexparser
from bibtexparser.bparser import BibTexParser

import click

@click.command()
@click.argument('bibfile')
@click.option('-o', default='_', help='output BibTex file\n')
@click.option('-f',
	default='[{:s}~citations]',
	help='format of text to save to \'addendum\' field\n',
	)
@click.option('-s', default=False, is_flag=True, help='print list sorted by cites\n')
@click.option('-v', default=False, is_flag=True, help='enable verbose output\n')
@click.option('-t', default=[], multiple=True, help='only process entries of this type (may be used several times to process several types)\n')
def cli(bibfile, o, s, f, v, t):
	'''
	Reads a BibTeX file (BIBFILE), finds entries with a DOI, looks up the corresponding
	number of citations using OpenCitations (https://opencitations.net), saves this
	number to the 'addendum' field of each entry, and writes results to a new BibTex file.
	
	Optionally, using option -s, print out a list of entries with DOI sorted
	by number of citations.
	'''
	
	t = [_.lower() for _ in t]
	
	## read BibTeX file
	with open(bibfile) as bibtex_file:
		parser = BibTexParser(common_strings = True)
		db = bibtexparser.load(bibtex_file, parser=parser)
	if v:
		print(f'Read {len(db.entries)} entries from {bibfile}.')

	## dict of entries with a DOI	
	dbe = {e['doi']: e for e in db.entries if 'doi' in e and (len(t) == 0 or e['ENTRYTYPE'].lower() in t)}
	if v:
		if t:
			tlist = [f'"{_}"' for _ in t]
			if len(tlist) == 1:
				tlist = tlist[0]
			elif len(tlist) == 2:
				tlist = tlist[0] + ' or ' + tlist[1]
			else:
				tlist[-1] = 'or ' + tlist[-1]
				tlist = ', '.join()
			print(f'Found {len(dbe)} entries of type {tlist} with a DOI.')
		else:
			print(f'Found {len(dbe)} entries with a DOI.')
	
	if v:
		print(f'Querying OpenCitations...')
	metadata = opencitingpy.client.Client().get_metadata([doi for doi in dbe])
	if v:
		print(f'Read {len(metadata)} records from OpenCitations.')

	for k in metadata:
		for j in dbe:
			if j.upper() == k.doi.upper():
				dbe[j]['cites'] = k.citation_count
				if v:
					print(f'Found {k.citation_count} citations for {j}.')
				if int(k.citation_count):
					if 'addendum' in dbe[j]:
						dbe[j]['addendum'] = dbe[j]['addendum'] + '. ' + f.format(k.citation_count)
					else:
						dbe[j]['addendum'] = f.format(k.citation_count)
				break

	if s:
		rlen = len(str(len(dbe)))
		for rank, doi in enumerate(sorted(dbe, key = lambda x: -int(dbe[x]['cites']))):
			try:
				authors = dbe[doi]['author'].split(' and ')
				print(f"[{rank+1:>{rlen}}] {dbe[doi]['cites']:>5}   {authors[0]}{' et al.' if len(authors)>1 else ''} ({dbe[doi]['year']}) {dbe[doi]['journal']}")
			except:
				print(f"[{rank+1:>{rlen}}] {dbe[doi]['cites']:>5}   {doi}")

	if o == '_':
		o = bibfile.split('.bib')[0] + '_withcites.bib'

	with open(o, 'w') as bibtex_file:
		bibtexparser.dump(db, bibtex_file)
	if v:
		print(f'Wrote {len(db.entries)} entries to {o}.')
