package pro.noty.caption;

import java.io.File;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;

public class Config {

    // Get the actual directory where App.jar is located
    private static String getJarDirectory() {
        try {
            // Get the location of the JAR file
            String path = Config.class.getProtectionDomain().getCodeSource().getLocation().getPath();

            // Decode URL encoding
            path = URLDecoder.decode(path, StandardCharsets.UTF_8.name());

            // Remove "file:" prefix if present
            if (path.startsWith("file:")) {
                path = path.substring(5);
            }

            // Remove leading slash on Windows
            if (path.startsWith("/") && System.getProperty("os.name").contains("Windows")) {
                path = path.substring(1);
            }

            File jarFile = new File(path);

            // Get the parent directory
            String jarDir = jarFile.getParentFile().getAbsolutePath();

            System.out.println("DEBUG: JAR path from CodeSource: " + path);
            System.out.println("DEBUG: JAR directory: " + jarDir);

            return jarDir;
        } catch (Exception e) {
            System.err.println("Error getting JAR directory: " + e.getMessage());
            return new File("").getAbsolutePath();
        }
    }

    // Resources are in the "resources" folder next to App.jar
    public static final String RESOURCES_DIR = getJarDirectory() + File.separator + "resources" + File.separator;

    public static String WHISPER_EXE_PATH;
    public static String WHISPER_DLL_PATH;
    public static String FFMPEG_PATH;
    public static String FFPROBE_PATH;
    public static String MODELS_DIR;

    static {
        WHISPER_EXE_PATH = RESOURCES_DIR + "whisper" + File.separator + "whisper-cli.exe";
        WHISPER_DLL_PATH = RESOURCES_DIR + "whisper" + File.separator + "whisper.dll";
        FFMPEG_PATH = RESOURCES_DIR + "Files" + File.separator + "ffmpeg.exe";
        FFPROBE_PATH = RESOURCES_DIR + "Files" + File.separator + "ffprobe.exe";
        MODELS_DIR = RESOURCES_DIR + "Models" + File.separator;

        System.out.println("DEBUG: Resources Directory: " + RESOURCES_DIR);
        System.out.println("DEBUG: Whisper Path: " + WHISPER_EXE_PATH);
        System.out.println("DEBUG: FFmpeg Path: " + FFMPEG_PATH);
        System.out.println("DEBUG: Models Directory: " + MODELS_DIR);

        // Create directories if they don't exist
        new File(RESOURCES_DIR + "whisper").mkdirs();
        new File(RESOURCES_DIR + "Files").mkdirs();
        new File(MODELS_DIR).mkdirs();

        // Check files with absolute paths
        File whisperExe = new File(WHISPER_EXE_PATH);
        File whisperDll = new File(WHISPER_DLL_PATH);
        File ffmpeg = new File(FFMPEG_PATH);
        File ffprobe = new File(FFPROBE_PATH);

        System.out.println("\n🔍 File Check:");
        System.out.println("  whisper-cli.exe exists: " + whisperExe.exists() + " - " + WHISPER_EXE_PATH);
        System.out.println("  whisper.dll exists: " + whisperDll.exists() + " - " + WHISPER_DLL_PATH);
        System.out.println("  ffmpeg.exe exists: " + ffmpeg.exists() + " - " + FFMPEG_PATH);
        System.out.println("  ffprobe.exe exists: " + ffprobe.exists() + " - " + FFPROBE_PATH);

        if (whisperExe.exists()) {
            System.out.println("✓ Found: whisper-cli.exe");
        } else {
            System.err.println("⚠️ Missing: whisper-cli.exe at " + WHISPER_EXE_PATH);
        }

        if (whisperDll.exists()) {
            System.out.println("✓ Found: whisper.dll");
        } else {
            System.err.println("⚠️ Missing: whisper.dll at " + WHISPER_DLL_PATH);
        }

        if (ffmpeg.exists()) {
            System.out.println("✓ Found: ffmpeg.exe");
        } else {
            System.err.println("⚠️ Missing: ffmpeg.exe at " + FFMPEG_PATH);
        }

        if (ffprobe.exists()) {
            System.out.println("✓ Found: ffprobe.exe");
        } else {
            System.err.println("⚠️ Missing: ffprobe.exe at " + FFPROBE_PATH);
        }

        // List models
        File modelsDir = new File(MODELS_DIR);
        File[] models = modelsDir.listFiles((dir, name) -> name.endsWith(".bin"));
        if (models != null && models.length > 0) {
            System.out.println("\n✓ Found existing models:");
            for (File model : models) {
                System.out.println("   - " + model.getName() + " (" + formatSize(model.length()) + ")");
            }
        } else {
            System.out.println("\n⚠️ No models found. They will be downloaded when needed.");
        }
    }

    private static String formatSize(long bytes) {
        if (bytes < 1024) return bytes + " B";
        int exp = (int) (Math.log(bytes) / Math.log(1024));
        String pre = "KMGTPE".charAt(exp - 1) + "";
        return String.format("%.1f %sB", bytes / Math.pow(1024, exp), pre);
    }

    // Model download URLs
    public static final String MODEL_TINY_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin";
    public static final String MODEL_BASE_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin";
    public static final String MODEL_SMALL_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin";
    public static final String MODEL_MEDIUM_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin";
    public static final String MODEL_LARGE_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v1.bin";

    public static final String TELEGRAM_LINK = "https://t.me/NotY215";
    public static final String YOUTUBE_LINK = "https://www.youtube.com/@NotY215";

    public static final int MODE_NORMAL = 1;
    public static final int MODE_TRANSLATION = 2;
    public static final int MODE_TRANSLITERATION = 3;

    public static final String[] TRANSLITERATION_LANGUAGES = {"ja", "hi"};
}