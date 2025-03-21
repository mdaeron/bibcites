'''
CLI to insert number of citations into BibTeX entries, using OpenCitations
'''

__author__	= 'Mathieu Daëron'
__contact__   = 'mathieu@daeron.fr'
__copyright__ = 'Copyright (c) 2025 Mathieu Daëron'
__license__   = 'MIT License - https://opensource.org/licenses/MIT'
__date__	  = '2025-03-21'
__version__   = '2.0.1'

import bibtexparser
from bibtexparser.bparser import BibTexParser
from requests import get
import click
from tqdm import tqdm

@click.command()
@click.argument('bibfile')
@click.option('-o', default='_', help='output BibTex file')
@click.option('-f',
	default = '[citations: {:s}]',
	help = "format of text to save to 'addendum' field",
	)
@click.option('-s', default=False, is_flag=True, help='print list sorted by cites')
@click.option('-v', default=False, is_flag=True, help='enable verbose output')
@click.option('-t', default=[], multiple=True, help='only process entries of this type (may be used several times to process several types)')
@click.option('-p', default='', multiple=False, help='prepend custom string to each bibtex key')
# @click.option('-k', default='', multiple=False, help='API token for OpenCitations')
def cli(bibfile, o, s, f, v, t, p):
	'''
	Reads a BibTeX file (BIBFILE), finds entries with a DOI, looks up the corresponding
	number of citations using OpenCitations (https://opencitations.net), saves this
	number to the 'addendum' field of each entry, and writes results to a new BibTex file.
	
	Optionally, using option -s, print out a list of entries with DOI sorted
	by number of citations.
	Optionally, using option -k, prepend each entry key with a custom string.
	'''

# 	Interrogating OpenCitations requires an API token which may be specified using option -k.
# 	Without this option, bibcites will use the contents of `./.opencitations-token`
	
	t = [_.lower() for _ in t]
	
	## read BibTeX file
	with open(bibfile) as bibtex_file:
		parser = BibTexParser(common_strings = True)
		db = bibtexparser.load(bibtex_file, parser=parser)
	if v:
		print(f'Read {len(db.entries)} entries from {bibfile}.')

	if p:
		for r in db.entries:
			r['ID'] = p + r['ID']

	## dict of entries with a DOI	
	dbe = {e['doi']: e for e in db.entries if 'doi' in e and (len(t) == 0 or e['ENTRYTYPE'].lower() in t)}

# 	if k == '':
# 		with open('./.opencitations-token') as fid:
# 			k = strip(fid.read())

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
	
	dois = [doi for doi in dbe]

# 	print('Querying OpenCitations...')
	metadata = []
	for _, doi in tqdm(
		list(enumerate(dois)),
		desc = 'Querying OpenCitations',
		bar_format = '{desc}: |{bar}{r_bar}',
		):
		r = get(		
			f'https://opencitations.net/index/api/v1/citation-count/{doi}?format=csv',
# 			dict(authorization = api_token),
			)
		metadata.append((doi, r.text))
# 		print([r.text])

	if v:
		print(f'Read {len(metadata)} records from OpenCitations.')

	for doi, c in metadata:

		try:
			c = c.split('\n')[1].strip()
		except:
			if v:
				print(f'Could not read citation count for {doi}')
			continue

		for j in dbe:
			if j.upper() == doi.upper():
				dbe[j]['cites'] = str(c) if len(c) else '0'
				if v:
					print(f'Found {c} citations for {j}.')
				if int(dbe[j]['cites']):
					if 'addendum' in dbe[j]:
						dbe[j]['addendum'] = dbe[j]['addendum'] + '. ' + f.format(dbe[j]['cites'])
					else:
						dbe[j]['addendum'] = f.format(dbe[j]['cites'])
				break

# 		for j in dbe:
# 			if 'cites' not in dbe[j]:
# 				print(dbe[j])

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
