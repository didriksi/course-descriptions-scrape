import fasttext
import re
import pandas as pd

def make_dataset(course_df, split=0.7):
    """Makes a fasttext-friendly list of course descriptions from a dataframe.

    :param course_df: pd.DataFrame with columns coursecode, coursename, course_description.
    :param split: Float 0-1 determining size of training set.

    :return: Two-tuple of list of strings, training set and then testing set.
    """

    train = []; test = []
    valid_course_df = course_df.dropna()
    valid_course_df = valid_course_df[valid_course_df["course_description"] != ""]
    institute_splits = {institute_name: int(len(group)*split)
                        for institute_name, group in valid_course_df.groupby("institute")}
    for (_, course) in valid_course_df.iterrows():
        if institute_splits[course["institute"]]:
            course_desc = re.sub('\n', ' ', course["course_description"])
            train.append(
                "__label__{institute} {course_desc}".format(**course, course_desc=course_desc)
            )
            institute_splits[course["institute"]] -= 1
        else:
            course_desc = re.sub('\n', ' ', course["course_description"])
            test.append(
                "__label__{institute} {course_desc}".format(**course, course_desc=course_desc)
            )
    return train, test

if __name__ == "__main__":
    course_df = pd.read_csv("courses.csv")
    train, test = make_dataset(course_df)
    for split_var, split_name in [(test, "test"), (train, "train")]:
        with open(f"{split_name}.txt", "w") as file:
            file.write("\n".join(split_var))
    model = fasttext.train_supervised("train.txt", epoch=30, lr=1.0, wordNgrams=3, verbose=2)
    print(model.test("test.txt"))
