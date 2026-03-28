package pro.noty.caption;

import java.io.File;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;

public class Config {
    // Base path for resources
    private static String basePath = null;

    public static String getBasePath() {
        if (basePath == null) {
            try {
                String path = Config.class.getProtectionDomain().getCodeSource().getLocation().getPath();
                File jarFile = new File(path);

                if (jarFile.isFile()) {
                    basePath = jarFile.getParentFile().getAbsolutePath();
                } else {
                    basePath = new File("").getAbsolutePath();
                }
            } catch (Exception e) {
                basePath = new File("").getAbsolutePath();
            }
        }
        return basePath;
    }

    public static String getResourcesDir() {
        String base = getBasePath();

        // Look for resources in Jre\lib\resources first
        String[] possiblePaths = {
                base + File.separator + ".." + File.separator + "lib" + File.separator + "resources",
                base + File.separator + "lib" + File.separator + "resources",
                base + File.separator + "resources",
                base + File.separator + ".." + File.separator + "resources",
                new File("").getAbsolutePath() + File.separator + "resources"
        };

        for (String path : possiblePaths) {
            File dir = new File(path);
            if (dir.exists() && dir.isDirectory()) {
                System.out.println("📁 Found resources at: " + path);
                return path;
            }
        }

        // Default to Jre\lib\resources
        String defaultPath = base + File.separator + ".." + File.separator + "lib" + File.separator + "resources";
        System.out.println("📁 Using default resources path: " + defaultPath);
        return defaultPath;
    }

    public static final String RESOURCES_DIR = getResourcesDir() + File.separator;

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

        System.out.println("📁 Resource Directory: " + RESOURCES_DIR);
        System.out.println("📁 Models Directory: " + MODELS_DIR);

        // Create directories if they don't exist
        File whisperDir = new File(RESOURCES_DIR + "whisper");
        File filesDir = new File(RESOURCES_DIR + "Files");
        File modelsDir = new File(MODELS_DIR);

        if (!whisperDir.exists()) whisperDir.mkdirs();
        if (!filesDir.exists()) filesDir.mkdirs();
        if (!modelsDir.exists()) modelsDir.mkdirs();

        // Check if files exist
        checkAndLogFile(WHISPER_EXE_PATH, "whisper-cli.exe");
        checkAndLogFile(WHISPER_DLL_PATH, "whisper.dll");
        checkAndLogFile(FFMPEG_PATH, "ffmpeg.exe");
        checkAndLogFile(FFPROBE_PATH, "ffprobe.exe");

        // List existing models
        File[] models = modelsDir.listFiles((dir, name) -> name.endsWith(".bin"));
        if (models != null && models.length > 0) {
            System.out.println("✓ Found existing models:");
            for (File model : models) {
                System.out.println("   - " + model.getName() + " (" + formatSize(model.length()) + ")");
            }
        } else {
            System.out.println("⚠️ No models found. They will be downloaded when needed.");
        }
    }

    private static void checkAndLogFile(String path, String name) {
        File file = new File(path);
        if (file.exists()) {
            System.out.println("✓ Found: " + name);
        } else {
            System.out.println("⚠️ Missing: " + name + " at " + path);
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