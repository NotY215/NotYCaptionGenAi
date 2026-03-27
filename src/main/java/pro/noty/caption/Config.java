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
                // Get the directory where the JAR or class files are running from
                String path = Config.class.getProtectionDomain().getCodeSource().getLocation().getPath();
                File jarFile = new File(path);

                if (jarFile.isFile()) {
                    // Running from JAR - use the directory containing the JAR
                    basePath = jarFile.getParentFile().getAbsolutePath();
                } else {
                    // Running from IDE - use the project root
                    basePath = new File("").getAbsolutePath();
                }
            } catch (Exception e) {
                basePath = new File("").getAbsolutePath();
            }
        }
        return basePath;
    }

    // Resources directory - try multiple possible locations
    public static String getResourcesDir() {
        String base = getBasePath();

        // Try multiple possible resource locations
        String[] possiblePaths = {
                base + File.separator + "resources",
                base + File.separator + ".." + File.separator + "resources",
                base + File.separator + "Jre" + File.separator + "bin" + File.separator + "resources",
                new File("").getAbsolutePath() + File.separator + "resources"
        };

        for (String path : possiblePaths) {
            File dir = new File(path);
            if (dir.exists() && dir.isDirectory()) {
                return path;
            }
        }

        // Default to resources in current directory
        return base + File.separator + "resources";
    }

    public static final String RESOURCES_DIR = getResourcesDir() + File.separator;

    // Application paths
    public static String WHISPER_EXE_PATH;
    public static String FFMPEG_PATH;
    public static String FFPROBE_PATH;
    public static String MODELS_DIR;

    static {
        // Initialize paths
        WHISPER_EXE_PATH = RESOURCES_DIR + "whisper" + File.separator + "whisper-cli.exe";
        FFMPEG_PATH = RESOURCES_DIR + "Files" + File.separator + "ffmpeg.exe";
        FFPROBE_PATH = RESOURCES_DIR + "Files" + File.separator + "ffprobe.exe";
        MODELS_DIR = RESOURCES_DIR + "Models" + File.separator;

        System.out.println("📁 Resource Directory: " + RESOURCES_DIR);
        System.out.println("📁 Models Directory: " + MODELS_DIR);

        // Check for existing models
        File modelsDir = new File(MODELS_DIR);
        if (modelsDir.exists()) {
            File[] models = modelsDir.listFiles((dir, name) -> name.endsWith(".bin"));
            if (models != null && models.length > 0) {
                System.out.println("✓ Found existing models:");
                for (File model : models) {
                    System.out.println("   - " + model.getName() + " (" + formatSize(model.length()) + ")");
                }
            }
        } else {
            modelsDir.mkdirs();
            System.out.println("✓ Created models directory: " + MODELS_DIR);
        }

        // Extract resources from JAR if needed
        extractResourceIfNeeded("/whisper/whisper-cli.exe", WHISPER_EXE_PATH);
        extractResourceIfNeeded("/Files/ffmpeg.exe", FFMPEG_PATH);
        extractResourceIfNeeded("/Files/ffprobe.exe", FFPROBE_PATH);
    }

    private static void extractResourceIfNeeded(String resourcePath, String destinationPath) {
        File destFile = new File(destinationPath);
        if (destFile.exists()) {
            return;
        }

        File parentDir = destFile.getParentFile();
        if (parentDir != null && !parentDir.exists()) {
            parentDir.mkdirs();
        }

        try (InputStream is = Config.class.getResourceAsStream(resourcePath)) {
            if (is != null) {
                Files.copy(is, destFile.toPath(), StandardCopyOption.REPLACE_EXISTING);
                destFile.setExecutable(true);
                System.out.println("✓ Extracted: " + resourcePath);
            }
        } catch (Exception e) {
            // Silent fail - files might not be in JAR
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