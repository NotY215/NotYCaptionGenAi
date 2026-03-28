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

        return base + File.separator + "resources";
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

        // Extract all resources
        extractResourceIfNeeded("/whisper/whisper-cli.exe", WHISPER_EXE_PATH);
        extractResourceIfNeeded("/whisper/whisper.dll", WHISPER_DLL_PATH);
        extractResourceIfNeeded("/Files/ffmpeg.exe", FFMPEG_PATH);
        extractResourceIfNeeded("/Files/ffprobe.exe", FFPROBE_PATH);

        File modelsDir = new File(MODELS_DIR);
        if (!modelsDir.exists()) {
            modelsDir.mkdirs();
            System.out.println("✓ Created models directory: " + MODELS_DIR);
        }
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
                if (destinationPath.endsWith(".exe")) {
                    destFile.setExecutable(true);
                }
                System.out.println("✓ Extracted: " + resourcePath);
            } else {
                System.err.println("⚠️ Resource not found in JAR: " + resourcePath);
            }
        } catch (Exception e) {
            // Silent fail
        }
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