"""Functions for scraping courses."""

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

from scrapeForCourses import make_soup

def get_course_description(content_tag,
                           id_headers=("course-content", "learning-outcomes"),
                           language_detector=lambda x: True):
    """Makes a string with the description of the course.

    :param content_tag: bs4.BeautifulSoup instance of content tag in course page.
    :param id_headers: IDs of div tags that we want to scrape content from.
    :param language_detector: Function taking in a string, and returning True if it is of the correct language.

    :return: List of strings.
    """
    
    if content_tag is None:
        # Occasional error that isn't impossible to handle,
        # but that occurs so rarely and with courses UiO has
        # themselves made an error, so this should do
        return {}
    
    sections = {}
    for child in content_tag.descendants:
        if child.name == "div" and "id" in child.attrs and child["id"] in id_headers:
            temp = [grandchild.text for grandchild in child.descendants if grandchild.name == "p"]
            title = child["id"].replace("-", " ").capitalize()
            sections[title] = "\n".join([string for string in temp if language_detector(string)])
    total_text = " ".join([title + "\n\n" + content for title, content in sections.items()])

    return total_text

def make_dataset(course_df):
    """Makes a ML-friendly list of course descriptions from a dataframe.

    :param course_df: pd.DataFrame with columns coursecode, coursename, course_description.

    :return: List of strings.
    """
    return ["{coursecode} {coursename}\n\n{course_description}".format(**course)
            for (_, course) in course_df.iterrows() if course["course_description"]]

if __name__ == '__main__':
    courseData = pd.read_pickle('courses.pkl')
    num_courses = len(courseData.index)

    course_descriptions = []
    for i, (_, course) in enumerate(courseData.iterrows()):
        print(f"\rScraping {course['coursecode']}, which is course {i}/{num_courses}                           ",
              flush=True,
              end='')
        course_soup = make_soup('https://www.uio.no/' + course['url'])
        content = course_soup.find(id='vrtx-course-content')
        course_descriptions.append(get_course_description(content))

    courseData['course_description'] = course_descriptions

    courseData.to_pickle('courses.pkl')

    print("\rScraped all courses, and updated dataframe in `courses.pkl`\033[K")
    print("Dataset can be generated with make_dataset(courseData)")
