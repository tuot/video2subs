import os
import subprocess
import datetime
import argparse
import tempfile
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


def format_timestamp(seconds, format_type="srt"):
    """格式化时间戳为 SRT 或 VTT 格式。"""
    delta = datetime.timedelta(seconds=seconds)
    time_str = str(delta).split(".")[0].zfill(8)  # HH:MM:SS
    milliseconds = str(int(delta.microseconds / 1000)).zfill(3)
    if format_type == "srt":
        return time_str.replace(":", ",") + f",{milliseconds}"
    elif format_type == "vtt":
        return time_str + f".{milliseconds}"
    else:
        raise ValueError("format_type 必须是 'srt' 或 'vtt'")


def generate_srt(segments, output_srt_path):
    """生成 SRT 字幕文件。"""
    with open(output_srt_path, "w", encoding="utf-8") as srt_file:
        segment_id = 1
        for segment in segments:
            start_time = format_timestamp(segment.start, "srt")
            end_time = format_timestamp(segment.end, "srt")
            srt_file.write(f"{segment_id}\n")
            srt_file.write(f"{start_time} --> {end_time}\n")
            srt_file.write(f"{segment.text.strip()}\n\n")
            segment_id += 1
    print(f"SRT 字幕已生成: {output_srt_path}")


def generate_vtt(segments, output_vtt_path):
    """生成 VTT 字幕文件。"""
    with open(output_vtt_path, "w", encoding="utf-8") as vtt_file:
        vtt_file.write("WEBVTT\n\n")
        for segment in segments:
            start_time = format_timestamp(segment.start, "vtt")
            end_time = format_timestamp(segment.end, "vtt")
            vtt_file.write(f"{start_time} --> {end_time}\n")
            vtt_file.write(f"{segment.text.strip()}\n\n")
    print(f"VTT 字幕已生成: {output_vtt_path}")


def create_subtitles(
    video_path, output_base, model_size, device, compute_type, language=None
):
    """为视频文件创建 SRT 和 VTT 字幕文件，并根据参数初始化 WhisperModel。"""
    try:
        # 初始化 WhisperModel
        model = WhisperModel(model_size, device=device, compute_type=compute_type)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp_audio:
            temp_audio_path = tmp_audio.name
            extract_audio(video_path, temp_audio_path)
            segments, info = transcribe_audio(model, temp_audio_path, language)

            srt_output_path = f"{output_base}.srt"
            generate_srt(segments, srt_output_path)

            vtt_output_path = f"{output_base}.vtt"
            generate_vtt(segments, vtt_output_path)

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
        description="从视频文件生成 SRT 和 VTT 字幕，并可配置 Whisper 模型。"
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
