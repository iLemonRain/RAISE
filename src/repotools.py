from git import Repo
from git.exc import NoSuchPathError
from git.exc import InvalidGitRepositoryError
import time
import shutil


# 根据文件夹的路径获取仓库
def SetRepo(repo_dir, repo_url):
    try:
        repo = Repo(repo_dir)
    except NoSuchPathError:
        print("没有这个目录,正在新建目录并且初始化新仓库...")
        repo = Repo.init(path=repo_dir)
        repo.create_remote(name='origin', url=repo_url)
    except InvalidGitRepositoryError:
        print("这个目录里面没有git信息,正在删除目录并克隆一个...")
        shutil.rmtree(repo_dir)  # 递归删除文件夹
        repo = Repo.init(path=repo_dir)
        repo.create_remote(name='origin', url=repo_url)
    finally:
        return repo


# 推送仓库中的所有文件
def PushFileList(repo, encrypted_file_dir_list):
    try:
        repo.index.add(encrypted_file_dir_list)
        commit_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        repo.index.commit(commit_str)
        repo.remote().push("master")
    except Exception as e:
        print(e)


# 拉去仓库中的所有文件
def PullAllFiles(repo):
    try:
        repo.remote().pull("master")
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
    pass
