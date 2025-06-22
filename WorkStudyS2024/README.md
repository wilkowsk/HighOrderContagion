# README
The following constitutes information concerning the HighOrderContagion repository.
## Table of Contents
[Technologies Used](#technologies-used)
[Download Instructions](#download-instructions)
[Usage Instructions](#usage-instructions)
## Technologies Used
This repository was made using Python 3.11. It requires the following libraries, which you may install by clicking the corresponding links:
- [numpy](https://numpy.org/install/)
- [matplotlib](https://matplotlib.org/stable/install/index.html)
  - pyplot
- [networkx](https://networkx.org/documentation/stable/install.html)
- [pandas](https://pandas.pydata.org/docs/getting_started/install.html)
- [sklearn](https://scikit-learn.org/stable/install.html)
## Download Instructions
- Verify that you have installed the packages in the previous section.
- In the GitHub repository, click on the green button reading "<> Code".
- Near the bottom of the menu, click on the option reading "Open with Visual Studio".
- In the Visual Studio window, on the bottom-right corner, click the button reading "Clone".
Visual Studio should now open a project containing this repository's code. Verify that the installation was successful by running the project.
## Usage Instructions
### Pure Model
Follow the directions on the console window. For example, the following input will yield results for the pure model on the full dataset, with $Q = 2$, and without the nonnegativity constraint. Results will be printed to the console and saved to `output-data/yourFilename.txt`.
```
Enter output filename:
    yourFilename
Enter model name (Baseline / Pure / Hypergraph):
    p
Enter dataset size (Partial / Full):
    f
Enter maximum clique dimension:
    2
Enter nonnegativity status (True / False / Yes / No):
    f
```
### Baseline Model
Follow the directions on the console window. For example, the following input will yield results for the baseline model on the full dataset, with $Q = 2$, without the nonnegativity constraint, and for 5 evenly spaced values of $\mu$ from 0 to 1 inclusive: i.e. for $\mu \in \{0, 0.25, 0.5, 0.75, 1\}$. Results will be displayed to the screen and saved to `figures/yourFilename_1.tiff`.
```
Enter output filename:
    yourFilename
Enter model name (Baseline / Pure / Hypergraph):
    b
Enter dataset size (Partial / Full):
    f
Enter maximum clique dimension:
    2
Enter nonnegativity status (True / False / Yes / No):
    f
Enter number of mu values to test:
    5
```
### Hypergraph Model
Follow the directions on the console window. For example, the following input will (eventually) yield results for the hypergraph model on the full dataset, without the nonnegativity constraint, for 5 evenly spaced values of $\delta_I$ from 0 to 1 inclusive: i.e. for $\delta_I \in \{0,0.25,0.5,0.75,1\}$, and for 4 evenly spaced values of $\Theta'_J$ from 0 to 1 exclusive: i.e. for $\Theta'_J \in \{0.2, 0.4, 0.6, 0.8\}$. Results will be displayed to the screen and saved to `figures/yourFilename_1.tiff` and `figures/yourFilename_2.tiff`.
```
Enter output filename:
    testfile
Enter model name (Baseline / Pure / Hypergraph):
    h
Enter dataset size (Partial / Full):
    f
Enter nonnegativity status (True / False / Yes / No):
    f
Enter number of delta values to test:
    5
Enter number of big theta values to test:
    4
```
> Written with [StackEdit](https://stackedit.io/).