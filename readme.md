# bibcites

Command-line utility which reads a BibTeX file, finds entries with a DOI, looks up the corresponding number of citations using [OpenCitations], saves this number to the `addendum` field of each entry, and writes results to a new BibTex file.

## Installation

`python -m pip install bibcites ` should do the trick

## Usage

````
Usage: bibcites [OPTIONS] BIBFILE

  Reads a BibTeX file (BIBFILE), finds entries with a DOI, looks up the
  corresponding number of citations using OpenCitations
  (https://opencitations.net), saves this number to the 'addendum' field of
  each entry, and writes results to a new BibTex file.

  Optionally, using option -s, print out a list of entries with DOI sorted by
  number of citations.

Options:
  -o TEXT     output BibTex file
  -f TEXT     format of text to save to 'addendum' field
  -s          print list sorted by cites
  -v          enable verbose output
  -t TEXT     only process entries of this type (may be used several times to
              process several types)
  -n INTEGER  size limit for OpenCitations queries
  --help      Show this message and exit.
````

`bibcites myfile.bib` will read the contents of `myfile.bib`, look up all entries with a `DOI` field in [OpenCitations], append “[X citations]” to the `addendum` field of each entry, and save the result to `myfile_withcites.bib`

* To get verbose output, use `-v` option.
* To set a custom file name for the output BibTeX file, use the `-o <customfilename>` option.
* To set a custom format to the `addendum` field, use the `-f` option, e.g., `-f 'Cited {:s} times'`. Use the `{:s}` specifier because the citation count is a string.
* To print out a list of processed entries, sorted by decreasing number of citations, use the `-s` option.
* To process only entries of certain types, use the `-t` option one or more times, e.g., `-t article -t book`.
* To limit the size of OpenCitations queries, use `-n` option (default is `-n 50`).


## Contact

All questions and suggestions are welcome and should be directed at [Mathieu Daëron](mailto:daeron@lsce.ipsl.fr?subject=[D47crunch]).

[OpenCitations]: (https://opencitations.net)