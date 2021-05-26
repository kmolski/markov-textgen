# markov-textgen

Text generation script using [Markov chains](https://en.wikipedia.org/wiki/Markov_chain) of any order.
Markov models can be created from ordinary strings, files, text lines or collections of words.
Model-generating functions provide options for processing input data - letter case normalisation and special character removal.


Usage:
------

This script requires Python 3.9 (or newer).
To use the script interactively, start `python3` and import the module:

```sh
$ python3
Python 3.9.5 (default, May 12 2021, 17:14:51) 
[GCC 10.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import markov_textgen
```

Examples:
--------

```python
>>> model = markov_textgen.model_from_file(
...     "dr_jekyll_and_mr_hyde.txt",
...     normalise_case=False,
...     remove_non_word_chars=False,
... )
>>> model.generate_string(30, sentences=True)
'Next they turned the end is sure and must flee before daylight from a house that was the messenger like?”'
>>> model.generate_string(30, sentences=True)
'John Utterson. He looked up when a drunkard reasons with himself upon his spirits. The fifth night he had means of obtaining a copy of a life of such a client.'
>>> model.generate_string(30, sentences=False)
'you. You had a shock,” he said, looking Mr. Utterson at last he struck. The next thing was not my master, why had he a mask upon his mind a singularly'
```


License:
--------

[MIT License](https://opensource.org/licenses/MIT)
