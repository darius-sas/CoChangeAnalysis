from git import Repo
import pandas as pd

# Constants
from CommitsPerCommitDay import commits_per_commitday
from Commits_over_lifetime import commits_over_lifetime
from FilesPerCommit import files_per_commit_information
from MBA import perform_mba
from TimeBetweenCommits import time_between_commits
from ThresholdAnalysis import threshold_distribution
from Utility import get_class_from_package
from config import output_directory
from dynamic_Warp import perform_dtw
from helper_scripts.output_helper import filter_duplicate_file_pairs, generate_all_pairs

git_url = "https://github.com/SonarSource/sonarlint-intellij.git"
clone_directory = "projects/sonarlint-intellij/"
branch = 'master'

warps, changedFiles = perform_dtw()

# Map changed files to class.java
changedFiles = list(map(get_class_from_package, changedFiles))

warpdf = filter_duplicate_file_pairs(warps)
# Map warps to class.java
warpdf['file1'] = warpdf['file1'].apply(get_class_from_package)
warpdf['file2'] = warpdf['file2'].apply(get_class_from_package)

all_pairs = generate_all_pairs(changedFiles)
warpdf.to_csv(output_directory + "/dtw.csv")
all_pairs.to_csv(output_directory + "/file_pairs_dtw.csv")

rules, changedFiles = perform_mba()
# Map changed files to class.java
changedFiles = list(map(get_class_from_package, changedFiles))

rules = filter_duplicate_file_pairs(rules)
# Map warps to class.java
rules['file1'] = rules['file1'].apply(get_class_from_package)
rules['file2'] = rules['file2'].apply(get_class_from_package)

all_pairs_mba = generate_all_pairs(changedFiles)
# both ante en consequents are sets of length 1

rules.to_csv(output_directory + "/mba.csv")
all_pairs_mba.to_csv(output_directory + "/file_pairs_mba.csv")

# Clone the repo we want to analyse.
# Repo.clone_from(git_url, clone_directory)
# repo = Repo(clone_directory)

# Analyse the amount of files per commit for this repo.
# files_per_commit_information(repo, branch)

# Analyse the time between commits for this repo.
# time_between_commits(repo, branch)

# Get the number of commits per day the repo exists
# commits_over_lifetime(repo, branch)

# Histogram of thresholds (make sure to update cochanges.csv!)
# threshold_distribution()
# Get the number of commits per day on which there were commits
# commits_per_commitday(repo, branch)
