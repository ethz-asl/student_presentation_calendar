import github3
import csv
import getpass

code = ''
try:
    # Python 2
    prompt = raw_input
except NameError:
    # Python 3
    prompt = input

def my_two_factor_function():
    global code
    if code == '':
      code = prompt('Enter 2FA code: ')
    return code
  
usr = prompt('Enter Username (has to be admin): ')
pw = getpass.getpass()
gh = github3.login(usr, pw,
                  two_factor_callback=my_two_factor_function)
org = gh.organization('ethz-asl')

repos = org.iter_repos(type="private")

with open('repos.csv', 'wb') as csvfile:
  writer = csv.writer(csvfile, delimiter=',')
  writer.writerow(["Name", "Created at", "Pushed at", "Updated at", "#1 contributor", "#2 contributor", "#3 contributor", "#4 contributor"])
  for repo in repos:
    try:
      print repo.name
      cont_list = repo.iter_contributors(number=4)
      conts = []
      for cont in cont_list:
        conts.append(cont.login)
      if len(conts) != 4:
        for i in range(0, 4 - len(conts)):
          conts.append('')
      writer.writerow([repo.name, repo.created_at, repo.pushed_at, repo.updated_at, conts[0], conts[1], conts[2], conts[3]])
    except github3.models.GitHubError:
      code = prompt('Enter 2FA code: ')
      print repo.name
      cont_list = repo.iter_contributors(number=4)
      conts = []
      for cont in cont_list:
        conts.append(cont.login)
      if len(conts) != 4:
        for i in range(0, 4 - len(conts)):
          conts.append('')
      writer.writerow([repo.name, repo.created_at, repo.pushed_at, repo.updated_at, conts[0], conts[1], conts[2], conts[3]])
 
      
