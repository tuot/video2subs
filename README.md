# 视频字幕生成工具

这是一个使用 `faster-whisper` 库从视频文件中提取音频并生成 SRT 和 VTT 字幕文件的 Python 脚本。它支持通过命令行参数灵活配置 Whisper 模型、设备和计算类型。

## 功能

- **音频提取：** 从常见的视频格式（如 MP4）中提取音频。
- **字幕生成：** 使用 `faster-whisper` 库转录音频，并生成标准的 SRT 和 VTT 字幕文件。
- **语言指定：** 可以选择指定视频的语言进行转录，或让程序自动检测。
- **模型配置：** 支持通过命令行参数选择不同的 Whisper 模型大小（tiny, small, medium, large-v2, large-v3）。
- **设备选择：** 可以指定在 CPU 或 CUDA 设备上运行模型（如果 CUDA 可用）。
- **计算类型选择：** 支持不同的计算类型（int8, float16, float32）以优化性能和显存使用。
- **自定义输出：** 可以通过命令行参数设置输出字幕文件的基本名称。

## 依赖

- Python 3.6 或更高版本
- `faster-whisper` 库 (`pip install faster-whisper`)
- `ffmpeg` (需要安装并在系统路径中可用)

## 安装

1.  **安装 `faster-whisper` 库：**

    ```bash
    pip install faster-whisper
    ```

2.  **安装 `ffmpeg`：**
    - **Linux (Debian/Ubuntu):**
      ```bash
      sudo apt update
      sudo apt install ffmpeg
      ```
    - **Linux (Fedora/CentOS):**
      ```bash
      sudo dnf install ffmpeg
      ```
    - **macOS:**
      ```bash
      brew install ffmpeg
      ```
      (需要先安装 Homebrew)
    - **Windows:**
      - 可以从 [FFmpeg 官网](https://ffmpeg.org/download.html) 下载预编译的二进制文件。
      - 下载后，请将 `ffmpeg.exe` 所在的目录添加到系统的环境变量 `Path` 中。

## 使用方法

在命令行中运行脚本 `main.py`，并提供视频文件路径作为参数。

```bash
python main.py your_video.mp4
```
