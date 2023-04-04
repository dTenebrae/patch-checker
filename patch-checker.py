import sys
import subprocess
from pathlib import Path

# CONST
P_FAILED = -1
P_APPLIED = -2
P_NOFILE = -3
P_SUCCESS = 0


def check_src_tree(src_path) -> bool:
    ps = subprocess.Popen("git status",
                          shell=True,
                          cwd=src_path,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    git_status = ps.communicate()[0].decode('utf-8')
    if 'fatal: not a git repository' in git_status:
        print("Not a git repository")
        return False
    elif 'Changes not staged for commit' in git_status:
        print("Some untracked changes in git tree")
        return False
    elif 'Changes to be committed' in git_status:
        print("Not commited files exists in tree")
        return False
    elif 'working tree clean' in git_status:
        return True
    else:
        print("Unknown error")
        return False


def reset_git_tree(src_path):
    subprocess.run(["git", "add", "."],
                   cwd=src_path,
                   stdout=subprocess.DEVNULL)
    subprocess.run(['git', 'commit', '-m', 'tmp'],
                   cwd=src_path,
                   stdout=subprocess.DEVNULL)
    subprocess.run(["git", "reset", "--hard", "HEAD~1"],
                   cwd=src_path,
                   stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)


def apply_patches(src_path, patch_path) -> int:
    """
    Пытаемся применить патч к требуемому дереву сорцов.
    Возвращает:
    0 - успешно пропатчено
    1 - применение патча не удалось
    2 - патч уже присутствет в сорцах
    3 - файла, к которому применяется файл, нет в наличии
    """
    ps = subprocess.Popen(f"patch -p 1 < {patch_path}",
                          shell=True,
                          cwd=src_path,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    git_status = ps.communicate()[0].decode('utf-8')
    print(patch_path.stem, end=" - ")
    if 'FAILED' in git_status:
        print("Patching failed")
        return P_FAILED
    elif 'previously applied' in git_status:
        print("Patch already exists in a tree")
        return P_APPLIED
    elif "can't find file" in git_status:
        print("File supposed to be patched does not exist")
        return P_NOFILE
    else:
        print("Patching successful")
        return P_SUCCESS


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"{Path(sys.argv[0]).stem} путь-до-сорцов путь-до-патчей")
        exit(1)

    SRC_PATH = sys.argv[1]
    PATCH_PATH = sys.argv[2]
    patchlist = Path(PATCH_PATH).glob('*.patch')
    for patch in patchlist:
        if not check_src_tree(SRC_PATH):
            print("Something wrong with src tree")
            exit(1)
        apply_patches(SRC_PATH, patch)
        reset_git_tree(SRC_PATH)
