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
    # print(GetDiffFileDirList(repo))
    file_list = ['F2bSfGXMzzGnrpfq7xJp6NGLcH5tf7kZJarw6bPXxYQm5PnnVofx9PqHPpREJW1dtZ4yFZcAgA6OLQp$wpFMUQ==', 'fVsfdZ1z6A3jIsoyOCw6qVmowkUrl60viyxj1P6oHwK018YiAGw$sR87GTdNbNTCvut5PBT2491TU94L$KmEPA==', 'TXfaE0SHZq6NvA62TRy+QoQQoYBbhh7P7vew+oLehtDyyOst8tBciXWj$pXO64yj26fv6cnVnercwK2bEXJo7Q==', 'fKWXBVDHjCHvF6LQi73r3Rx$bgS3FlwQGqTLpqLqCg7kcKmeFE9UfgiEhR4zerqcehKc3U0G+gPG0ACN$u4DMw==', 'N$IW$hBoFHTfx5tm4MoDK11lsPEUljqbpePOJM3K8j7QR5XQ+iEs5ymx9vhnq6OcsdVfJmIsqRn5rdma$GZ9DA==', 'ppcrG6ihE+qSMnY4lIKMvJklryYiHPONrRIj56hMc2YiqQDe1vFjmw7RDKpZWlF+fIKSzxj0k+9mAZwEFOjQ7g==', 'IR4kYGQy89oyy0Ld5DWbNyE4mDebNh9wYV8amjuVNmvAKviwkddrO1vw+0sAusc9faf6IY$JYrlsc5wrvBP96w==', 'a6JTVDX2ZfZ92O02zwf8UzHjakwv3MboUsUw69JF1E9UAhG+DcGni9rbOCqGpG2D550ojdEBtOkPFje4R1L1yg==']
    PushFileList(repo, file_list)
