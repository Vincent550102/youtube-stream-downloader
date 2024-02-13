import concurrent.futures
import subprocess

output_format = r'outputs\%(upload_date)s_%(title)s'
ytarchive_bin = r'bin\ytarchive.exe'
ffmpeg_bin = r'bin\ffmpeg.exe'

def record_live_stream(url):
    result = subprocess.run([ytarchive_bin, '-w', '--merge', '-o', output_format, '--ffmpeg-path', ffmpeg_bin, url, 'best'])
    return result

# 直播連結列表
with open('stream_list.txt', 'r') as f:
    live_urls = [url for url in f.read().splitlines() if url != ""]

print(live_urls)

# 使用 ThreadPoolExecutor 來同時錄製多個直播
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(record_live_stream, url) for url in live_urls]
    for future in concurrent.futures.as_completed(futures):
        try:
            result = future.result()
        except Exception as exc:
            print(f'錄製任務產生了一個異常: {exc}')
        else:
            print('錄製成功完成')
