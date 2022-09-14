# Input Format:

The input file should be of the following form:

*First line is reserved for the number of agents.

*Starting from the 2nd line, agent's preferences are specified at each line. If there is a tie between agents, those agents are specified between curly brackets. 

Example: 

4 

4 {2,3} 

{4,1} 3 

1 2 4 

2 3


=> There are 4 agents.

agent 1 prefers agent 4 to agent 2, prefers agent 4 to agent 3, and agent 1 is indifferent between agent 2 and agent 3.

agent 2 is indifferent between agent 4 and agent 1, and agent 2 prefers agent 4 to agent 3, and prefers agent 1 to agent 3.

agent 3 prefers agent 1 to agent 2, and prefers agent 2 to agent 4.

agent 4 preferes agent 2 to agent 3.

For Clingo the input file should be a .lp file which contains atoms that represents the instance. We formalize the input of an SRTI instance in ASP by a set of facts using atoms of the forms agent(x) (“x is an agent in A”) and prefer2(x, y,z) (“agent x prefers agent y to agent z). For every agent x, since x prefers being matched with a roommate acceptable y instead of being single, for every y, we also add facts of the form prefer2(x, y, x). 

Referring to the previous example, the corresponding .lp file would contain:

agent(1..4).
prefer2(1,4,2).
prefer2(1,4,3).
prefer2(2,4,3).
prefer2(2,1,3).
prefer2(3,1,2).
prefer2(3,2,4).
prefer2(4,2,3).

prefer2(X,Y,X) :- prefer2(X,Y,\_), X!=Y.
prefer2(X,Y,X) :- prefer2(X,\_,Y), X!=Y.

*******************************************************
## *Choco*

For SRI-CP, see: http://www.dcs.gla.ac.uk/~pat/roommates/distribution/.

Under '/Choco' we provide our implementations of the CP model to solve SRTI.

*Prerequisites*: Choco version 4.0.8 must be installed.

To run our implementation, first add the path to choco to your classpath. Then, compile the java classes from the .java files in the directory by running ```javac *.java```

Then, run ```java SRTI input.txt```

*******************************************************
## *OR-Tools*

Under '/OR-Tools' we provide our implementation of our CP model to solve SRTI.

*Prerequisites*: OR-Tools CP SAT solver must be installed.

To run our implementation, run ```python SRTI-CP-OR.py input.txt```

*******************************************************
## *Clingo*

Under '/Clingo' directory we provide logic programs that solve SRI (2D-SRI.lp), SRTI (2D-weakly-SRTI.lp) and its some variants (egal.lp, rankmax.lp, almost.lp).

*Prerequisites*: clingo must be installed.

To run our implementation, run ```clingo 2D-SRI.lp input.lp```.

To solve optimization variants, run ``` clingo egal.lp input.lp```; ```clingo rankmax.lp input lp.```

To find almost stable solution, run ```clingo almost.lp input.lp```.



