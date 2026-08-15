"""测试导出模块(第 9 课):测 save_resume 把文本写进文件。

不联网、不花钱——save_resume 是纯本地文件操作,正好该测。

tmp_path:pytest 内置的"临时文件夹",每个测试自动分一个,
    测完自动清理,不会把文件写进项目目录。
"""
from resume_optimizer.exporter import save_resume


def test_save_resume_writes_content(tmp_path):
    """写入的内容能原样读回来(round-trip),说明编码和内容都没坏。"""
    output = tmp_path / "optimized.txt"
    save_resume("郭园\n专业技能\nPython", str(output))
    with open(output, "r", encoding="utf-8") as f:
        content = f.read()
    assert content == "郭园\n专业技能\nPython"


def test_save_resume_creates_missing_dir(tmp_path):
    """文件夹不存在时,save_resume 会自己建出来。"""
    output = tmp_path / "nested" / "dir" / "resume.txt"
    save_resume("你好", str(output))
    assert output.exists()


def test_save_resume_returns_path(tmp_path):
    """返回值就是传进去的路径,方便调用方打印"已保存到 xxx"。"""
    output = tmp_path / "resume.txt"
    result = save_resume("x", str(output))
    assert result == str(output)
