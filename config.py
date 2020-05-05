import datetime

analysis_start_date = datetime.datetime(2013, 10, 29)
analysis_end_date = datetime.datetime(2020, 4, 28)
project_name = "sonarlint-intellij"
input_directory = "input/" + project_name
output_directory = "output/" + project_name
clone_directory = "projects/" + project_name
git_repo = "SonarSource/sonarlint-intellij"
git_url = "https://github.com/"+git_repo+".git"
branch = 'master'
