package pro.noty.caption;

public class Config {
    // Application paths - Using correct whisper-cli.exe
    public static final String WHISPER_EXE_PATH = "resources/whisper/whisper-cli.exe";
    public static final String FFMPEG_PATH = "resources/files/ffmpeg.exe";
    public static final String FFPROBE_PATH = "resources/files/ffprobe.exe";
    public static final String MODELS_DIR = "resources/models/";

    // Download URLs for Whisper models
    public static final String MODEL_BASE_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-";

    // Browser links
    public static final String TELEGRAM_LINK = "https://t.me/NotY215";
    public static final String YOUTUBE_LINK = "https://www.youtube.com/@NotY215";

    // Subtitle modes
    public static final int MODE_NORMAL = 1;
    public static final int MODE_TRANSLATION = 2;
    public static final int MODE_TRANSLITERATION = 3;

    // Languages for transliteration
    public static final String[] TRANSLITERATION_LANGUAGES = {"ja", "hi"};

    // Whisper CLI command arguments
    public static final String[] WHISPER_ARGS = {
            "-t", "8",           // Threads
            "-p", "4",           // Processors
            "--print-progress",  // Show progress
            "--output-srt"       // Output SRT format
    };
}