package pro.noty.caption.service;

import pro.noty.caption.model.CaptionConfig;
import pro.noty.caption.util.FileValidator;
import pro.noty.caption.Config;

import java.util.Scanner;

public class InputHandler {
    private static Scanner scanner = null;

    private static Scanner getScanner() {
        if (scanner == null) {
            scanner = new Scanner(System.in);
        }
        return scanner;
    }

    public static String getMediaPath(String[] allowedExtensions) {
        Scanner sc = getScanner();
        while (true) {
            try {
                System.out.print("\n📂 Provide Video/Audio Path");
                System.out.print("\n   Allowed extensions: ");
                System.out.print(String.join(", ", allowedExtensions));
                System.out.print("\n➤ ");

                String path = sc.nextLine().trim().replace("\"", "");

                if (path.isEmpty()) {
                    System.out.println("❌ Path cannot be empty! Please enter a valid path.");
                    continue;
                }

                if (FileValidator.validateMediaFile(path, allowedExtensions)) {
                    return path;
                }

                System.out.println("❌ Invalid file! File doesn't exist or has wrong extension.");
                System.out.println("   Please try again.\n");
            } catch (Exception e) {
                System.err.println("Error reading input: " + e.getMessage());
                // Reset scanner on error
                scanner = new Scanner(System.in);
            }
        }
    }

    public static int showMainMenu() {
        Scanner sc = getScanner();
        while (true) {
            try {
                System.out.println("\n┌─────────────────────────────────┐");
                System.out.println("│         MAIN MENU               │");
                System.out.println("├─────────────────────────────────┤");
                System.out.println("│  1) Choose Model               │");
                System.out.println("│  0) Go Back (Resend video path)│");
                System.out.println("└─────────────────────────────────┘");
                System.out.print("➤ Choose option (0-1): ");

                String input = sc.nextLine().trim();
                if (input.matches("[01]")) {
                    return Integer.parseInt(input);
                }
                System.out.println("❌ Invalid input! Please enter 0 or 1.");
            } catch (Exception e) {
                System.err.println("Error reading input: " + e.getMessage());
                scanner = new Scanner(System.in);
            }
        }
    }

    public static int selectModel() {
        Scanner sc = getScanner();
        while (true) {
            try {
                System.out.println("\n┌─────────────────────────────────┐");
                System.out.println("│       SELECT MODEL             │");
                System.out.println("├─────────────────────────────────┤");
                System.out.println("│  1) Tiny (75 MB) - Fastest     │");
                System.out.println("│  2) Base (150 MB) - Balanced   │");
                System.out.println("│  3) Small (500 MB) - Good      │");
                System.out.println("│  4) Medium (1.5 GB) - Accurate │");
                System.out.println("│  5) Large (2.9 GB) - Best      │");
                System.out.println("│  0) Back                       │");
                System.out.println("└─────────────────────────────────┘");
                System.out.print("➤ Choose model (0-5): ");

                String input = sc.nextLine().trim();
                if (input.matches("[0-5]")) {
                    return Integer.parseInt(input);
                }
                System.out.println("❌ Invalid input! Please enter 0-5.");
            } catch (Exception e) {
                System.err.println("Error reading input: " + e.getMessage());
                scanner = new Scanner(System.in);
            }
        }
    }

    public static int handleModelDownload(String modelName, String modelSize, boolean exists) {
        Scanner sc = getScanner();
        while (true) {
            try {
                System.out.println("\n┌─────────────────────────────────┐");
                System.out.println("│       MODEL STATUS             │");
                System.out.println("├─────────────────────────────────┤");
                System.out.printf("│  Selected: %s (%s)      │\n",
                        modelName.toUpperCase(), modelSize);
                System.out.println("├─────────────────────────────────┤");

                if (exists) {
                    System.out.println("│  ✓ Model already exists!       │");
                    System.out.println("│  1) Continue                   │");
                } else {
                    System.out.println("│  ✗ Model not found!            │");
                    System.out.println("│  1) Download Model             │");
                    System.out.println("│     (≈ " + modelSize + ")          │");
                }
                System.out.println("│  0) Back                       │");
                System.out.println("└─────────────────────────────────┘");
                System.out.print("➤ Choose option (0-1): ");

                String input = sc.nextLine().trim();
                if (input.matches("[01]")) {
                    return Integer.parseInt(input);
                }
                System.out.println("❌ Invalid input! Please enter 0 or 1.");
            } catch (Exception e) {
                System.err.println("Error reading input: " + e.getMessage());
                scanner = new Scanner(System.in);
            }
        }
    }

    public static int choosePreference() {
        Scanner sc = getScanner();
        while (true) {
            try {
                System.out.println("\n┌─────────────────────────────────┐");
                System.out.println("│       LINE PREFERENCE          │");
                System.out.println("├─────────────────────────────────┤");
                System.out.println("│  1) Words                      │");
                System.out.println("│  2) Letters                    │");
                System.out.println("│  0) Back                       │");
                System.out.println("└─────────────────────────────────┘");
                System.out.print("➤ Choose preference (0-2): ");

                String input = sc.nextLine().trim();
                if (input.matches("[0-2]")) {
                    return Integer.parseInt(input);
                }
                System.out.println("❌ Invalid input! Please enter 0, 1, or 2.");
            } catch (Exception e) {
                System.err.println("Error reading input: " + e.getMessage());
                scanner = new Scanner(System.in);
            }
        }
    }

    public static int chooseSubtitleMode() {
        Scanner sc = getScanner();
        while (true) {
            try {
                System.out.println("\n┌─────────────────────────────────────────┐");
                System.out.println("│         SUBTITLE MODE                   │");
                System.out.println("├─────────────────────────────────────────┤");
                System.out.println("│  1) Normal                              │");
                System.out.println("│     (Generate in original language)     │");
                System.out.println("│                                         │");
                System.out.println("│  2) Translation                         │");
                System.out.println("│     (Translate subtitle to English)     │");
                System.out.println("│                                         │");
                System.out.println("│  3) Transliteration                    │");
                System.out.println("│     (Convert Japanese/Hindi to English)│");
                System.out.println("│     ⚠️  Works only for Japanese/Hindi  │");
                System.out.println("│                                         │");
                System.out.println("│  0) Back                                │");
                System.out.println("└─────────────────────────────────────────┘");
                System.out.print("➤ Choose mode (0-3): ");

                String input = sc.nextLine().trim();
                if (input.matches("[0-3]")) {
                    int choice = Integer.parseInt(input);
                    if (choice == 3) {
                        System.out.println("\n⚠️  Note: Transliteration works best for:");
                        System.out.println("   • Japanese (Romaji conversion)");
                        System.out.println("   • Hindi (Romanized Hindi)");
                        System.out.println("   Press Enter to continue...");
                        sc.nextLine();
                    }
                    return choice;
                }
                System.out.println("❌ Invalid input! Please enter 0, 1, 2, or 3.");
            } catch (Exception e) {
                System.err.println("Error reading input: " + e.getMessage());
                scanner = new Scanner(System.in);
            }
        }
    }

    public static int getNumberPerLine(int preferenceChoice) {
        Scanner sc = getScanner();
        String type = preferenceChoice == 1 ? "words" : "letters";

        while (true) {
            try {
                System.out.printf("\n┌─────────────────────────────────┐\n");
                System.out.printf("│  How many %s per line?     │\n", type);
                System.out.println("├─────────────────────────────────┤");
                System.out.println("│  Range: 1-30                   │");
                System.out.println("│  0) Back                       │");
                System.out.println("└─────────────────────────────────┘");
                System.out.printf("➤ Enter number (0-30): ");

                String input = sc.nextLine().trim();
                if (input.matches("0|([1-9]|[1-2][0-9]|30)")) {
                    return Integer.parseInt(input);
                }
                System.out.println("❌ Invalid input! Please enter 0-30.");
            } catch (Exception e) {
                System.err.println("Error reading input: " + e.getMessage());
                scanner = new Scanner(System.in);
            }
        }
    }

    public static boolean confirmGeneration(CaptionConfig config) {
        Scanner sc = getScanner();
        while (true) {
            try {
                System.out.println("\n╔═══════════════════════════════════════════╗");
                System.out.println("║         CONFIRM GENERATION                ║");
                System.out.println("╠═══════════════════════════════════════════╣");

                // Print config with formatting
                String[] lines = config.toString().split("\n");
                for (String line : lines) {
                    if (line.length() > 45) {
                        // Wrap long lines
                        while (line.length() > 45) {
                            String part = line.substring(0, 45);
                            System.out.printf("║ %-45s ║\n", part);
                            line = line.substring(45);
                        }
                        System.out.printf("║ %-45s ║\n", line);
                    } else {
                        System.out.printf("║ %-45s ║\n", line);
                    }
                }

                System.out.println("╠═══════════════════════════════════════════╣");
                System.out.println("║  1) Continue                             ║");
                System.out.println("║  0) Back                                 ║");
                System.out.println("╚═══════════════════════════════════════════╝");
                System.out.print("➤ Are you sure? (0-1): ");

                String input = sc.nextLine().trim();
                if (input.matches("[01]")) {
                    return input.equals("1");
                }
                System.out.println("❌ Invalid input! Please enter 0 or 1.");
            } catch (Exception e) {
                System.err.println("Error reading input: " + e.getMessage());
                scanner = new Scanner(System.in);
            }
        }
    }

    public static int handleNextVideo() {
        Scanner sc = getScanner();
        while (true) {
            try {
                System.out.println("\n┌─────────────────────────────────┐");
                System.out.println("│         WHAT'S NEXT?           │");
                System.out.println("├─────────────────────────────────┤");
                System.out.println("│  1) Quit App                   │");
                System.out.println("│  0) Next Video                 │");
                System.out.println("└─────────────────────────────────┘");
                System.out.print("➤ Choose option (0-1): ");

                String input = sc.nextLine().trim();
                if (input.matches("[01]")) {
                    return Integer.parseInt(input);
                }
                System.out.println("❌ Invalid input! Please enter 0 or 1.");
            } catch (Exception e) {
                System.err.println("Error reading input: " + e.getMessage());
                scanner = new Scanner(System.in);
            }
        }
    }
}