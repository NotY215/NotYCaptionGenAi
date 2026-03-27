package pro.noty.caption;

import pro.noty.caption.model.CaptionConfig;
import pro.noty.caption.service.*;
import pro.noty.caption.util.ConsoleUtils;
import java.io.File;
import java.util.Scanner;

public class Main {
    private static final String[] ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mkv", ".mov", ".mp3", ".wav", ".m4a", ".flac", ".webm", ".m4v", ".mpg", ".mpeg"};
    private static Scanner scanner = null;

    private static Scanner getScanner() {
        if (scanner == null) {
            scanner = new Scanner(System.in);
        }
        return scanner;
    }

    public static void main(String[] args) {
        ConsoleUtils.clearScreen();
        System.out.println("╔═══════════════════════════════════════════╗");
        System.out.println("║     NOTY CAPTION GENERATOR AI v1.0       ║");
        System.out.println("║     Powered by Whisper.cpp               ║");
        System.out.println("╚═══════════════════════════════════════════╝");
        System.out.println();

        // Show current paths for debugging
        System.out.println("📁 Resource Directory: " + Config.RESOURCES_DIR);
        System.out.println("🔧 Checking required files...\n");

        // Check if required executables exist
        if (!checkRequiredFiles()) {
            System.out.println("\n❌ Required files are missing! Please check the installation.");
            System.out.println("\n📝 Expected file locations:");
            System.out.println("   " + Config.WHISPER_EXE_PATH);
            System.out.println("   " + Config.FFMPEG_PATH);
            System.out.println("   " + Config.FFPROBE_PATH);
            System.out.println("\n💡 Tip: Your current structure:");
            System.out.println("   " + Config.RESOURCES_DIR);
            System.out.println("   ├── whisper/");
            System.out.println("   │   └── whisper-cli.exe");
            System.out.println("   ├── Files/        ← Note: Capital F");
            System.out.println("   │   ├── ffmpeg.exe");
            System.out.println("   │   └── ffprobe.exe");
            System.out.println("   └── Models/       ← Note: Capital M");
            System.out.println("       ├── ggml-tiny.bin");
            System.out.println("       └── ggml-base.bin");
            System.out.println("\nPress Enter to exit...");
            getScanner().nextLine();
            return;
        }

        System.out.println("✅ All required files found!\n");

        boolean continueApp = true;

        while (continueApp) {
            try {
                // Step a: Get video/audio path
                System.out.println("\n💡 Tip: You can drag and drop a file here, then press Enter");
                System.out.println("   Or type the full path (e.g., C:\\Videos\\test.mp4)");
                String mediaPath = InputHandler.getMediaPath(ALLOWED_EXTENSIONS);

                System.out.println("\n✅ Selected file: " + mediaPath);

                while (true) {
                    // Step b: Main menu
                    int choice = InputHandler.showMainMenu();

                    if (choice == 0) {
                        // Go back to path selection
                        break;
                    }

                    // Step c: Model selection
                    int modelChoice = InputHandler.selectModel();
                    if (modelChoice == 0) {
                        continue;
                    }

                    String modelName = getModelName(modelChoice);
                    String modelSize = getModelSize(modelChoice);
                    String modelPath = Config.MODELS_DIR + "ggml-" + modelName + ".bin";

                    // Step d: Download or continue
                    boolean modelExists = ModelManager.checkModelExists(modelPath);
                    int downloadChoice = InputHandler.handleModelDownload(modelName, modelSize, modelExists);

                    if (downloadChoice == 0) {
                        continue;
                    }

                    if (downloadChoice == 1 && !modelExists) {
                        // Download model
                        System.out.println("\n📥 Downloading model... This may take a while.");
                        boolean downloaded = ModelManager.downloadModel(modelName, modelPath);
                        if (!downloaded) {
                            System.out.println("\n❌ Failed to download model. Please check your internet connection.");
                            System.out.print("Press Enter to continue...");
                            getScanner().nextLine();
                            continue;
                        }
                    }

                    // Step e: Choose word or letter preference
                    int preferenceChoice = InputHandler.choosePreference();
                    if (preferenceChoice == 0) {
                        continue;
                    }

                    // Step e2: Choose subtitle mode
                    int modeChoice = InputHandler.chooseSubtitleMode();
                    if (modeChoice == 0) {
                        continue;
                    }

                    // Step f: Number per line
                    int numberPerLine = InputHandler.getNumberPerLine(preferenceChoice);
                    if (numberPerLine == 0) {
                        continue;
                    }

                    // Step g: Confirm and generate
                    CaptionConfig config = new CaptionConfig(
                            mediaPath, modelPath, modelName,
                            preferenceChoice == 1 ? "words" : "letters",
                            numberPerLine,
                            modeChoice
                    );

                    boolean confirmed = InputHandler.confirmGeneration(config);
                    if (!confirmed) {
                        continue;
                    }

                    // Generate captions
                    System.out.println("\n🎬 Generating captions... This may take several minutes.");
                    CaptionGenerator generator = new CaptionGenerator();
                    boolean success = generator.generateCaptions(config);

                    if (success) {
                        System.out.println("\n✅ Thanks For using NotY Caption Generator AI!");
                        System.out.println("Your caption has been generated successfully!");
                        System.out.println("📄 Output file: " + config.getOutputPath());

                        // Open browser links
                        BrowserOpener.openLinks();

                        // Step h: Next video or quit
                        int nextChoice = InputHandler.handleNextVideo();
                        if (nextChoice == 1) {
                            continueApp = false;
                            System.out.println("\n╔═══════════════════════════════════════════╗");
                            System.out.println("║     Thank you for using our app!         ║");
                            System.out.println("║     Visit us again!                      ║");
                            System.out.println("╚═══════════════════════════════════════════╝");
                            break;
                        } else {
                            break; // Go back to start for next video
                        }
                    } else {
                        System.out.println("\n❌ Failed to generate captions. Please try again.");
                        Thread.sleep(2000);
                        break;
                    }
                }
            } catch (Exception e) {
                System.err.println("Error: " + e.getMessage());
                e.printStackTrace();
                System.out.println("\nPress Enter to continue...");
                getScanner().nextLine();
            }
        }

        if (scanner != null) {
            scanner.close();
        }
    }

    private static boolean checkRequiredFiles() {
        boolean allGood = true;

        // Check if resources directory exists
        File resourcesDir = new File(Config.RESOURCES_DIR);
        if (!resourcesDir.exists()) {
            System.err.println("❌ Resources directory not found: " + Config.RESOURCES_DIR);
            allGood = false;
        } else {
            System.out.println("✓ Resources directory found");
        }

        // Check whisper-cli.exe
        File whisper = new File(Config.WHISPER_EXE_PATH);
        if (!whisper.exists()) {
            System.err.println("❌ Missing: " + Config.WHISPER_EXE_PATH);
            allGood = false;
        } else {
            System.out.println("✓ Found: " + whisper.getName());
        }

        // Check ffmpeg.exe
        File ffmpeg = new File(Config.FFMPEG_PATH);
        if (!ffmpeg.exists()) {
            System.err.println("❌ Missing: " + Config.FFMPEG_PATH);
            allGood = false;
        } else {
            System.out.println("✓ Found: " + ffmpeg.getName());
        }

        // Check ffprobe.exe
        File ffprobe = new File(Config.FFPROBE_PATH);
        if (!ffprobe.exists()) {
            System.err.println("❌ Missing: " + Config.FFPROBE_PATH);
            allGood = false;
        } else {
            System.out.println("✓ Found: " + ffprobe.getName());
        }

        // Check models directory
        File modelsDir = new File(Config.MODELS_DIR);
        if (!modelsDir.exists()) {
            System.err.println("⚠️ Models directory not found, will create: " + Config.MODELS_DIR);
            modelsDir.mkdirs();
        } else {
            System.out.println("✓ Models directory found");

            // List existing models
            File[] models = modelsDir.listFiles((dir, name) -> name.endsWith(".bin"));
            if (models != null && models.length > 0) {
                System.out.println("   Existing models:");
                for (File model : models) {
                    System.out.println("   - " + model.getName());
                }
            }
        }

        return allGood;
    }

    private static String getModelName(int choice) {
        switch (choice) {
            case 1: return "tiny";
            case 2: return "base";
            case 3: return "small";
            case 4: return "medium";
            case 5: return "large";
            default: return "base";
        }
    }

    private static String getModelSize(int choice) {
        switch (choice) {
            case 1: return "75 MB";
            case 2: return "150 MB";
            case 3: return "500 MB";
            case 4: return "1.5 GB";
            case 5: return "2.9 GB";
            default: return "150 MB";
        }
    }
}