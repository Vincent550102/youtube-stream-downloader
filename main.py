import concurrent.futures
import subprocess
import threading

output_format = r'outputs\%(upload_date)s_%(title)s'
ytarchive_bin = r'bin\ytarchive.exe'
ffmpeg_bin = r'bin\ffmpeg.exe'
yt_dlp_bin = r'bin\yt-dlp.exe'


output_format = r'outputs\%(upload_date)s_%(title)s'
ytarchive_bin = r'bin\ytarchive.exe'
ffmpeg_bin = r'bin\ffmpeg.exe'
yt_dlp_bin = r'bin\yt-dlp.exe'


def read_stream_and_check(stream, prefix, check_string, callback, url):
    """檢測到特定字串，使用 callback 函數"""
    found = False
    for line in stream:
        print(f"{url} | {prefix}{line}", end='', flush=True)
        if check_string in line and not found:
            found = True
            callback(url)
    return found


def start_yt_dlp(url):
    """使用 yt-dlp 下載"""
    print(f"檢測到直播已結束，使用一般方式下載: {url}")
    subprocess.run([yt_dlp_bin, '-o', output_format,
                   '--ffmpeg-location', ffmpeg_bin, url], capture_output=False)


def record_live_stream(url):
    print(f"正在使用直播錄製工具: {url}")
    proc = subprocess.Popen(
        [ytarchive_bin, '-w', '--merge', '-o', output_format,
            '--ffmpeg-path', ffmpeg_bin, url, 'best'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', bufsize=1)

    # 分別處理 stdout 和 stderr
    threads = [
        threading.Thread(target=read_stream_and_check, args=(
            proc.stdout, "stdout: ", "yt-dlp", start_yt_dlp, url)),
        threading.Thread(target=read_stream_and_check, args=(
            proc.stderr, "stderr: ", "yt-dlp", start_yt_dlp, url))
    ]

    # 啟動線程
    for thread in threads:
        thread.start()

    # 等待線程結束
    for thread in threads:
        thread.join()

    # 等待進程結束
    proc.wait()

    print(f"{url} 完成錄製")


with open('stream_list.txt', 'r') as f:
    live_urls = [url.split("|")[0]
                 for url in f.read().splitlines() if url != ""]

print(f"正在處理以下直播連結 {live_urls}")

# 使用 ThreadPoolExecutor 來同時錄製多個直播
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(record_live_stream, url) for url in live_urls]
    for future in concurrent.futures.as_completed(futures):
        future.result()

print('錄製成功完成。')
