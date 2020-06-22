from git import Repo
from git.exc import NoSuchPathError
from git.exc import InvalidGitRepositoryError
import time
import shutil

# 根据文件夹的路径获取仓库
def SetRepo(dir, href):
    try:
        return Repo(dir)
    except NoSuchPathError:
        print("没有这个目录,正在克隆一个...")
        return Repo.clone_from(href, dir)
    except InvalidGitRepositoryError:
        print("这个目录里面没有git信息,正在删除目录并克隆一个...")
        shutil.rmtree(dir) # 递归删除文件夹
        return Repo.clone_from(href, dir)


# 推送仓库中的所有文件
def PushFileList(repo, encrypted_file_dir_list):
    try:
        repo.index.add(encrypted_file_dir_list)
        commit_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        repo.index.commit(commit_str)
        repo.remote().push()
    except Exception as e:
        print(e)


# 拉去仓库中的所有文件
def PullAllFiles(repo):
    try:
        repo.remote().pull()
    except Exception as e:
        print(e)


# 得到更改了的文件列表
def GetDiffFileDirList(repo):
    commits = list(repo.iter_commits("origin/master"))
    repo_dir = repo.working_dir
    diff_file_dir_list = repo.git.diff(commits[1], commits[0], name_only=True).split("\n")
    for i in range(len(diff_file_dir_list)):
        diff_file_dir_list[i] = repo_dir + "/" + diff_file_dir_list[i]
    return diff_file_dir_list


if __name__ == '__main__':
    repo = SetRepo('./repo', "https://github.com/iLemonRain/testgithubcovertcommunication.git")
    print(GetDiffFileDirList(repo))
    # file_list = ["beSPAewd0ESfbwJo5$eK10Y1pUglLbk7+piZQCl0zj4v$x2PyO$dkVM3l0m3vs70yDOxQC$jZhyQF1$VynviyQ==", "c4QqA1qzeqnnjtMQrTjBqqRcNIdLXxZ4wpnOuYUxgQ9Mw+n6aUFWQSTZYXSkhsv7N0PNKLuprQ9k9jwAYS6yAQ=="]
    # PushFileList(repo, file_list)
