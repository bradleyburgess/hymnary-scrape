# hymnary-scrape

This is a very simple utility written in Python to scrape hymn texts from [Hymnary.org](https://hymnar.org).

## Example

```python
python hymnary-scrape.py UMH 147     # Will download only 147 from United Methodist Hymnal

python hymnar-scrape.py UMH 216 230  # Will download range from 216–230
```

All texts are saved in a folder named after the hymnal in the current directory, each hymn in its own text file.

Error checking is *very* simple, but if the arguments are not correct, there is a help message.
