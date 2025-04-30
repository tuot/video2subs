import os
import subprocess
import datetime
import argparse
import tempfile
import mimetypes
from faster_whisper import WhisperModel


def extract_audio(video_path, audio_path):
    """从视频文件中提取音频。"""
    try:
        command = [
            "ffmpeg",
            "-i",
            video_path,
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            audio_path,
            "-y",
        ]
        print(" ".join(command))
        subprocess.run(command, check=True, capture_output=True)
        print(f"音频已提取到: {audio_path}")
    except FileNotFoundError:
        raise FileNotFoundError(
            "ffmpeg 未找到。请确保已安装 ffmpeg 并将其添加到系统路径。"
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"提取音频失败: {e.stderr.decode()}")


def transcribe_audio(model, audio_path, language=None):
    """使用给定的 WhisperModel 转录音频文件。"""
    segments, info = model.transcribe(
        audio_path,
        language=language,
        word_timestamps=True,
        vad_filter=True,
    )
    return segments, info


def format_timestamp(seconds):
    """格式化时间戳为 SRT 格式。
    格式：HH:MM:SS,mmm
    例如：00:01:23,456
    """
    delta = datetime.timedelta(seconds=seconds)
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    seconds = delta.seconds % 60
    milliseconds = delta.microseconds // 1000

    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def generate_srt(segments, output_srt_path):
    """生成 SRT 字幕文件。"""
    with open(output_srt_path, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(segments, 1):
            start_time = format_timestamp(segment.start)
            end_time = format_timestamp(segment.end)
            text = segment.text.strip()

            # 写入字幕序号
            srt_file.write(f"{i}\n")
            # 写入时间轴
            srt_file.write(f"{start_time} --> {end_time}\n")
            # 写入字幕文本
            srt_file.write(f"{text}\n")
            # 写入空行分隔
            srt_file.write("\n")

    print(f"SRT 字幕已生成: {output_srt_path}")


def is_video_file(file_path):
    """判断文件是否为视频文件。"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type and mime_type.startswith("video/")


def create_subtitles(
    video_path, output_base, model_size, device, compute_type, language=None
):
    """为视频文件创建 SRT 和 VTT 字幕文件，并根据参数初始化 WhisperModel。"""
    try:
        # 初始化 WhisperModel
        model = WhisperModel(model_size, device=device, compute_type=compute_type)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp_audio:
            temp_audio_path = tmp_audio.name

            # 判断文件类型，只有视频文件才需要提取音频
            if is_video_file(video_path):
                print(f"检测到视频文件: {video_path}")
                extract_audio(video_path, temp_audio_path)
            else:
                print(f"检测到音频文件: {video_path}")
                temp_audio_path = video_path

            segments, info = transcribe_audio(model, temp_audio_path, language)

            srt_output_path = f"{output_base}.srt"
            generate_srt(segments, srt_output_path)

            print(
                f"检测到的语言: {info.language} (置信度: {info.language_probability:.2f})"
            )

    except FileNotFoundError as e:
        print(f"错误: {e}")
    except RuntimeError as e:
        print(f"错误: {e}")
    finally:
        # 显式地卸载模型以释放资源 (如果适用)
        del model


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="从视频或音频文件生成 SRT 字幕，并可配置 Whisper 模型。"
    )
    parser.add_argument("video_path", help="输入视频文件的路径")
    parser.add_argument(
        "-o",
        "--output_base",
        default="output",
        help="输出字幕文件的基本名称 (默认为 'output')",
    )
    parser.add_argument(
        "-l", "--language", default=None, help="指定音频语言 (默认为自动检测)"
    )
    parser.add_argument(
        "-m",
        "--model_size",
        default="medium",
        choices=["tiny", "small", "medium", "large-v2", "large-v3"],
        help="Whisper 模型大小 (默认为 'medium')",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        choices=["cpu", "cuda"],
        help="运行设备 (默认为 'cpu')",
    )
    parser.add_argument(
        "--compute_type",
        default="int8",
        choices=["int8", "float16", "float32"],
        help="计算类型 (默认为 'int8')",
    )

    args = parser.parse_args()

    create_subtitles(
        args.video_path,
        args.output_base,
        args.model_size,
        args.device,
        args.compute_type,
        args.language,
    )
