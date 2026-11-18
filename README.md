# Student performance Sankey diagram

An interactive Python chart of weekly study time, school absences and final mathematics grades. Hover over a link to see how many records fall into that pair of categories. The two sets of links are counted separately, so a path across all three columns does not identify an individual student's trajectory.

## Run the example

From the project directory:

```sh
python -m pip install -r requirements.txt
python student_sankey.py
```

The bundled `student-mat.csv` is a small synthetic example. The script writes `student_sankey.html` and opens it in your browser. The HTML includes Plotly and can be viewed offline.

## Use the original data

Download the [UCI Student Performance dataset (P. Cortez, 2008)](https://doi.org/10.24432/C5TG7T), extract the mathematics file `student-mat.csv`, and pass its path to the script:

```sh
python student_sankey.py --data path/to/student-mat.csv --no-browser
```

The analysis uses three fields: `studytime` (weekly study-time category, 1–4), `absences` (number of school absences), and `G3` (final grade, 0–20). A zero grade is valid. Records with identical values in these fields are retained because they may represent different students. The absence and grade bands are choices made for this visualization.

## Design and code

The project author chose the validation rules, the category and node structure, and what the hover text should communicate. AI assisted with pandas and Plotly syntax and with completing the code that maps adjacent category counts to chart links.
