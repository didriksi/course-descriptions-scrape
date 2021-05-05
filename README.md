# Course descriptions scrape

Finds english course descriptions of courses at University of Oslo. To be used as a dataset.

To find courses, run `python scrapeForCourses.py`, and to scrape for descriptions of these courses, run `python scrapeEachCourse.py`. The course data is stored as a Pickled Pandas DataFrame, in `courses.pkl`. To make a list of all the course descriptions, use something like  
```
from scrapeEachCourse import make_dataset
course_df = pd.read_pickle('courses.pkl')
dataset = make_dataset(course_df)
```

There are some options as to what parts of the course descriptions to include in the `id_headers`-kwarg in `scrapeEachCourse.get_course_description`.

Based on [didriksi/course-search](https://github.com/didriksi/course-search)
