# ltlf-assum

## Installation


Needs [MONA](http://www.brics.dk/mona/) to convert LTLf formulae to DFA. Check the website for installation instructions or try to install with apt (see below).

Needs [PRISM-games](https://www.prismmodelchecker.org/games/) for all computations on stochastic games. Check the website for installation instructions. 
Uses Py4J to create a java gateway. Check the [PRISM-api github](https://github.com/prismmodelchecker/prism-api) for further info on how to expand the java classpath to include PRISM .class files and .jars.

python dependencies: networkx, ltlf2dfa, pygraphviz, py4j. 

If you have apt, try this:

```
sudo apt install mona, graphviz
pip3 install networkx ltlf2dfa pygraphviz py4j
```

## Running the Code

In order to run the code, first start the java PRISM handler. Make sure your classpath includes py4j and the PRISM-games .class files and .jars either by extending the CLASSPATH or with the -cp option.

```
javac PrismEntryPoint.java
java PrismEntryPoint.java
```

Once the gateway is running, run the main code

```
python3 main.py
```
