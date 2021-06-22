# report_miner
Report Miner - A tool for report mining in datasets

Many time it can be difficult to create datasets based on reports. As most radiologists don't use pre-defined templates, it can be a hassle to deal with thousand reports.

The idea of Report Miner is to define inclusion and exclusion words/phrases foraminal searching for specific diseases.

The same code is available it two formats: a Jupyter Notebook and a GUI. The GUI needs to be run locally, while the Jupyter runs in a cloud enviroment.

The steps inside the code are:

1) open a CSV containing report datasets
2) create a stopwords list, removing from this list some stopwords you would need in your searches.
3) drop the columsn you will not need
4) defining the name of the columns containing the report
5) clear this column removing undesired character such as double paragraphs, radiologist name, etc.
6) remove stopwords from the report

Then, you will define inclusion and exclusion words/phrases. The following steps will occur:

1) the report is broken in paragraphs splitted by paragraphs or . (dots)
2) for each paragraph splitted, the code will look fora exclusion words. If it find, the paragraph is discharged.
3) for the remaining paragraphs, the code will for for inclusion words. If it find, this report is tagged as "Positive"
4) all inclusion paragraphs are sorted and listed together, so the user can check is results are good. If they're not, one can change inclusion and exclusion words and run the code again.

And finally, you can export a new dataset containing the original reports and a new columns with "positive" phrases.
