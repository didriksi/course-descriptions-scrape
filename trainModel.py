import fasttext
import re
import pandas as pd

def make_dataset(course_df):
    """Makes a fasttext-friendly list of course descriptions from a dataframe.

    :param course_df: pd.DataFrame with columns coursecode, coursename, course_description.

    :return: List of strings.
    """

    dataset = []
    for (_, course) in course_df.iterrows():
        if course["course_description"] and isinstance(course["course_description"], str):
            course_desc = re.sub('\n', ' ', course["course_description"])
            dataset.append(
                "__label__{institute} {course_desc}".format(**course, course_desc=course_desc))
    return dataset

if __name__ == "__main__":
    course_df = pd.read_csv("courses.csv")
    dataset = make_dataset(course_df)
    print(course_df)
    with open("dataset.txt", "w") as file:
        file.write("\n".join(dataset))
    model = fasttext.train_supervised("dataset.txt", epoch=30, lr=1.0, wordNgrams=3, verbose=2)