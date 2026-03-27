package pro.noty.caption;

import java.io.File;

public class Config {
    // Get the base path (where the JAR or class files are running from)
    private static String getBasePath() {
        try {
            String path = Config.class.getProtectionDomain().getCodeSource().getLocation().getPath();
            File jarFile = new File(path);
            if (jarFile.isFile()) {
                // Running from JAR - return the directory containing the JAR
                return jarFile.getParentFile().getAbsolutePath();
            } else {
                // Running from IDE - return the project root
                return new File("").getAbsolutePath();
            }
        } catch (Exception e) {
            return new File("").getAbsolutePath();
        }
    }

    // Get the correct resources path (works both in IDE and JAR)
    private static String getResourcesPath() {
        String basePath = getBasePath();

        // Try multiple possible locations
        String[] possiblePaths = {
                basePath + File.separator + "src" + File.separator + "main" + File.separator + "resources",
                basePath + File.separator + "resources",
                basePath + File.separator + "build" + File.separator + "resources" + File.separator + "main",
                new File("").getAbsolutePath() + File.separator + "src" + File.separator + "main" + File.separator + "resources"
        };

        for (String path : possiblePaths) {
            File dir = new File(path);
            if (dir.exists() && dir.isDirectory()) {
                return path;
            }
        }

        // Default to the first option
        return possiblePaths[0];
    }

    // Application paths
    public static final String RESOURCES_DIR = getResourcesPath() + File.separator;
    public static final String WHISPER_EXE_PATH = RESOURCES_DIR + "whisper" + File.separator + "whisper-cli.exe";
    public static final String FFMPEG_PATH = RESOURCES_DIR + "files" + File.separator + "ffmpeg.exe";
    public static final String FFPROBE_PATH = RESOURCES_DIR + "files" + File.separator + "ffprobe.exe";
    public static final String MODELS_DIR = RESOURCES_DIR + "models" + File.separator;

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
}