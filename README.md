# ltlf-assum

## Installation


Needs [MONA](http://www.brics.dk/mona/) to convert LTLf formulae to DFA. Check the website for installation instructions or try to install with apt.
```
sudo apt install mona
```


Needs [PRISM-games](https://www.prismmodelchecker.org/games/) for all computations on stochastic games. Check the website for installation instructions. 
Uses Py4J to create a java gateway. Check the [PRISM-api github](https://github.com/prismmodelchecker/prism-api) for further info on how to expand the java classpath to include PRISM .class files and .jars.

python dependencies: networkx, ltlf2dfa, pygraphviz, py4j. 
```
sudo apt install graphviz
pip3 install networkx ltlf2dfa pygraphviz py4j
```

## Running the Code

In order to run the code, first start the java PRISM handler. Make sure your classpath includes py4j and the PRISM-games .class files and .jars either by extending the CLASSPATH or with the -cp option.

```
cd prismhandler
javac PrismEntryPoint.java
java PrismEntryPoint.java
```

Once the gateway is running, run the main code or the unittests:

```
python3 main.py
```

## Commit Conventions

Every commit is associated with one of the following types:

* (feature) - added functionality to the code
* (bugfix) - fixed bugs in the code
* (test) - added or changed unittests
* (refactor) - refactored the structure of the code without changing the functionality
* (cleanup) - minor code cleanups like removing unused imports or changing some comment lines/whitespaces
* (other) - a commit that doesn't fit any category above; should rarely be used
