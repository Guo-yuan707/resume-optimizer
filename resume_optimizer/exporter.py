"""导出模块(第 9 课):把 AI 改写好的简历文本保存成文件。

职责就一件事:把内存里的字符串写到磁盘上的文件里。
——这叫"文件写入",和第 1 课学的"文件读取"(read_text)正好是相反的操作:

    读取:文件 → 字符串   open(path, "r")
    写入:字符串 → 文件   open(path, "w")
"""
import os


def save_resume(resume_text: str, output_path: str) -> str:
    """把简历文本写入文件，返回文件路径。

    参数:
        resume_text: 要保存的文本(通常是 AI 改写后的整份简历)
        output_path: 存到哪个文件，例如 "output/optimized_resume.txt"

    返回:
        保存好的文件路径(方便调用方打印"已保存到 xxx")

    三个知识点(和第 1 课读文件正好对称):
        1. "w" = write 写模式:文件不存在会新建,存在会【整个覆盖】
        2. with open(...) as f:文件用完自动关闭(读的时候也是一样)
        3. encoding="utf-8":写中文必须指定,不然按系统编码写会乱码
    """
    # 如果文件夹还不存在,先建出来(不然 open 会报错)
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(resume_text)

    return output_path
