"""Functions for scraping for courses."""

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

def make_soup(url):
    """Makes bs4.BeautifulSoup instance of content of url.

    :param url: url to make bs4.BeautifulSoup instance from.
    
    :return: bs4.BeautifulSoup instance of content of url.
    """
    coursepage = requests.get(url)
    coursecontent = coursepage.content
    return BeautifulSoup(coursecontent, 'html.parser')

def has_results(coursepage_url, tag_id="vrtx-listing-filter-no-results"):
    """Returns True if site has tag with id tag_id.
    
    Used in this case to find out if a search page has results, because
    UiOs search sites have a tag with id 'vrtx-listing-filter-no-results'
    if there are no results.

    :param coursepage_url: String representation of url to check if exists.
    :param tag_id: Id of tag that is on site when there are no results.

    :return: True if there are results, False if not.
    """
    soup = make_soup(coursepage_url)
    return not soup.find(id=tag_id)

def get_course_url_list(base_url="https://www.uio.no/studier/emner/alle/?page="):
    """Constructs a list with all pages that have results.
    
    :param base_url: String representation of url to append ints to to make search page.

    :return: List of string urls that have valid pages with results.
    """
    url_list = []
    i = 0
    url = base_url + str(i)
    while has_results(url):
        url_list.append(url)
        i += 1
        url = base_url + str(i)
        print(f"\rChecking if there are courses on page: {i}", end="", flush=True)
    
    print(f"\rCompleted. Found {len(url_list)} pages of courses.\033[K", flush=True)

    return url_list

def get_course_url_info(course_url):
    """Finds faculty, institute and coursecode given some course url.

    :param course_url: String representation of course url. Expecting it to be in the 
                      format '/studier/emner/<faculty>/<institute>/<coursecode>/index.html'
    
    :return: 3-tuple with faculty, institute and coursecode.

    :raise ValueError: When course_url is invalid, and doesn't follow format.
    """
    url_format = r"\/studier\/emner\/(\w*)\/(\w*)\/(.*)\/index.{0,10}.html"
    for match in re.finditer(url_format, course_url):
        return match.group(1), match.group(2), match.group(3)
    
    raise ValueError(f"Course url `{course_url}` is invalid, and doesn't follow the format"
                     "'/studier/emner/<faculty>/<institute>/<coursecode>/index.html'.")

def find_coursecodes(coursepage_url):
    """Scrapes search page for courses on it.

    :param coursepage_url: Url with search results of courses.
                           Like the ones generated by get_course_url_list.
    
    :return: 4-tuple of lists with faculties, institutes, course codes and course names.
             The lists have the same length, meaning they eg repeat faculties for each course.
    """
    coursepage_soup = make_soup(coursepage_url)

    faculties, institutes, coursecodes, coursenames, urls = [], [], [], [], []
    for link in coursepage_soup.tbody.find_all('a'):
        course_url = link.get('href')
        
        faculty, institute, coursecode = get_course_url_info(course_url)

        # The regex search is based on the pattern course codes at UiO had in spring 2020, but it
        # is a bit random, and can probably change over time. If a new code is added that doesn't
        # follow this pattern, this function will break.
        coursename_search = re.search(r"^[A-ZÆØÅ\-]+\d*[A-ZÆØÅ\-]{0,6}\d{0,2} *.? *(.*)", link.string)
        coursename = coursename_search.group(1)
        
        faculties.append(faculty)
        institutes.append(institute)
        coursecodes.append(coursecode)
        coursenames.append(coursename)
        urls.append(course_url)

    return faculties, institutes, coursecodes, coursenames, urls

if __name__ == '__main__':
    faculties, institutes, coursecodes, coursenames, urls = [], [], [], [], []

    for coursepage_url in get_course_url_list(base_url="https://www.uio.no/english/studies/courses/all/?page="):
        print(f"\rGoing through {coursepage_url}. Have so far found {len(coursecodes)} courses.", flush=True, end='')
        new_faculties, new_institutes, new_coursecodes, new_coursenames, new_urls = find_coursecodes(coursepage_url)
        
        faculties.extend(new_faculties)
        institutes.extend(new_institutes)
        coursecodes.extend(new_coursecodes)
        coursenames.extend(new_coursenames)
        urls.extend(new_urls)

    courseData = pd.DataFrame()

    courseData['coursecode'] = coursecodes
    courseData['coursename'] = coursenames
    courseData['faculty'] = faculties
    courseData['institute'] = institutes
    courseData['url'] = urls
    
    courseData.to_pickle('courses.pkl')

    print(f"\rFound {len(coursecodes)} courses on those pages, and saved them in 'courses.pkl'\033[K", flush=True)
