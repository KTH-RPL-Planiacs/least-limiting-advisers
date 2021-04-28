# ltlf-assum

## Installation

### [MONA](http://www.brics.dk/mona/)
We use [MONA](http://www.brics.dk/mona/) to convert LTLf formulae to DFA. Check the website for installation instructions or try to install with apt.
```
sudo apt install mona
```

### [PRISM-games](https://www.prismmodelchecker.org/games/)
[PRISM-games](https://www.prismmodelchecker.org/games/) is used for all computations on stochastic games. We recommend building from source, please check their [website](https://www.prismmodelchecker.org/games/installation.php) for build instructions. 

### [Py4J](https://www.py4j.org/)
We use Py4J to create a java gateway in order to access the PRISM-games java API. You need to expand the java classpath to include PRISM .class files and .jars. Check the [PRISM-api github](https://github.com/prismmodelchecker/prism-api) for further examples and information.
```
pip3 install py4j
```

### Other Dependencies
pygraphviz requires graphviz and is used for dot-graph output of automata. pygame is used for visualization purposes.
```
sudo apt install graphviz
pip3 install networkx ltlf2dfa pygraphviz pygame
```

## Running the Code

In order to run the code, first start the java PRISM handler. Make sure your classpath includes py4j and the PRISM-games .class files and .jars either by extending the CLASSPATH or using the -cp option.

```
cd prismhandler
javac PrismEntryPoint.java
java PrismEntryPoint.java
```

Once the gateway is running, run the main code or the unittests:

```
python3 main.py
```
