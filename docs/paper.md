---
title: General binary file parser.
tags:
  - binary
  - parser
  - yaml
  - json 
  - read write
authors:
  - name: Jeroen F.J. Laros
    orchid: 0000-0002-8715-7371
    affiliation: 1
affiliations:
  - name: Leiden University Medical Center,
    index: 1
date: 5 May 2018
---

# Summary
To enable interoperability for (proprietary) binary file formats while
maintaining compatibility with the original software, a lot of effort needs to
be put in reverse engineering of the file format and the subsequent programming
of a dedicated parser and writer. Here we introduce a library that aims to keep
this effort to a minimum by providing a framework that enables a programmer to
record the knowledge gained in the reverse engineering process in a structured
way for it to be used directly in a parser, a writer and as documentation.

General binary file parsing and writing is implemented by interpretation of
human readable documentation of the file structure and data types. Basic types
like variable length strings, maps and bit fields (flags), as well as
elementary data types provided by the [struct][struct] library are supported
and other data types are easily added. Apart from basic types, nested
structures and various kinds of iterators are supported to accommodate for
complicated file formats. Numerous character encodings are supported via the
[iconv][iconv] library.

Since all operations needed for parsing a binary file can be reversed, fully
functional binary editing is possible using this library. A binary file can be
converted to a serialised dictionary representation, edited and be converted
back to its binary form.

We have made two implementations of this library: one in Python and one in
JavaScript. We chose YAML as our preferred serialised dictionary format, but
other serialisation formats (JSON for example) can be used too.
