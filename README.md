# Favorlang Dictionary

This is the repo that hosts the transcribed [Favorlang dictionary](https://books.google.at/books?id=WpUEAAAAQAAJ&hl=en). All the hard work was done by the students participating the course [Introduction to Phonology](https://nol2.aca.ntu.edu.tw/nol/coursesearch/print_table.php?course_id=142%20M0110&class=&dpt_code=1420&ser_no=10017&semester=108-1) offered by Prof. Chiang at [Graduate Institute of Linguistics](https://linguistics.ntu.edu.tw/), National Taiwan University.

View the transcribed dictionary files [here](https://favorlanglang.github.io/dict/). Visit [this site](https://favorlanglang.github.io) to read more about this project and search Favorlang dictionary online.


## Compile the transcribed dictionary


```python
python3 main.py
```

This generates `docs/dict.html`, `docs/favorlang_dict_transcribed.pdf`, `docs/dict.json`, `docs/dict.csv`.

### Prerequisites

- python3
    - `pandas`, `numpy`, `bs4`
- Chrome or Chromium