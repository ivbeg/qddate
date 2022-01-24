.. :changelog:

History
=======


1.0.1 (2022-01-15)
------------------
* Added "noyear" flag to match function. If used than all "noyear" patterns will be ignored. This is needed to avoid a lot of false positives
* Added "patterns" and "base_only" parameters for DataParser __init__ function. Now patterns used to pass list of date patterns listed in qddate.patterns and "base_only" used to do not generate any additional patterns from base patterns provided
* Disabled pattern "dt:date:date_7" for dates like 09.2019 without day in date string. It generated too many false positives and it's extremely rare.

0.1.1 (2018-07-20)
------------------
* Code cleanup, date patterns moved to "qddate.patterns"

0.1.0 (2018-01-14)
------------------
* First public release on PyPI and github
