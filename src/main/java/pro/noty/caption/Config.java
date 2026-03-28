package pro.noty.caption;

import java.io.File;

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

    // Resources are always in Jre\lib\resources relative to the JAR location
    public static String getResourcesDir() {
        String base = getBasePath();
        // JAR is in Jre\bin\App.jar, so resources are in Jre\lib\resources
        String resourcesPath = base + File.separator + ".." + File.separator + "lib" + File.separator + "resources";

        // Normalize the path
        try {
            File resourcesDir = new File(resourcesPath);
            return resourcesDir.getCanonicalPath();
        } catch (Exception e) {
            return resourcesPath;
        }
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
        new File(RESOURCES_DIR + "whisper").mkdirs();
        new File(RESOURCES_DIR + "Files").mkdirs();
        new File(MODELS_DIR).mkdirs();

        // Check files
        checkFile(WHISPER_EXE_PATH, "whisper-cli.exe");
        checkFile(WHISPER_DLL_PATH, "whisper.dll");
        checkFile(FFMPEG_PATH, "ffmpeg.exe");
        checkFile(FFPROBE_PATH, "ffprobe.exe");

        // List models
        File modelsDir = new File(MODELS_DIR);
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

    private static void checkFile(String path, String name) {
        File file = new File(path);
        if (file.exists()) {
            System.out.println("✓ Found: " + name);
        } else {
            System.err.println("⚠️ Missing: " + name + " at " + path);
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